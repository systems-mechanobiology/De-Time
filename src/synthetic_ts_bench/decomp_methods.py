"""Unified wrappers for time-series decomposition methods."""

from __future__ import annotations

from dataclasses import dataclass, field, fields as dataclass_fields
from typing import Any, Dict, List, Optional, TypedDict, Literal

import numpy as np

from decomp_methods.sota_methods import (
    decompose_ceemdan_components,
    decompose_mstl_components,
    decompose_robuststl_components,
    decompose_vmd_components,
)
from .gabor import GaborConfig, gabor_decompose
from .gabor_cluster import (
    GaborClusterConfig,
    GaborClusterModel,
    gabor_cluster_decompose,
    gabor_components_to_TS,
)
from .dr_ts_reg import dr_ts_reg_decompose
from .dr_ts_ae import dr_ts_ae_decompose
from .sl_lib import sl_lib_decompose
try:
    from PyEMD import EMD

    _HAS_PYEMD = True
except ImportError:  # pragma: no cover - optional dependency
    EMD = None
    _HAS_PYEMD = False

try:
    import pywt

    _HAS_PYWT = True
except ImportError:  # pragma: no cover - optional dependency
    pywt = None
    _HAS_PYWT = False


@dataclass
class DecompResult:
    """
    Unified container for time-series decomposition results.

    Attributes
    ----------
    trend : np.ndarray
        Estimated trend component, shape (T,).
    season : np.ndarray
        Estimated seasonal / cyclic component (can be multi-season sum), shape (T,).
    residual : np.ndarray
        Estimated residual component (y - trend - season), shape (T,).
    extra : Dict[str, Any]
        Method-specific extra information.
    """

    trend: np.ndarray
    season: np.ndarray
    residual: np.ndarray
    extra: Dict[str, Any] = field(default_factory=dict)


class DecompConfig(TypedDict, total=False):
    """
    Configuration for a decomposition method.

    Keys are method-dependent, but common examples include:
    - "period": int
    - "periods": List[int]
    - "window": int
    - "rank": int
    - "n_imfs": int
    - "n_modes": int
    etc.
    """


DecompMethodName = Literal[
    "stl",
    "mstl",
    "robuststl",
    "ssa",
    "std",
    "emd",
    "ceemdan",
    "vmd",
    "wavelet",
    "ma_baseline",
    "gabor_bands",
    "gabor_ridge",
    "gabor_cluster",
    "dr_ts_reg",
    "dr_ts_ae",
    "sl_lib",
]


def decompose_series(
    y: np.ndarray,
    method: DecompMethodName,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    """
    High-level dispatcher: run a given decomposition method on y.
    """

    method_key = method.lower()
    y_arr = _as_float_array(y)
    cfg = dict(config or {})
    if method_key in {"gabor_bands", "gabor_ridge"}:
        return gabor_method_dispatch(
            y_arr,
            cfg,
            fs=fs,
            mode=method_key.split("_", 1)[1],
        )

    if method_key == "gabor_cluster":
        return gabor_cluster_dispatch(y_arr, cfg)

    # New data-driven methods
    if method_key == "dr_ts_reg":
        return dr_ts_reg_decompose(y_arr, cfg, fs=fs, meta=meta)
    if method_key == "dr_ts_ae":
        return dr_ts_ae_decompose(y_arr, cfg, fs=fs, meta=meta)
    if method_key == "sl_lib":
        return sl_lib_decompose(y_arr, cfg, fs=fs, meta=meta)

    dispatch = {
        "stl": stl_decompose,
        "mstl": mstl_decompose,
        "robuststl": robuststl_decompose,
        "ssa": ssa_decompose,
        "std": std_decompose,
        "emd": emd_decompose,
        "ceemdan": ceemdan_decompose,
        "vmd": vmd_decompose,
        "wavelet": wavelet_decompose,
        "ma_baseline": ma_decompose,
    }

    if method_key not in dispatch:
        raise ValueError(
            f"Unknown decomposition method '{method}'. "
            f"Supported: {sorted(dispatch.keys())}"
        )

    return dispatch[method_key](y_arr, cfg, fs=fs, meta=meta)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _as_float_array(y: np.ndarray) -> np.ndarray:
    arr = np.asarray(y, dtype=float).reshape(-1)
    if arr.ndim != 1:
        raise ValueError("Input time series must be 1D.")
    return arr


def _dominant_frequency(x: np.ndarray, fs: float = 1.0) -> float:
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("Component must be 1D for frequency estimation.")
    if len(x) < 2:
        return 0.0
    x = x - np.mean(x)
    spectrum = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), d=1.0 / fs if fs > 0 else 1.0)
    if spectrum.size <= 1:
        return 0.0
    idx = int(np.argmax(spectrum[1:]) + 1) if spectrum.size > 1 else 0
    return float(freqs[idx]) if idx < len(freqs) else 0.0


