import numpy as np
from typing import Dict, Any, Tuple, Optional
from ..core import DecompResult
from ..registry import MethodRegistry
from .utils import dominant_frequency

try:
    from PyEMD import CEEMDAN
    _HAS_CEEMDAN = True
    _CEEMDAN_IMPORT_ERROR = None
except Exception as exc:
    _HAS_CEEMDAN = False
    _CEEMDAN_IMPORT_ERROR = exc

def estimate_imf_dom_freqs(imfs: np.ndarray, fs: float) -> np.ndarray:
    freqs = []
    for imf in imfs:
        freqs.append(dominant_frequency(imf, fs))
    return np.array(freqs, dtype=float)

def assign_imfs_to_components(
    freqs: np.ndarray,
    primary_freq: Optional[float],
    config: Dict[str, Any],
) -> Tuple[np.ndarray, np.ndarray]:
    trend_threshold = float(config.get("trend_freq_max", 0.02))
    if primary_freq:
        trend_threshold = config.get("trend_freq_max", primary_freq / 8.0)

    season_band_factor = float(config.get("season_band_factor", 2.0))
    trend_mask = freqs <= max(trend_threshold, 1e-6)
    season_mask = np.zeros_like(freqs, dtype=bool)

    if primary_freq and primary_freq > 0:
        low = primary_freq / max(season_band_factor, 1.0)
        high = primary_freq * max(season_band_factor, 1.0)
        season_mask = (freqs >= low) & (freqs <= high)

    if not trend_mask.any():
        trend_mask[np.argmin(freqs)] = True
    if not season_mask.any():
        if primary_freq:
            idx = int(np.argmin(np.abs(freqs - primary_freq)))
            season_mask[idx] = True
        else:
            season_mask[~trend_mask] = True
    return trend_mask, season_mask

@MethodRegistry.register("CEEMDAN")
def ceemdan_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    if not _HAS_CEEMDAN:
        raise ImportError(
            "PyEMD>=1.0 is required for CEEMDAN decomposition."
        ) from _CEEMDAN_IMPORT_ERROR

    cfg = params.copy()
    ceemdan = CEEMDAN()
    if "trials" in cfg:
        ceemdan.trials = int(cfg["trials"])
    if "noise_width" in cfg:
        ceemdan.noise_width = float(cfg["noise_width"])

    imfs = ceemdan(y)
    imfs = np.asarray(imfs, dtype=float)
    if imfs.ndim == 1:
        imfs = imfs[np.newaxis, :]
    
    if imfs.size == 0:
        zeros = np.zeros_like(y)
        return DecompResult(
            trend=zeros,
            season=zeros,
            residual=y.copy(),
            meta={"method": "CEEMDAN", "imfs": []}
        )

    fs = float(cfg.get("fs", 1.0))
    freqs = estimate_imf_dom_freqs(imfs, fs)
    primary_period = cfg.get("primary_period")
    primary_freq = 1.0 / float(primary_period) if primary_period else None

    trend_mask, season_mask = assign_imfs_to_components(freqs, primary_freq, cfg)

    trend = imfs[trend_mask].sum(axis=0) if trend_mask.any() else np.zeros_like(y)
    season = imfs[season_mask].sum(axis=0) if season_mask.any() else np.zeros_like(y)
    residual = y - trend - season
    
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        meta={
            "method": "CEEMDAN",
            "dominant_frequencies": freqs.tolist(),
            "trend_mask": trend_mask.tolist(),
            "season_mask": season_mask.tolist(),
            "primary_period": primary_period,
        }
    )
