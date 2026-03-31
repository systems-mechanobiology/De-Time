import numpy as np
from importlib import import_module
from time import perf_counter
from typing import Any, Dict

from .._native import invoke_native
from ..backends import finalize_result, resolve_backend, result_from_native_payload, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry

def _load_python_backend():
    try:
        module = import_module("synthetic_ts_bench.dr_ts_reg")
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise ImportError(
            "synthetic_ts_bench is required for DR_TS_REG decomposition."
        ) from exc
    return module.dr_ts_reg_decompose


def _estimate_dominant_period(y: np.ndarray, max_period: int = 128) -> int:
    y_centered = np.asarray(y, dtype=float).ravel() - float(np.mean(y))
    n = y_centered.size
    if n < 4:
        return max(1, n // 2)
    spectrum = np.abs(np.fft.rfft(y_centered))
    freqs = np.fft.rfftfreq(n)
    if spectrum.size < 2:
        return max(1, n // 4)
    spectrum[0] = 0.0
    peak_idx = int(np.argmax(spectrum))
    if peak_idx == 0 or freqs[peak_idx] < 1e-10:
        return max(1, min(n // 4, max_period))
    period = int(round(1.0 / freqs[peak_idx]))
    return max(2, min(period, max_period, max(2, n // 2)))


def _resolve_period(cfg: Dict[str, Any], length: int) -> int:
    period = cfg.get("period", cfg.get("primary_period"))
    if period not in (None, 0):
        return max(1, min(int(period), length - 1))
    max_search = int(cfg.get("max_period_search", 128))
    return _estimate_dominant_period(np.asarray(cfg["_signal"], dtype=float), max_period=max_search)


@MethodRegistry.register("DR_TS_REG")
def dr_ts_reg_wrapper(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    y_arr = np.asarray(y, dtype=float).ravel()
    cfg["_signal"] = y_arr
    period = _resolve_period(cfg, len(y_arr))
    cfg.pop("_signal", None)
    backend = resolve_backend("DR_TS_REG", runtime, native_methods=("dr_ts_reg_decompose",))

    if backend == "native":
        payload = invoke_native(
            "dr_ts_reg_decompose",
            y_arr,
            period=period,
            lambda_t=float(cfg.get("lambda_T", 5.0)),
            lambda_s=float(cfg.get("lambda_S", 50.0)),
            lambda_r=float(cfg.get("lambda_R", 0.1)),
            max_iter=int(cfg.get("max_iter", 500)),
            tol=float(cfg.get("tol", 1e-8)),
        )
        return finalize_result(
            result_from_native_payload(payload, method="DR_TS_REG"),
            method="DR_TS_REG",
            runtime=runtime,
            backend_used="native",
            started_at=started_at,
        )

    dr_ts_reg_decompose = _load_python_backend()
    cfg["period"] = period
    meta = {"primary_period": period}
    res = dr_ts_reg_decompose(
        y_arr,
        config=cfg,
        fs=float(cfg.get("fs", 1.0)),
        meta=meta,
    )
    meta_out = dict(getattr(res, "extra", {}) or {})
    meta_out.setdefault("method", "DR_TS_REG")
    return finalize_result(
        DecompResult(
            trend=np.asarray(res.trend, dtype=float),
            season=np.asarray(res.season, dtype=float),
            residual=np.asarray(res.residual, dtype=float),
            meta=meta_out,
        ),
        method="DR_TS_REG",
        runtime=runtime,
        backend_used="python",
        started_at=started_at,
    )