def _moving_average(y: np.ndarray, window: int) -> np.ndarray:
    window = max(1, int(window))
    if window == 1 or len(y) == 0:
        return y.copy()
    kernel = np.ones(window) / window
    return np.convolve(y, kernel, mode="same")


# ---------------------------------------------------------------------------
# STL and MSTL
# ---------------------------------------------------------------------------


def stl_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    """
    STL decomposition: y = trend + seasonal + resid.
    """

    try:
        from statsmodels.tsa.seasonal import STL
    except ImportError as exc:
        raise ImportError("statsmodels is required for STL decomposition.") from exc

    cfg = dict(config or {})
    period = cfg.pop("period", None)
    if period is None:
        raise ValueError("STL requires 'period' in config.")
    period = int(period)

    stl = STL(y, period=period, **cfg)
    res = stl.fit()

    trend = np.asarray(res.trend)
    seasonal = np.asarray(res.seasonal)
    residual = np.asarray(res.resid)
    return DecompResult(
        trend=trend,
        season=seasonal,
        residual=residual,
        extra={"method": "stl", "params": {"period": period, **cfg}},
    )


def mstl_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    trend, season, residual, extra = decompose_mstl_components(y, fs, config or {}, meta or {})
    return DecompResult(trend=trend, season=season, residual=residual, extra=extra)


# ---------------------------------------------------------------------------
# SSA and STD (placeholder)
# ---------------------------------------------------------------------------


