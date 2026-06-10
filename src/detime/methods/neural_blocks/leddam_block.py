from __future__ import annotations

from typing import Any, Dict

import numpy as np

from ...core import DecompResult
from ...registry import MethodRegistry


def _normalize_kernel_size(raw_value: Any, length: int) -> int:
    try:
        kernel_size = int(round(float(raw_value)))
    except (TypeError, ValueError):
        kernel_size = 25

    kernel_size = max(1, kernel_size)
    if kernel_size % 2 == 0:
        kernel_size += 1
    if length <= 1:
        return 1

    max_kernel = length if length % 2 == 1 else length - 1
    return max(1, min(kernel_size, max_kernel))


def _gaussian_kernel(kernel_size: int, sigma: float) -> np.ndarray:
    kernel_size = max(1, int(kernel_size))
    if kernel_size == 1:
        return np.ones(1, dtype=float)

    sigma = float(sigma)
    if not np.isfinite(sigma) or sigma <= 0:
        sigma = 1.0

    center = kernel_size // 2
    positions = np.arange(kernel_size, dtype=float) - float(center)
    weights = np.exp(-(positions**2) / (2.0 * (sigma**2)))
    weights_sum = float(np.sum(weights))
    if not np.isfinite(weights_sum) or weights_sum <= 0:
        return np.full(kernel_size, 1.0 / kernel_size, dtype=float)
    return (weights / weights_sum).astype(float)


def _replicate_pad_smooth(series: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    arr = np.asarray(series, dtype=float).reshape(-1)
    if arr.size == 0:
        return arr.copy()
    if kernel.size <= 1:
        return arr.copy()

    pad = (kernel.size - 1) // 2
    padded = np.pad(arr, (pad, pad), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


@MethodRegistry.register("LEDDAM_BLOCK")
def leddam_block_decompose(y: np.ndarray, params: Dict[str, Any]) -> DecompResult:
    """
    Extracted standalone LD block from Leddam.

    The original Leddam module applies a Gaussian-initialized 1D convolution
    over each channel to produce a smooth main/trend stream. Here we expose
    that block as a lightweight decomposition operator for a 1D series.
    """
    cfg = dict(params or {})
    arr = np.asarray(y, dtype=float).reshape(-1)
    length = int(arr.size)

    kernel_size = _normalize_kernel_size(cfg.get("kernel_size", 25), length)
    sigma = float(cfg.get("sigma", 1.0))
    kernel = _gaussian_kernel(kernel_size, sigma)
    trend = _replicate_pad_smooth(arr, kernel)
    season = arr - trend
    residual = arr - trend - season

    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components={"ld_trend": trend.copy(), "kernel": kernel.copy()},
        meta={
            "method": "LEDDAM_BLOCK",
            "block_family": "learnable_decomposition_ld",
            "kernel_size": int(kernel_size),
            "sigma": float(sigma),
            "padding_mode": "replicate",
            "derived_residual": True,
            "notes": "Standalone extracted LD smoothing block from Leddam.",
        },
    )
