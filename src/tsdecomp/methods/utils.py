import numpy as np
from typing import List, Optional, Sequence

def dominant_frequency(x: np.ndarray, fs: float = 1.0) -> float:
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return 0.0
    x = x - np.mean(x)
    spectrum = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), d=1.0 / fs if fs > 0 else 1.0)
    if spectrum.size <= 1:
        return 0.0
    idx = int(np.argmax(spectrum[1:]) + 1) if spectrum.size > 1 else 0
    return float(freqs[idx]) if idx < len(freqs) else 0.0

def ensure_period_list(
    periods: Optional[Sequence[float]],
    fallback: Optional[float],
    series_length: int,
) -> List[int]:
    cleaned: List[int] = []
    if periods:
        for val in periods:
            try:
                p_int = int(round(float(val)))
            except (TypeError, ValueError):
                continue
            if p_int >= 2:
                cleaned.append(p_int)
    if not cleaned and fallback:
        try:
            p = int(round(float(fallback)))
            if p >= 2:
                cleaned.append(p)
        except (TypeError, ValueError):
            pass
    if not cleaned:
        approx = max(2, series_length // 10)
        cleaned.append(approx)
    # deduplicate while preserving order
    seen = set()
    unique: List[int] = []
    for p in cleaned:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique

def aggregate_modes(modes: np.ndarray, indices: Optional[List[int]]) -> np.ndarray:
    if indices is None or len(indices) == 0:
        return np.zeros(modes.shape[1], dtype=float)
    valid = [idx for idx in indices if 0 <= idx < modes.shape[0]]
    if not valid:
        return np.zeros(modes.shape[1], dtype=float)
    return np.sum(modes[valid, :], axis=0)
