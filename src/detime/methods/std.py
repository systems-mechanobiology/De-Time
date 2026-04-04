from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, Optional

import numpy as np

from .._native import invoke_native
from ..backends import finalize_result, resolve_backend, result_from_native_payload, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry


def _infer_period(y: np.ndarray, max_period_search: int = 128) -> int:
    y_arr = np.asarray(y, dtype=float).ravel()
    n = y_arr.size
    if n < 4:
        return max(1, n)

    centered = y_arr - float(np.mean(y_arr))
    spectrum = np.abs(np.fft.rfft(centered))
    freqs = np.fft.rfftfreq(n)
    if spectrum.size <= 1:
        return max(2, min(max_period_search, max(2, n // 4)))

    spectrum[0] = 0.0
    peak_idx = int(np.argmax(spectrum))
    if peak_idx <= 0 or freqs[peak_idx] <= 1e-12:
        return max(2, min(max_period_search, max(2, n // 4)))

    period = int(round(1.0 / freqs[peak_idx]))
    return max(2, min(period, max_period_search, n))


def compute_std_components(
    y: np.ndarray,
    period: Optional[int] = None,
    *,
    variant: str = "STD",
    max_period_search: int = 128,
    eps: float = 1e-12,
) -> Dict[str, Any]:
    """
    Compute Seasonal-Trend-Dispersion decomposition.

    This is a practical implementation of the method proposed in
    "STD: A Seasonal-Trend-Dispersion Decomposition of Time Series"
    (Dudek, 2022). The implementation supports arbitrary series lengths by
    handling the final partial seasonal block directly.
    """

    y_arr = np.asarray(y, dtype=float).ravel()
    n = y_arr.size
    if n == 0:
        zeros = np.zeros(0, dtype=float)
        return {
            "trend": zeros,
            "season": zeros,
            "residual": zeros,
            "dispersion": zeros,
            "seasonal_shape": zeros,
            "period": 0,
            "variant": variant.upper(),
            "n_cycles": 0,
            "incomplete_cycle": False,
        }

    variant_norm = str(variant).upper()
    resolved_period = int(period) if period not in (None, 0) else _infer_period(y_arr, max_period_search=max_period_search)
    resolved_period = max(1, min(resolved_period, n))

    trend = np.zeros(n, dtype=float)
    dispersion = np.zeros(n, dtype=float)
    seasonal_shape = np.zeros(n, dtype=float)
    season = np.zeros(n, dtype=float)

    block_shapes = []
    block_slices = []
    for start in range(0, n, resolved_period):
        stop = min(start + resolved_period, n)
        sl = slice(start, stop)
        block = y_arr[sl]
        block_mean = float(np.mean(block))
        centered = block - block_mean
        block_diversity = float(np.linalg.norm(centered))
        if block_diversity <= eps:
            shape = np.zeros_like(block)
            block_diversity = 0.0
        else:
            shape = centered / block_diversity

        trend[sl] = block_mean
        dispersion[sl] = block_diversity
        seasonal_shape[sl] = shape
        season[sl] = block_diversity * shape

        block_shapes.append(shape)
        block_slices.append(sl)

    average_seasonal_shape = None
    if variant_norm == "STDR":
        average_seasonal_shape = np.zeros(resolved_period, dtype=float)
        counts = np.zeros(resolved_period, dtype=float)
        for shape in block_shapes:
            average_seasonal_shape[: shape.size] += shape
            counts[: shape.size] += 1.0
        valid = counts > 0
        average_seasonal_shape[valid] /= counts[valid]

        season = np.zeros_like(y_arr)
        seasonal_shape = np.zeros_like(y_arr)
        for sl in block_slices:
            avg_shape = average_seasonal_shape[: sl.stop - sl.start]
            seasonal_shape[sl] = avg_shape
            season[sl] = dispersion[sl] * avg_shape

    residual = y_arr - trend - season
    return {
        "trend": trend,
        "season": season,
        "residual": residual,
        "dispersion": dispersion,
        "seasonal_shape": seasonal_shape,
        "average_seasonal_shape": average_seasonal_shape,
        "period": resolved_period,
        "variant": variant_norm,
        "n_cycles": len(block_slices),
        "incomplete_cycle": bool(n % resolved_period),
    }


def _wrap_std_result(result: Dict[str, Any]) -> DecompResult:
    components = {
        "dispersion": np.asarray(result["dispersion"], dtype=float),
        "seasonal_shape": np.asarray(result["seasonal_shape"], dtype=float),
    }
    if result.get("average_seasonal_shape") is not None:
        components["average_seasonal_shape"] = np.asarray(result["average_seasonal_shape"], dtype=float)

    return DecompResult(
        trend=np.asarray(result["trend"], dtype=float),
        season=np.asarray(result["season"], dtype=float),
        residual=np.asarray(result["residual"], dtype=float),
        components=components,
        meta={
            "method": result["variant"],
            "period": int(result["period"]),
            "n_cycles": int(result["n_cycles"]),
            "incomplete_cycle": bool(result["incomplete_cycle"]),
        },
    )


def _single_channel_std(
    y: np.ndarray,
    *,
    cfg: Dict[str, Any],
    variant: str,
    backend: str,
) -> DecompResult:
    period = cfg.get("period", cfg.get("primary_period"))
    max_period_search = int(cfg.get("max_period_search", 128))
    eps = float(cfg.get("eps", 1e-12))

    if backend == "native":
        payload = invoke_native(
            "std_decompose",
            np.asarray(y, dtype=float),
            period=period,
            variant=variant,
            max_period_search=max_period_search,
            eps=eps,
        )
        return result_from_native_payload(payload, method=variant)

    result = compute_std_components(
        y,
        period=period,
        variant=variant,
        max_period_search=max_period_search,
        eps=eps,
    )
    return _wrap_std_result(result)


def _stack_channelwise_results(results: list[DecompResult], variant: str) -> DecompResult:
    trend = np.column_stack([np.asarray(result.trend, dtype=float) for result in results])
    season = np.column_stack([np.asarray(result.season, dtype=float) for result in results])
    residual = np.column_stack([np.asarray(result.residual, dtype=float) for result in results])

    components: Dict[str, np.ndarray] = {}
    for key in ("dispersion", "seasonal_shape"):
        components[key] = np.column_stack(
            [np.asarray(result.components[key], dtype=float) for result in results]
        )

    avg_shapes = [
        np.asarray(result.components["average_seasonal_shape"], dtype=float)
        for result in results
        if "average_seasonal_shape" in result.components
    ]
    if avg_shapes:
        max_len = max(shape.size for shape in avg_shapes)
        avg_matrix = np.full((max_len, len(results)), np.nan, dtype=float)
        for idx, result in enumerate(results):
            if "average_seasonal_shape" not in result.components:
                continue
            shape = np.asarray(result.components["average_seasonal_shape"], dtype=float)
            avg_matrix[: shape.size, idx] = shape
        components["average_seasonal_shape"] = avg_matrix

    periods = [
        int(result.meta.get("period", 0))
        for result in results
    ]
    meta: Dict[str, Any] = {
        "method": variant,
        "periods": periods,
        "n_channels": len(results),
        "decomposition_mode": "channelwise",
    }
    if periods and all(period == periods[0] for period in periods):
        meta["period"] = periods[0]

    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components=components,
        meta=meta,
    )


def _std_dispatch(y: np.ndarray, params: Dict[str, Any], *, variant: str) -> DecompResult:
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    backend = resolve_backend(variant, runtime, native_methods=("std_decompose",))

    y_arr = np.asarray(y, dtype=float)
    if y_arr.ndim == 1:
        result = _single_channel_std(y_arr, cfg=cfg, variant=variant, backend=backend)
    elif y_arr.ndim == 2:
        results = [
            _single_channel_std(y_arr[:, idx], cfg=cfg, variant=variant, backend=backend)
            for idx in range(y_arr.shape[1])
        ]
        result = _stack_channelwise_results(results, variant)
    else:
        raise ValueError(f"{variant} expects a 1D series or a 2D (T, C) array.")

    return finalize_result(
        result,
        method=variant,
        runtime=runtime,
        backend_used=backend,
        started_at=started_at,
    )


@MethodRegistry.register("STD", input_mode="channelwise")
def std_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    return _std_dispatch(y, params, variant="STD")


@MethodRegistry.register("STDR", input_mode="channelwise")
def stdr_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    return _std_dispatch(y, params, variant="STDR")
