import numpy as np
from typing import Dict, Any, List, Optional
from ..core import DecompResult
from ..registry import MethodRegistry

try:
    import pywt
    _HAS_PYWT = True
    _PYWT_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - depends on local binary wheels
    pywt = None
    _HAS_PYWT = False
    _PYWT_IMPORT_ERROR = exc

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

@MethodRegistry.register("WAVELET")
def wavelet_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """
    Wavelet-based multi-scale decomposition using PyWavelets.
    """
    if not _HAS_PYWT:
        raise ImportError(
            "PyWavelets (pywt) is required for wavelet decomposition."
        ) from _PYWT_IMPORT_ERROR

    cfg = params.copy()
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
        meta={
            "method": "WAVELET",
            "params": cfg,
            "coeffs_shapes": [c.shape for c in coeffs]
        },
    )