def ssa_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    """
    SSA-based decomposition of a 1D time series with optional frequency-based grouping.

    Config keys (all optional):
    - window: int, window length for embedding (default: T // 4, clipped to [2, T-1])
    - rank: int, number of leading RCs to reconstruct (default: 10)
    - trend_components: explicit RC indices for trend (overrides auto grouping)
    - season_components: explicit RC indices for season (overrides auto grouping)
    - primary_period: float, expected main seasonal period (enables freq-based grouping)
    - fs: float, sampling frequency for frequency calculations (default: 1.0)
    """

    y_arr = np.asarray(y, dtype=float)
    T = y_arr.shape[0]
    cfg = dict(config or {})

    window = int(cfg.get("window", max(4, T // 4)))
    window = min(max(2, window), T - 1)
    rank = int(cfg.get("rank", 10))
    rank = max(1, min(rank, window, T - window + 1))

    fs = float(cfg.get("fs", 1.0))
    primary_period = cfg.get("primary_period")
    primary_period = float(primary_period) if primary_period not in (None, 0) else None

    rc_list = _basic_ssa(y_arr, window=window, rank=rank)
    num_rc = len(rc_list)
    if num_rc == 0:
        zeros = np.zeros_like(y_arr)
        return DecompResult(
            trend=zeros,
            season=zeros,
            residual=y_arr.copy(),
            extra={
                "method": "ssa",
                "window": window,
                "rank": rank,
                "rc_list": [],
            },
        )

    trend_components = list(cfg.get("trend_components", []))
    season_components = list(cfg.get("season_components", []))
    extra_freq_info: Dict[str, Any] = {}

    if not trend_components and not season_components:
        if primary_period is not None and primary_period > 0:
            dom_freqs: List[float] = [
                _dominant_frequency(rc, fs=fs) for rc in rc_list
            ]
            f0 = 1.0 / primary_period if primary_period > 0 else 0.0
            tol_ratio = float(cfg.get("season_freq_tol_ratio", 0.25))
            tol = tol_ratio * f0
            low_freq_threshold = float(cfg.get("trend_freq_threshold", f0 / 4.0 if f0 else 0.05))

            for idx, f_dom in enumerate(dom_freqs):
                if f_dom <= max(low_freq_threshold, 1e-8):
                    trend_components.append(idx)
                elif f0 > 0 and abs(f_dom - f0) <= max(tol, 1e-8):
                    season_components.append(idx)

            if not trend_components and num_rc >= 1:
                trend_components.append(0)
            if not season_components:
                for idx in range(num_rc):
                    if idx not in trend_components:
                        season_components.append(idx)
                        break

            extra_freq_info = {
                "dom_freqs": dom_freqs,
                "primary_period_used": primary_period,
                "fs": fs,
                "trend_freq_threshold": low_freq_threshold,
                "season_freq_tolerance": tol,
            }
        else:
            if num_rc >= 1:
                trend_components.append(0)
            if num_rc >= 2:
                trend_components.append(1)
            if num_rc >= 4:
                season_components.extend([2, 3])
            elif num_rc >= 3:
                season_components.append(2)

    trend = _sum_components(rc_list, trend_components, T)
    season = _sum_components(rc_list, season_components, T)
    residual = y_arr - trend - season

    extra: Dict[str, Any] = {
        "method": "ssa",
        "window": window,
        "rank": rank,
        "rc_list": rc_list,
        "trend_components": trend_components,
        "season_components": season_components,
    }
    if extra_freq_info:
        extra.update(extra_freq_info)

    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        extra=extra,
    )


def std_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    from tsdecomp.methods.std import compute_std_components

    cfg = dict(config or {})
    period = cfg.get("period")
    if period is None and meta:
        period = meta.get("primary_period")

    result = compute_std_components(
        y,
        period=period,
        variant=str(cfg.get("variant", "STD")),
        max_period_search=int(cfg.get("max_period_search", 128)),
        eps=float(cfg.get("eps", 1e-12)),
    )

    extra: Dict[str, Any] = {
        "method": str(result["variant"]).lower(),
        "period": int(result["period"]),
        "n_cycles": int(result["n_cycles"]),
        "incomplete_cycle": bool(result["incomplete_cycle"]),
        "dispersion": np.asarray(result["dispersion"], dtype=float),
        "seasonal_shape": np.asarray(result["seasonal_shape"], dtype=float),
    }
    if result.get("average_seasonal_shape") is not None:
        extra["average_seasonal_shape"] = np.asarray(result["average_seasonal_shape"], dtype=float)

    return DecompResult(
        trend=np.asarray(result["trend"], dtype=float),
        season=np.asarray(result["season"], dtype=float),
        residual=np.asarray(result["residual"], dtype=float),
        extra=extra,
    )


def _basic_ssa(y: np.ndarray, window: int, rank: int) -> List[np.ndarray]:
    """
    Basic SSA: build Hankel matrix, run SVD, reconstruct RCs via diagonal averaging.
    """

    y_arr = np.asarray(y, dtype=float)
    T = y_arr.shape[0]
    L = int(window)
    if L < 2 or L > T - 1:
        raise ValueError(f"Invalid SSA window length L={L} for T={T}")
    K = T - L + 1

    X = np.empty((L, K), dtype=float)
    for i in range(K):
        X[:, i] = y_arr[i : i + L]

    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    d = min(rank, U.shape[1])
    rc_list: List[np.ndarray] = []
    for idx in range(d):
        Xi = np.outer(U[:, idx], s[idx] * Vt[idx, :])
        rc = _diagonal_averaging(Xi)[:T]
        rc_list.append(rc)
    return rc_list


def _diagonal_averaging(matrix: np.ndarray) -> np.ndarray:
    """
    Reconstruct a 1D series from a trajectory matrix via diagonal averaging.
    """

    L, K = matrix.shape
    T = L + K - 1
    recon = np.zeros(T)
    counts = np.zeros(T)
    for i in range(L):
        for j in range(K):
            recon[i + j] += matrix[i, j]
            counts[i + j] += 1.0
    counts[counts == 0.0] = 1.0
    return recon / counts


def _sum_components(components: List[np.ndarray], indices: List[int], length: int) -> np.ndarray:
    if not indices:
        return np.zeros(length)
    out = np.zeros(length)
    for idx in indices:
        if 0 <= idx < len(components):
            out += components[idx]
    return out


# ---------------------------------------------------------------------------
# EMD and VMD
# ---------------------------------------------------------------------------


def emd_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    """
    Empirical Mode Decomposition wrapper using PyEMD with frequency-based grouping.
    """

    if not _HAS_PYEMD:
        raise ImportError("PyEMD is required for EMD decomposition. Install 'EMD-signal' or 'PyEMD'.")

    y_arr = np.asarray(y, dtype=float)
    T = y_arr.shape[0]
    cfg = dict(config or {})

    fs = float(cfg.get("fs", 1.0))
    primary_period = cfg.get("primary_period")
    primary_period = float(primary_period) if primary_period not in (None, 0) else None
    n_imfs = cfg.get("n_imfs")

    emd = EMD()
    if n_imfs is not None:
        imfs = emd.emd(y_arr, max_imf=int(n_imfs))
    else:
        imfs = emd.emd(y_arr)
    imfs = np.asarray(imfs, dtype=float)
    if imfs.ndim == 1:
        imfs = imfs[np.newaxis, :]
    num_imfs = imfs.shape[0]
    if num_imfs == 0:
        zeros = np.zeros_like(y_arr)
        return DecompResult(
            trend=zeros,
            season=zeros,
            residual=y_arr.copy(),
            extra={"method": "emd", "imfs": np.empty((0, T)), "dominant_frequencies": []},
        )

    dom_freqs = [_dominant_frequency(comp, fs=fs) for comp in imfs]
    trend_imfs = list(cfg.get("trend_imfs", []))
    season_imfs = list(cfg.get("season_imfs", []))

    extra_freq: Dict[str, Any] = {}
    if not trend_imfs and not season_imfs:
        if primary_period is not None and primary_period > 0:
            f0 = 1.0 / primary_period
            tol = float(cfg.get("season_freq_tol_ratio", 0.25)) * f0
            low_thresh = float(cfg.get("trend_freq_threshold", f0 / 4.0 if f0 else 0.05))

            for idx, f_dom in enumerate(dom_freqs):
                if f_dom <= max(low_thresh, 1e-8):
                    trend_imfs.append(idx)
                elif f0 > 0 and abs(f_dom - f0) <= max(tol, 1e-8):
                    season_imfs.append(idx)

            if not trend_imfs:
                trend_imfs.append(num_imfs - 1)
            if not season_imfs:
                best_idx = int(np.argmin([abs(f - f0) for f in dom_freqs]))
                season_imfs.append(best_idx)

            extra_freq = {
                "primary_period_used": primary_period,
                "fs": fs,
                "trend_freq_threshold": low_thresh,
                "season_freq_tolerance": tol,
            }
        else:
            if num_imfs >= 1:
                trend_imfs.append(num_imfs - 1)
            if num_imfs >= 2:
                trend_imfs.append(num_imfs - 2)
            if num_imfs >= 1:
                season_imfs.append(0)
            if num_imfs >= 3:
                season_imfs.append(1)

    trend = _aggregate_modes(imfs, trend_imfs)
    season = _aggregate_modes(imfs, season_imfs)
    residual = y_arr - trend - season

    extra: Dict[str, Any] = {
        "method": "emd",
        "imfs": imfs,
        "dominant_frequencies": dom_freqs,
        "trend_components": trend_imfs,
        "season_components": season_imfs,
    }
    if extra_freq:
        extra.update(extra_freq)

    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        extra=extra,
    )


def ceemdan_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    trend, season, residual, extra = decompose_ceemdan_components(
        y, fs, config or {}, meta or {}
    )
    return DecompResult(trend=trend, season=season, residual=residual, extra=extra)


def vmd_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    trend, season, residual, extra = decompose_vmd_components(y, fs, config or {}, meta or {})
    return DecompResult(trend=trend, season=season, residual=residual, extra=extra)


def _aggregate_modes(modes: np.ndarray, indices: Optional[List[int]]) -> np.ndarray:
    if indices is None or len(indices) == 0:
        return np.zeros(modes.shape[1], dtype=float)
    valid = [idx for idx in indices if 0 <= idx < modes.shape[0]]
    if not valid:
        return np.zeros(modes.shape[1], dtype=float)
    return np.sum(modes[valid, :], axis=0)


# ---------------------------------------------------------------------------
# Wavelet-based decomposition
# ---------------------------------------------------------------------------


def wavelet_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    """
    Wavelet-based multi-scale decomposition using PyWavelets.
    """

    if not _HAS_PYWT:
        raise ImportError("PyWavelets (pywt) is required for wavelet decomposition. Install 'pywt'.")

    cfg = dict(config or {})
    wavelet_name = cfg.get("wavelet", "db4")
    level = cfg.get("level")
    wavelet = pywt.Wavelet(wavelet_name)
    max_level = pywt.dwt_max_level(len(y), wavelet.dec_len)
    if level is None:
        level = max(1, min(5, max_level))
    coeffs = pywt.wavedec(y, wavelet, level=level)
    num_coeffs = len(coeffs)

    trend_levels = cfg.get("trend_levels")
    season_levels = cfg.get("season_levels")

    if trend_levels is None:
        trend_levels = [0]
    if season_levels is None and num_coeffs > 2:
        season_levels = [1, 2]
    elif season_levels is None:
        season_levels = [idx for idx in range(1, num_coeffs)]

    trend = _reconstruct_from_levels(coeffs, trend_levels, wavelet_name, len(y))
    season = _reconstruct_from_levels(coeffs, season_levels, wavelet_name, len(y))
    residual = y - trend - season

    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        extra={
            "method": "wavelet",
            "params": cfg,
            "coeffs": coeffs,
        },
    )


