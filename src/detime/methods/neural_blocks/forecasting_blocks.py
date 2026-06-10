from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from ...core import DecompResult
from ...registry import MethodRegistry


def _normalize_moving_avg_window(raw_value: Any, length: int) -> int:
    try:
        window = int(round(float(raw_value)))
    except (TypeError, ValueError):
        window = 25
    window = max(1, window)
    if window % 2 == 0:
        window += 1
    if length <= 1:
        return 1
    max_window = length if length % 2 == 1 else length - 1
    max_window = max(1, max_window)
    return min(window, max_window)


def _resolve_window_and_source(y: np.ndarray, cfg: Dict[str, Any]) -> Tuple[int, str]:
    length = int(np.asarray(y).reshape(-1).size)
    for key in ("moving_avg", "window"):
        if cfg.get(key) is not None:
            return _normalize_moving_avg_window(cfg.get(key), length), key
    for key in ("primary_period", "period", "season_period"):
        if cfg.get(key) is not None:
            return _normalize_moving_avg_window(cfg.get(key), length), key
    return _normalize_moving_avg_window(25, length), "source_default"


def _moving_average_block(y: np.ndarray, window: int) -> np.ndarray:
    arr = np.asarray(y, dtype=float).reshape(-1)
    if arr.size == 0:
        return arr.copy()
    if window <= 1:
        return arr.copy()
    pad = (window - 1) // 2
    padded = np.pad(arr, (pad, pad), mode="edge")
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(padded, kernel, mode="valid")


def _forecasting_block_decompose(y: np.ndarray, params: Dict[str, Any], source_model: str) -> DecompResult:
    cfg = dict(params or {})
    arr = np.asarray(y, dtype=float).reshape(-1)
    window, source = _resolve_window_and_source(arr, cfg)
    trend = _moving_average_block(arr, window)
    season = arr - trend
    residual = arr - trend - season
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components={"moving_mean": trend.copy()},
        meta={
            "method": source_model.upper(),
            "source_model": source_model,
            "block_family": "forecasting_moving_average_decomposition",
            "moving_avg": int(window),
            "window_source": source,
            "derived_residual": True,
        },
    )


@MethodRegistry.register("AUTOFORMER_BLOCK")
def autoformer_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    return _forecasting_block_decompose(y, params, source_model="autoformer_block")


@MethodRegistry.register("DLINEAR_BLOCK")
def dlinear_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    return _forecasting_block_decompose(y, params, source_model="dlinear_block")


@MethodRegistry.register("MOVING_AVERAGE_DECOMPOSITION_BLOCK")
def moving_average_decomposition_block(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    return _forecasting_block_decompose(y, params, source_model="moving_average_decomposition_block")
