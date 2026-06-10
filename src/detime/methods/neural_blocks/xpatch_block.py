from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from ...core import DecompResult
from ...registry import MethodRegistry


def _as_float_01(value: Any, default: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        out = float(default)
    if not np.isfinite(out):
        out = float(default)
    return float(np.clip(out, 0.0, 1.0))


def _normalize_window(raw_value: Any, default: int, length: int) -> int:
    try:
        window = int(round(float(raw_value)))
    except (TypeError, ValueError):
        window = int(default)
    window = max(1, window)
    if window % 2 == 0:
        window += 1
    if length <= 1:
        return 1
    max_window = length if length % 2 == 1 else length - 1
    return max(1, min(window, max_window))


def _moving_average(series: np.ndarray, window: int) -> np.ndarray:
    arr = np.asarray(series, dtype=float).reshape(-1)
    if arr.size == 0 or window <= 1:
        return arr.copy()
    pad = (window - 1) // 2
    padded = np.pad(arr, (pad, pad), mode="edge")
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(padded, kernel, mode="valid")


def _ema(series: np.ndarray, alpha: float) -> np.ndarray:
    arr = np.asarray(series, dtype=float).reshape(-1)
    if arr.size == 0:
        return arr.copy()
    alpha = _as_float_01(alpha, 0.3)
    trend = np.empty_like(arr, dtype=float)
    trend[0] = arr[0]
    for idx in range(1, arr.size):
        trend[idx] = alpha * arr[idx] + (1.0 - alpha) * trend[idx - 1]
    return trend


def _dema(series: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    arr = np.asarray(series, dtype=float).reshape(-1)
    if arr.size == 0:
        return arr.copy()
    alpha = _as_float_01(alpha, 0.3)
    beta = _as_float_01(beta, 0.3)

    level = np.empty_like(arr, dtype=float)
    slope = np.empty_like(arr, dtype=float)

    level[0] = arr[0]
    slope[0] = 0.0
    for idx in range(1, arr.size):
        prev_level = level[idx - 1]
        prev_slope = slope[idx - 1]
        level[idx] = alpha * arr[idx] + (1.0 - alpha) * (prev_level + prev_slope)
        slope[idx] = beta * (level[idx] - prev_level) + (1.0 - beta) * prev_slope

    return level


def _xpatch_decompose(y: np.ndarray, params: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, str, Dict[str, float]]:
    arr = np.asarray(y, dtype=float).reshape(-1)
    if arr.size == 0:
        empty = arr.copy()
        return empty, empty, "ema", {"alpha": 0.3, "beta": 0.3}

    cfg = dict(params or {})
    ma_type = str(cfg.get("ma_type", "ema")).strip().lower()
    trend_window = cfg.get("trend_window")
    season_smooth = cfg.get("season_smooth")
    trend_window_resolved = None
    season_smooth_resolved = None
    if trend_window is not None:
        trend_window_resolved = _normalize_window(trend_window, 25, arr.size)
    if season_smooth is not None:
        season_smooth_resolved = _normalize_window(season_smooth, 5, arr.size)

    default_alpha = 0.3 if trend_window_resolved is None else float(np.clip(2.0 / (trend_window_resolved + 1.0), 1e-4, 0.9999))
    default_beta = 0.3 if season_smooth_resolved is None else float(np.clip(2.0 / (season_smooth_resolved + 1.0), 1e-4, 0.9999))
    alpha = _as_float_01(cfg.get("alpha", default_alpha), default_alpha)
    beta = _as_float_01(cfg.get("beta", default_beta), default_beta)

    if ma_type == "dema":
        trend = _dema(arr, alpha=alpha, beta=beta)
    else:
        ma_type = "ema"
        trend = _ema(arr, alpha=alpha)

    season = arr - trend
    if season_smooth_resolved is not None:
        season = _moving_average(season, season_smooth_resolved)

    coeffs = {"alpha": alpha, "beta": beta}
    if trend_window_resolved is not None:
        coeffs["trend_window"] = float(trend_window_resolved)
    if season_smooth_resolved is not None:
        coeffs["season_smooth"] = float(season_smooth_resolved)
    return trend, season, ma_type, coeffs


@MethodRegistry.register("XPATCH_BLOCK")
def xpatch_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    trend, season, ma_type, coeffs = _xpatch_decompose(y, params)
    arr = np.asarray(y, dtype=float).reshape(-1)
    residual = arr - trend - season
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components={
            "trend": trend.copy(),
            "season": season.copy(),
        },
        meta={
            "method": "XPATCH_BLOCK",
            "block_family": "xpatch_exponential_seasonal_trend_decomposition",
            "ma_type": ma_type,
            "derived_residual": True,
            **coeffs,
        },
    )
