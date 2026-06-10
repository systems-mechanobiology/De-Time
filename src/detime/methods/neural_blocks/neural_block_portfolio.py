from __future__ import annotations

from typing import Any, Dict, Iterable, List

import numpy as np

from ...core import DecompResult
from ...registry import MethodRegistry

try:
    import pywt
    _HAS_PYWT = all(hasattr(pywt, attr) for attr in ("Wavelet", "dwt_max_level", "wavedec", "waverec"))
except Exception:  # pragma: no cover - optional dependency
    pywt = None
    _HAS_PYWT = False


def _as_1d_float(y: np.ndarray) -> np.ndarray:
    return np.asarray(y, dtype=float).reshape(-1)


def _clip_unit(raw: Any, fallback: float) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = float(fallback)
    return float(np.clip(value, 1e-4, 0.9999))


def _odd_window(raw: Any, fallback: int, length: int) -> int:
    try:
        window = int(round(float(raw)))
    except (TypeError, ValueError):
        window = int(fallback)
    window = max(1, window)
    if window % 2 == 0:
        window += 1
    if length <= 1:
        return 1
    if window >= length:
        window = length if length % 2 == 1 else length - 1
    return max(1, window)


def _resolve_primary_period(cfg: Dict[str, Any], length: int) -> int:
    for key in ("primary_period", "period", "season_period"):
        if cfg.get(key) is not None:
            try:
                period = int(round(float(cfg[key])))
                if period >= 2:
                    return min(period, max(2, length // 2))
            except (TypeError, ValueError):
                continue
    return max(2, min(24, max(2, length // 8)))


def _moving_average(y: np.ndarray, window: int) -> np.ndarray:
    arr = _as_1d_float(y)
    if arr.size == 0 or window <= 1:
        return arr.copy()
    pad = (window - 1) // 2
    padded = np.pad(arr, (pad, pad), mode="edge")
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(padded, kernel, mode="valid")


def _fit_window(n: int, fit_scope: str, train_fraction: float) -> int:
    if n <= 1:
        return max(0, n)
    if fit_scope == "full":
        return n
    return max(2, min(n, int(round(n * float(train_fraction)))))


def _extend_with_last(values: np.ndarray, n: int) -> np.ndarray:
    arr = _as_1d_float(values)
    if arr.size >= n:
        return arr[:n].copy()
    if arr.size == 0:
        return np.zeros(n, dtype=float)
    out = np.empty(n, dtype=float)
    out[: arr.size] = arr
    out[arr.size :] = arr[-1]
    return out


def _moving_average_trend(y: np.ndarray, window: int, *, fit_scope: str = "full", train_fraction: float = 0.6) -> np.ndarray:
    arr = _as_1d_float(y)
    fit_end = _fit_window(arr.size, fit_scope, train_fraction)
    trend_prefix = _moving_average(arr[:fit_end], window)
    if fit_scope == "full" or fit_end >= arr.size:
        return trend_prefix
    return _extend_with_last(trend_prefix, arr.size)


def _ema_trend(y: np.ndarray, alpha: float, *, fit_scope: str = "full", train_fraction: float = 0.6) -> np.ndarray:
    arr = _as_1d_float(y)
    if arr.size == 0:
        return arr.copy()
    alpha = _clip_unit(alpha, 0.3)
    fit_end = _fit_window(arr.size, fit_scope, train_fraction)
    out = np.empty_like(arr)
    out[0] = arr[0]
    for idx in range(1, fit_end):
        out[idx] = alpha * arr[idx] + (1.0 - alpha) * out[idx - 1]
    if fit_end < arr.size:
        for idx in range(fit_end, arr.size):
            out[idx] = out[idx - 1]
    return out


def _holt_trend(y: np.ndarray, alpha: float, beta: float, *, fit_scope: str = "full", train_fraction: float = 0.6) -> np.ndarray:
    arr = _as_1d_float(y)
    if arr.size <= 1:
        return arr.copy()
    alpha = _clip_unit(alpha, 0.4)
    beta = _clip_unit(beta, 0.2)
    fit_end = _fit_window(arr.size, fit_scope, train_fraction)
    trend = np.empty_like(arr)
    level = arr[0]
    slope = arr[1] - arr[0]
    trend[0] = level
    for idx in range(1, fit_end):
        level_new = alpha * arr[idx] + (1.0 - alpha) * (level + slope)
        slope = beta * (level_new - level) + (1.0 - beta) * slope
        level = level_new
        trend[idx] = level
    if fit_end < arr.size:
        for idx in range(fit_end, arr.size):
            level = level + slope
            trend[idx] = level
    return trend


def _seasonal_template(
    y: np.ndarray,
    period: int,
    *,
    fit_scope: str = "prefix",
    train_fraction: float = 0.6,
) -> np.ndarray:
    arr = _as_1d_float(y)
    n = arr.size
    period = max(2, min(int(period), max(2, n)))
    if fit_scope == "full":
        fit_end = n
    else:
        fit_end = max(period, min(n, int(round(n * float(train_fraction)))))
    template = np.zeros(period, dtype=float)
    counts = np.zeros(period, dtype=float)
    for idx in range(fit_end):
        bucket = idx % period
        template[bucket] += arr[idx]
        counts[bucket] += 1.0
    counts[counts == 0.0] = 1.0
    template = template / counts
    return np.take(template, np.arange(n) % period)


def _harmonic_design(n: int, period: int, harmonics: int) -> np.ndarray:
    t = np.arange(n, dtype=float)
    cols: List[np.ndarray] = []
    for h in range(1, max(1, int(harmonics)) + 1):
        angle = 2.0 * np.pi * h * t / float(period)
        cols.append(np.cos(angle))
        cols.append(np.sin(angle))
    return np.stack(cols, axis=1)


def _fourier_season(y: np.ndarray, period: int, harmonics: int, *, fit_scope: str = "full", train_fraction: float = 0.6) -> np.ndarray:
    arr = _as_1d_float(y)
    fit_end = _fit_window(arr.size, fit_scope, train_fraction)
    X_fit = _harmonic_design(fit_end, period, harmonics)
    coef, *_ = np.linalg.lstsq(X_fit, arr[:fit_end], rcond=None)
    X_full = _harmonic_design(arr.size, period, harmonics)
    return X_full @ coef


def _frequency_mixture_season(
    y: np.ndarray,
    primary_period: int,
    num_bands: int,
    expert_width: int,
    *,
    fit_scope: str = "full",
    train_fraction: float = 0.6,
) -> np.ndarray:
    arr = _as_1d_float(y)
    periods = _dominant_periods_from_fft(
        arr,
        primary_period,
        top_k=max(1, int(num_bands)),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    harmonics = max(1, int(round(float(expert_width) / 64.0)))
    pieces = [
        _fourier_season(arr, period, harmonics, fit_scope=fit_scope, train_fraction=train_fraction)
        for period in periods
    ]
    if not pieces:
        return np.zeros_like(arr)
    return np.mean(pieces, axis=0)


def _dominant_periods_from_fft(
    y: np.ndarray,
    primary_period: int,
    top_k: int,
    *,
    fit_scope: str = "full",
    train_fraction: float = 0.6,
) -> List[int]:
    arr = _as_1d_float(y)
    fit_end = _fit_window(arr.size, fit_scope, train_fraction)
    arr = arr[:fit_end]
    arr = arr - np.mean(arr)
    spec = np.abs(np.fft.rfft(arr))
    spec[0] = 0.0
    order = np.argsort(spec)[::-1]
    periods: List[int] = []
    for idx in order:
        if idx <= 0:
            continue
        period = int(round(arr.size / float(idx)))
        if period >= 2 and period not in periods:
            periods.append(period)
        if len(periods) >= max(1, int(top_k)):
            break
    if not periods:
        periods = [primary_period]
    return periods


def _wavelet_trend_season(
    y: np.ndarray,
    *,
    wavelet_name: str,
    level: int,
    season_levels: Iterable[int],
) -> tuple[np.ndarray, np.ndarray]:
    arr = _as_1d_float(y)
    if not _HAS_PYWT:
        raise RuntimeError(
            "Wavelet-based neural blocks require PyWavelets. "
            "Install de-time with its default dependencies before using this method."
        )

    wavelet = pywt.Wavelet(wavelet_name)
    max_level = pywt.dwt_max_level(arr.size, wavelet.dec_len)
    level = max(1, min(int(level), max_level))
    coeffs = pywt.wavedec(arr, wavelet, level=level)

    def _reconstruct(keep: set[int]) -> np.ndarray:
        rec_coeffs: List[np.ndarray] = []
        for idx, coeff in enumerate(coeffs):
            rec_coeffs.append(np.copy(coeff) if idx in keep else np.zeros_like(coeff))
        recon = pywt.waverec(rec_coeffs, wavelet_name)
        if recon.shape[0] > arr.size:
            recon = recon[: arr.size]
        elif recon.shape[0] < arr.size:
            recon = np.pad(recon, (0, arr.size - recon.shape[0]), mode="edge")
        return recon

    trend = _reconstruct({0})
    season = _reconstruct(set(int(x) for x in season_levels if 0 < int(x) < len(coeffs)))
    return trend, season


def _finalize_result(y: np.ndarray, trend: np.ndarray, season: np.ndarray, meta: Dict[str, Any]) -> DecompResult:
    arr = _as_1d_float(y)
    trend = _as_1d_float(trend)
    season = _as_1d_float(season)
    residual = arr - trend - season
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components={
            "trend": trend.copy(),
            "season": season.copy(),
        },
        meta={**meta, "derived_residual": True},
    )


@MethodRegistry.register("INPARFORMER_BLOCK")
def inparformer_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "prefix")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    trend = _moving_average_trend(
        arr,
        _odd_window(cfg.get("trend_window", 2 * period + 1), 2 * period + 1, arr.size),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    season = _seasonal_template(arr - trend, period, fit_scope=fit_scope, train_fraction=train_fraction)
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "INPARFORMER_BLOCK",
            "paper_family": "seasonal_trend_transformer_backbone",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(period),
            "trend_window": int(_odd_window(cfg.get("trend_window", 2 * period + 1), 2 * period + 1, arr.size)),
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "moving_average_trend + periodic_template_season",
        },
    )


@MethodRegistry.register("DELELSTM_BLOCK")
def delelstm_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "prefix")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    trend = _holt_trend(
        arr,
        cfg.get("alpha", 0.4),
        cfg.get("beta", 0.2),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    season = _seasonal_template(arr - trend, period, fit_scope=fit_scope, train_fraction=train_fraction)
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "DELELSTM_BLOCK",
            "paper_family": "explainable_decomposition_lstm_module",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(period),
            "alpha": float(_clip_unit(cfg.get("alpha", 0.4), 0.4)),
            "beta": float(_clip_unit(cfg.get("beta", 0.2), 0.2)),
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "holt_trend + periodic_template_season",
        },
    )


@MethodRegistry.register("AMD_BLOCK")
def amd_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "prefix")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    raw_windows = cfg.get("multiscale_windows")
    if raw_windows is None:
        raw_windows = [max(3, period // 2), period, 2 * period + 1]
    windows = [_odd_window(raw_window, max(3, period // 2), arr.size) for raw_window in raw_windows]
    trend = np.mean(
        [
            _moving_average_trend(arr, window, fit_scope=fit_scope, train_fraction=train_fraction)
            for window in windows
        ],
        axis=0,
    )
    season = _seasonal_template(arr - trend, period, fit_scope=fit_scope, train_fraction=train_fraction)
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "AMD_BLOCK",
            "paper_family": "adaptive_multiscale_decomposition_backbone",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(period),
            "windows": [int(w) for w in windows],
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "multiscale_trend_average + periodic_template_season",
        },
    )


@MethodRegistry.register("PARSIMONY_BLOCK")
def parsimony_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "full")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    trend = _moving_average_trend(
        arr,
        _odd_window(cfg.get("trend_window", period), period, arr.size),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    season = _fourier_season(
        arr - trend,
        period,
        int(cfg.get("num_harmonics", 2)),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "PARSIMONY_BLOCK",
            "paper_family": "modern_forecasting_decomposition_branch",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(period),
            "num_harmonics": int(cfg.get("num_harmonics", 2)),
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "moving_average_trend + harmonic_projection_season",
        },
    )


@MethodRegistry.register("ST_MTM_BLOCK")
def stmtm_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "prefix")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    trend = _moving_average_trend(
        arr,
        _odd_window(cfg.get("trend_window", 2 * period + 1), 2 * period + 1, arr.size),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    season_raw = _seasonal_template(arr - trend, period, fit_scope=fit_scope, train_fraction=train_fraction)
    season = _moving_average(season_raw, _odd_window(cfg.get("season_smooth_window", max(3, period // 2)), max(3, period // 2), arr.size))
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "ST_MTM_BLOCK",
            "paper_family": "seasonal_trend_pretraining_module",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(period),
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "moving_average_trend + smoothed_periodic_template_season",
        },
    )


@MethodRegistry.register("WAVEFORM_BLOCK")
def waveform_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    trend, season = _wavelet_trend_season(
        arr,
        wavelet_name=str(cfg.get("wavelet", "db4")),
        level=int(cfg.get("level", 3)),
        season_levels=cfg.get("season_levels", [1, 2]),
    )
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "WAVEFORM_BLOCK",
            "paper_family": "wavelet_graph_backbone",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "wavelet": str(cfg.get("wavelet", "db4")),
            "level": int(cfg.get("level", 3)),
            "canonical_mapping": "wavelet_approximation_trend + detail_levels_season",
        },
    )


@MethodRegistry.register("WAVELETMIXER_BLOCK")
def waveletmixer_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    trend, season = _wavelet_trend_season(
        arr,
        wavelet_name=str(cfg.get("wavelet", "sym4")),
        level=int(cfg.get("level", 4)),
        season_levels=cfg.get("season_levels", [1, 2, 3]),
    )
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "WAVELETMIXER_BLOCK",
            "paper_family": "multiresolution_wavelet_mixer",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "wavelet": str(cfg.get("wavelet", "sym4")),
            "level": int(cfg.get("level", 4)),
            "canonical_mapping": "wavelet_coarse_trend + mixed_detail_season",
        },
    )


