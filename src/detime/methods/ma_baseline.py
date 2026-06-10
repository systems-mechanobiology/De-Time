import numpy as np
from typing import Dict, Any
from time import perf_counter
from .._native import invoke_native
from ..backends import finalize_result, resolve_backend, result_from_native_payload, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry

def _moving_average(y: np.ndarray, window: int) -> np.ndarray:
    window = max(1, int(window))
    if window == 1 or len(y) == 0:
        return y.copy()
    kernel = np.ones(window) / window
    return np.convolve(y, kernel, mode="same")

def _estimate_seasonal_indices(detrended: np.ndarray, period: int) -> np.ndarray:
    period = max(1, int(period))
    season = np.zeros_like(detrended)
    for offset in range(period):
        idx = np.arange(offset, len(detrended), period)
        if idx.size == 0:
            continue
        mean_val = np.mean(detrended[idx])
        season[idx] = mean_val
    season -= np.mean(season)
    return season

@MethodRegistry.register("MA_BASELINE")
def ma_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """
    Moving-average baseline decomposition.
    """
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    y_arr = np.asarray(y, dtype=float).ravel()
    default_window = max(3, len(y_arr) // 20)
    trend_window = int(cfg.get("trend_window", default_window))
    if trend_window % 2 == 0:
        trend_window += 1

    backend = resolve_backend("MA_BASELINE", runtime, native_methods=("ma_baseline_decompose",))
    if backend == "native":
        payload = invoke_native(
            "ma_baseline_decompose",
            y_arr,
            trend_window=trend_window,
            season_period=cfg.get("season_period"),
        )
        return finalize_result(
            result_from_native_payload(payload, method="MA_BASELINE"),
            method="MA_BASELINE",
            runtime=runtime,
            backend_used="native",
            started_at=started_at,
        )
    
    trend = _moving_average(y_arr, trend_window)

    season_period = cfg.get("season_period")
    if season_period:
        season = _estimate_seasonal_indices(y_arr - trend, int(season_period))
    else:
        season = np.zeros_like(y_arr)
        
    residual = y_arr - trend - season
    
    result = DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        meta={"method": "MA_BASELINE", "params": cfg}
    )
    return finalize_result(
        result,
        method="MA_BASELINE",
        runtime=runtime,
        backend_used=backend,
        started_at=started_at,
    )