def _reconstruct_from_levels(
    coeffs: List[np.ndarray],
    keep_levels: List[int],
    wavelet: str,
    target_len: int,
) -> np.ndarray:
    rec_coeffs: List[Optional[np.ndarray]] = []
    for idx, coeff in enumerate(coeffs):
        if idx in (keep_levels or []):
            rec_coeffs.append(np.copy(coeff))
        else:
            rec_coeffs.append(np.zeros_like(coeff))
    recon = pywt.waverec(rec_coeffs, wavelet)
    if recon.shape[0] > target_len:
        recon = recon[:target_len]
    elif recon.shape[0] < target_len:
        pad = target_len - recon.shape[0]
        recon = np.pad(recon, (0, pad), mode="edge")
    return recon


# ---------------------------------------------------------------------------
# Moving-average baseline
# ---------------------------------------------------------------------------


def ma_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    """
    Moving-average baseline decomposition.
    """

    cfg = dict(config or {})
    default_window = max(3, len(y) // 20)
    trend_window = int(cfg.get("trend_window", default_window))
    if trend_window % 2 == 0:
        trend_window += 1
    trend = _moving_average(y, trend_window)

    season_period = cfg.get("season_period")
    if season_period:
        season = _estimate_seasonal_indices(y - trend, int(season_period))
    else:
        season = np.zeros_like(y)
    residual = y - trend - season
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        extra={"method": "ma_baseline", "params": cfg},
    )


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