@MethodRegistry.register("TIMES2D_BLOCK")
def times2d_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    primary_period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "full")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    top_k = max(1, int(cfg.get("top_k_periods", 2)))
    periods = _dominant_periods_from_fft(arr, primary_period, top_k=top_k, fit_scope=fit_scope, train_fraction=train_fraction)
    trend = _moving_average_trend(
        arr,
        _odd_window(cfg.get("trend_window", 2 * primary_period + 1), 2 * primary_period + 1, arr.size),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    season = np.zeros_like(arr)
    for period in periods:
        season += _fourier_season(
            arr - trend,
            period,
            int(cfg.get("num_harmonics", 1)),
            fit_scope=fit_scope,
            train_fraction=train_fraction,
        )
    season = season / float(max(1, len(periods)))
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "TIMES2D_BLOCK",
            "paper_family": "multi_period_decomposition_block",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(primary_period),
            "periods_used": [int(p) for p in periods],
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "moving_average_trend + multi_period_harmonic_season",
        },
    )


@MethodRegistry.register("FREQMOE_BLOCK")
def freqmoe_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    primary_period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "full")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    trend_window = _odd_window(cfg.get("trend_window", 2 * primary_period + 1), 2 * primary_period + 1, arr.size)
    num_bands = max(1, int(cfg.get("num_bands", 4)))
    expert_width = max(8, int(cfg.get("expert_width", 64)))
    trend = _moving_average_trend(arr, trend_window, fit_scope=fit_scope, train_fraction=train_fraction)
    season = _frequency_mixture_season(
        arr - trend,
        primary_period,
        num_bands=num_bands,
        expert_width=expert_width,
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "FREQMOE_BLOCK",
            "paper_family": "frequency_mixture_of_experts_backbone",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(primary_period),
            "trend_window": int(trend_window),
            "num_bands": int(num_bands),
            "expert_width": int(expert_width),
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "moving_average_trend + multi_band_fourier_season",
        },
    )


