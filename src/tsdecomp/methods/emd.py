import numpy as np
from typing import Dict, Any, List, Optional
from ..core import DecompResult
from ..registry import MethodRegistry

try:
    from PyEMD import EMD
    _HAS_PYEMD = True
    _PYEMD_IMPORT_ERROR = None
except Exception as exc:
    _HAS_PYEMD = False
    _PYEMD_IMPORT_ERROR = exc

from .utils import dominant_frequency, aggregate_modes

def _dominant_frequency(x: np.ndarray, fs: float = 1.0) -> float:
    return dominant_frequency(x, fs)

def _aggregate_modes(modes: np.ndarray, indices: Optional[List[int]]) -> np.ndarray:
    return aggregate_modes(modes, indices)

@MethodRegistry.register("EMD")
def emd_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """
    Empirical Mode Decomposition wrapper using PyEMD with frequency-based grouping.
    """
    if not _HAS_PYEMD:
        raise ImportError(
            "PyEMD is required for EMD decomposition. Install 'EMD-signal' or 'PyEMD'."
        ) from _PYEMD_IMPORT_ERROR

    y_arr = np.asarray(y, dtype=float)
    T = y_arr.shape[0]
    cfg = params.copy()

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
            meta={"method": "EMD", "imfs": [], "dominant_frequencies": []}
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

    meta = {
        "method": "EMD",
        "imfs_shape": imfs.shape,
        "dominant_frequencies": dom_freqs,
        "trend_components": trend_imfs,
        "season_components": season_imfs,
    }
    if extra_freq:
        meta.update(extra_freq)

    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        meta=meta,
    )