_GABOR_FIELDS = {field.name for field in dataclass_fields(GaborConfig)}

_GLOBAL_GABOR_CLUSTER_MODEL_CACHE: Dict[str, GaborClusterModel] = {}


def _get_gabor_cluster_model(model_path: str) -> GaborClusterModel:
    model_path = str(model_path)
    if model_path not in _GLOBAL_GABOR_CLUSTER_MODEL_CACHE:
        _GLOBAL_GABOR_CLUSTER_MODEL_CACHE[model_path] = GaborClusterModel.load(model_path)
    return _GLOBAL_GABOR_CLUSTER_MODEL_CACHE[model_path]


def gabor_method_dispatch(
    y: np.ndarray,
    cfg: Dict[str, Any],
    fs: float,
    mode: str,
) -> DecompResult:
    cfg_dict = dict(cfg or {})
    cfg_dict.setdefault("fs", fs)
    gabor_kwargs = {k: cfg_dict[k] for k in list(cfg_dict.keys()) if k in _GABOR_FIELDS}
    gabor_cfg = GaborConfig(**gabor_kwargs)
    if mode == "ridge":
        gabor_cfg.ridge = True
    gabor_result = gabor_decompose(y, gabor_cfg)
    return _gabor_to_decomp_result(y, gabor_result, mode)