@MethodRegistry.register("TIMEKAN_BLOCK")
def timekan_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    cfg = dict(params or {})
    arr = _as_1d_float(y)
    primary_period = _resolve_primary_period(cfg, arr.size)
    fit_scope = str(cfg.get("fit_scope", "prefix")).strip().lower()
    train_fraction = float(cfg.get("train_fraction", 0.6))
    trend_window = _odd_window(cfg.get("trend_window", primary_period), primary_period, arr.size)
    num_bands = max(1, int(cfg.get("num_bands", 2)))
    kan_width = max(8, int(cfg.get("kan_width", 32)))
    trend = _moving_average_trend(arr, trend_window, fit_scope=fit_scope, train_fraction=train_fraction)
    periods = _dominant_periods_from_fft(arr - trend, primary_period, top_k=num_bands, fit_scope=fit_scope, train_fraction=train_fraction)
    template_stack = [
        _seasonal_template(arr - trend, period, fit_scope=fit_scope, train_fraction=train_fraction)
        for period in periods
    ]
    template_season = np.mean(template_stack, axis=0) if template_stack else np.zeros_like(arr)
    harmonic_season = _fourier_season(
        arr - trend,
        primary_period,
        max(1, kan_width // 32),
        fit_scope=fit_scope,
        train_fraction=train_fraction,
    )
    blend = float(np.clip(0.35 + 0.1 * min(num_bands, 4), 0.25, 0.75))
    season = blend * template_season + (1.0 - blend) * harmonic_season
    return _finalize_result(
        arr,
        trend,
        season,
        {
            "method": "TIMEKAN_BLOCK",
            "paper_family": "frequency_decomposition_learning_backbone",
            "candidate_status": "first_pass_paper_inspired_scaffold",
            "primary_period": int(primary_period),
            "trend_window": int(trend_window),
            "num_bands": int(num_bands),
            "kan_width": int(kan_width),
            "fit_scope_requested": fit_scope,
            "fit_scope_applied": fit_scope,
            "train_fraction": train_fraction,
            "canonical_mapping": "moving_average_trend + template_and_harmonic_season",
        },
    )