def _gabor_to_decomp_result(
    y: np.ndarray,
    gabor_result,
    mode: str,
) -> DecompResult:
    components = gabor_result.components or {}
    trend = components.get("Trend_LF")
    if trend is None:
        trend = np.zeros_like(y)
    else:
        trend = np.asarray(trend, dtype=float)
    seasonal_parts = [
        np.asarray(arr, dtype=float)
        for name, arr in components.items()
        if name != "Trend_LF"
    ]
    if seasonal_parts:
        season = np.sum(seasonal_parts, axis=0)
    else:
        season = np.zeros_like(y)
    residual = (
        np.asarray(gabor_result.residual, dtype=float)
        if gabor_result.residual is not None
        else y - trend - season
    )
    extra = {
        "method": f"gabor_{mode}",
        "components": components,
        "gabor_meta": gabor_result.meta,
    }
    return DecompResult(trend=trend, season=season, residual=residual, extra=extra)


def gabor_cluster_dispatch(
    y: np.ndarray,
    cfg: Dict[str, Any],
) -> DecompResult:
    model: Optional[GaborClusterModel] = cfg.get("model")
    if model is None:
        model_path = cfg.get("model_path", "models/gabor_cluster_v1.npz")
        model = _get_gabor_cluster_model(model_path)
    max_clusters = cfg.get("max_clusters")
    trend_thr = float(cfg.get("trend_freq_thr", 0.08))
    cluster_res = gabor_cluster_decompose(y, model, max_clusters=max_clusters)
    ts_components = gabor_components_to_TS(cluster_res.components, model, trend_freq_thr=trend_thr)
    trend = ts_components.get("trend")
    seasonal = ts_components.get("seasonal")
    if trend is None:
        trend = np.zeros_like(y)
    if seasonal is None:
        seasonal = np.zeros_like(y)
    residual = cluster_res.residual
    extra = {
        "method": "gabor_cluster",
        "clusters": list(cluster_res.components.keys()),
        "meta": cluster_res.meta,
    }
    return DecompResult(trend=trend, season=seasonal, residual=residual, extra=extra)
def robuststl_decompose(
    y: np.ndarray,
    config: Optional[DecompConfig] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> DecompResult:
    trend, season, residual, extra = decompose_robuststl_components(y, fs, config or {}, meta or {})
    return DecompResult(trend=trend, season=season, residual=residual, extra=extra)
