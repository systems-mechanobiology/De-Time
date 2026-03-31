"""DR-TS-SL-LIB: Operator-based Basis Library + FAISS Candidate Selection.

This module implements a decomposition approach using a pre-computed library of
basis functions (polynomials, sinusoids, logistic curves) with FAISS for fast
candidate retrieval and sparse regression for coefficient optimization.

Decomposition form:
    x_t ≈ Σ_i c_i φ_i(t) + r_t

Where φ_i are basis functions from a trend or seasonal library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import nnls

try:
    import faiss
    _HAS_FAISS = True
except ImportError:
    _HAS_FAISS = False
    faiss = None


@dataclass
class SLLibConfig:
    """Configuration for SL-LIB decomposition.
    
    Attributes
    ----------
    library_size : int
        Total number of basis functions in the library.
    n_trend_bases : int
        Number of trend basis functions.
    n_seasonal_bases : int
        Number of seasonal basis functions.
    n_candidates : int
        Number of candidates to retrieve from FAISS.
    sparsity_lambda : float
        L1 regularization for sparse coefficients.
    max_poly_degree : int
        Maximum polynomial degree for trend bases.
    min_period : int
        Minimum period for sinusoidal bases.
    max_period : int
        Maximum period for sinusoidal bases.
    """
    library_size: int = 500
    n_trend_bases: int = 200
    n_seasonal_bases: int = 300
    n_candidates: int = 100  # v1.1.0: increased from 50
    sparsity_lambda: float = 0.001  # v1.1.0: reduced from 0.01
    max_poly_degree: int = 5
    min_period: int = 4
    max_period: int = 128


def _generate_polynomial_bases(length: int, n_bases: int, max_degree: int = 5) -> np.ndarray:
    """Generate polynomial trend basis functions.
    
    Returns
    -------
    bases : np.ndarray of shape (n_bases, length)
    """
    t = np.linspace(-1, 1, length)
    bases = []
    
    # Standard polynomials
    for degree in range(max_degree + 1):
        bases.append(t ** degree)
    
    # Chebyshev-like bases
    while len(bases) < n_bases // 2:
        d = len(bases) % (max_degree + 1)
        offset = len(bases) // (max_degree + 1) * 0.1
        bases.append(np.cos(d * np.arccos(np.clip(t + offset, -1, 1))))
    
    # Logistic-style bases
    while len(bases) < n_bases * 3 // 4:
        k = 1.0 + len(bases) * 0.5  # steepness
        midpoint = (len(bases) - n_bases // 2) / (n_bases // 4) - 0.5
        bases.append(1.0 / (1.0 + np.exp(-k * (t - midpoint))))
    
    # Smoothed random-walk bases (cumulative sums of smooth noise)
    rng = np.random.RandomState(42)
    while len(bases) < n_bases:
        noise = rng.randn(length)
        # Smooth the noise
        kernel = np.ones(max(3, length // 20)) / max(3, length // 20)
        smooth_noise = np.convolve(noise, kernel, mode='same')
        cumsum = np.cumsum(smooth_noise)
        # Normalize
        cumsum = (cumsum - cumsum.mean()) / (cumsum.std() + 1e-8)
        bases.append(cumsum)
    
    bases = np.array(bases[:n_bases])
    # Normalize each basis
    norms = np.linalg.norm(bases, axis=1, keepdims=True) + 1e-8
    return bases / norms


def _generate_sinusoidal_bases(
    length: int,
    n_bases: int,
    min_period: int = 4,
    max_period: int = 128,
) -> np.ndarray:
    """Generate sinusoidal seasonal basis functions.
    
    Returns
    -------
    bases : np.ndarray of shape (n_bases, length)
    """
    t = np.arange(length, dtype=float)
    bases = []
    
    # Generate periods logarithmically spaced
    periods = np.logspace(np.log10(min_period), np.log10(min(max_period, length // 2)), n_bases // 2)
    
    for period in periods:
        freq = 2 * np.pi / period
        # Sine and cosine at this frequency
        bases.append(np.sin(freq * t))
        bases.append(np.cos(freq * t))
        
        # Harmonics
        if len(bases) < n_bases:
            bases.append(np.sin(2 * freq * t))
        if len(bases) < n_bases:
            bases.append(np.cos(2 * freq * t))
    
    # Multi-harmonic combinations
    rng = np.random.RandomState(123)
    while len(bases) < n_bases:
        n_harmonics = rng.randint(2, 5)
        base_period = rng.uniform(min_period, max_period)
        combo = np.zeros(length)
        for h in range(1, n_harmonics + 1):
            amp = rng.uniform(0.5, 1.5) / h
            phase = rng.uniform(0, 2 * np.pi)
            combo += amp * np.sin(h * 2 * np.pi / base_period * t + phase)
        bases.append(combo)
    
    bases = np.array(bases[:n_bases])
    # Normalize
    norms = np.linalg.norm(bases, axis=1, keepdims=True) + 1e-8
    return bases / norms


def build_basis_library(
    length: int,
    config: Optional[SLLibConfig] = None,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Build the basis function library.
    
    Parameters
    ----------
    length : int
        Length of the time series.
    config : SLLibConfig, optional
        Configuration for library generation.
        
    Returns
    -------
    trend_bases : np.ndarray of shape (n_trend, length)
    seasonal_bases : np.ndarray of shape (n_seasonal, length)
    metadata : dict
        Library metadata.
    """
    cfg = config or SLLibConfig()
    
    trend_bases = _generate_polynomial_bases(
        length,
        cfg.n_trend_bases,
        max_degree=cfg.max_poly_degree,
    )
    
    seasonal_bases = _generate_sinusoidal_bases(
        length,
        cfg.n_seasonal_bases,
        min_period=cfg.min_period,
        max_period=cfg.max_period,
    )
    
    metadata = {
        'length': length,
        'n_trend': trend_bases.shape[0],
        'n_seasonal': seasonal_bases.shape[0],
    }
    
    return trend_bases, seasonal_bases, metadata


def _build_faiss_index(bases: np.ndarray) -> Any:
    """Build a FAISS index for the basis library.
    
    Parameters
    ----------
    bases : np.ndarray of shape (n_bases, length)
        Basis functions as feature vectors.
        
    Returns
    -------
    index : faiss.IndexFlatIP
        FAISS inner product index.
    """
    if not _HAS_FAISS:
        return None
    
    # Normalize for inner product search
    bases_norm = bases / (np.linalg.norm(bases, axis=1, keepdims=True) + 1e-8)
    bases_norm = bases_norm.astype(np.float32)
    
    d = bases_norm.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(bases_norm)
    
    return index


def _search_candidates_faiss(
    query: np.ndarray,
    index: Any,
    k: int,
) -> np.ndarray:
    """Search for k nearest basis candidates using FAISS."""
    query_norm = query / (np.linalg.norm(query) + 1e-8)
    query_norm = query_norm.astype(np.float32).reshape(1, -1)
    
    _, indices = index.search(query_norm, k)
    return indices[0]


def _search_candidates_numpy(
    query: np.ndarray,
    bases: np.ndarray,
    k: int,
) -> np.ndarray:
    """Fallback search using numpy correlation."""
    query_norm = query / (np.linalg.norm(query) + 1e-8)
    bases_norm = bases / (np.linalg.norm(bases, axis=1, keepdims=True) + 1e-8)
    
    # Inner products
    scores = bases_norm @ query_norm
    indices = np.argsort(-np.abs(scores))[:k]
    return indices


def _sparse_regression(
    y: np.ndarray,
    B: np.ndarray,
    lambda_l1: float = 0.01,
    max_iter: int = 100,
) -> np.ndarray:
    """Solve sparse regression: min ||y - Bc||² + λ||c||₁
    
    Uses iteratively reweighted least squares (IRLS) approximation.
    """
    # Expect B shape (length, n_bases)
    n_bases = B.shape[1]
    
    if n_bases == 0:
        return np.array([])
    
    # Initial non-negative least squares (simple but works)
    # For speed, use OLS then threshold
    BT = B.T
    BTB = BT @ B
    BTy = BT @ y
    
    # Add small regularization for stability
    reg = lambda_l1 * np.eye(BTB.shape[0])
    
    try:
        c = np.linalg.solve(BTB + reg, BTy)
    except np.linalg.LinAlgError:
        c = np.linalg.lstsq(BTB + reg, BTy, rcond=None)[0]
    
    # Soft threshold for L1
    threshold = lambda_l1 * 0.5
    c = np.sign(c) * np.maximum(np.abs(c) - threshold, 0)
    
    return c


def sl_lib_decompose(
    y: np.ndarray,
    config: Optional[Dict[str, Any]] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> "DecompResult":
    """SL-LIB decomposition using basis library and FAISS selection.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series.
    config : dict, optional
        Configuration for the method.
    fs : float
        Sampling frequency.
    meta : dict, optional
        Metadata from scenario.
        
    Returns
    -------
    DecompResult
        Decomposition result.
    """
    from .decomp_methods import DecompResult
    
    y_arr = np.asarray(y, dtype=float).ravel()
    n = len(y_arr)
    cfg_dict = dict(config or {})
    
    # Build config
    lib_cfg = SLLibConfig(
        library_size=int(cfg_dict.get('library_size', 500)),
        n_trend_bases=int(cfg_dict.get('n_trend_bases', 200)),
        n_seasonal_bases=int(cfg_dict.get('n_seasonal_bases', 300)),
        n_candidates=int(cfg_dict.get('n_candidates', 100)),  # v1.1.0
        sparsity_lambda=float(cfg_dict.get('sparsity_lambda', 0.001)),  # v1.1.0
        max_poly_degree=int(cfg_dict.get('max_poly_degree', 5)),
        min_period=int(cfg_dict.get('min_period', 4)),
        max_period=int(cfg_dict.get('max_period', min(128, n // 2))),
    )
    
    # Build library
    trend_bases, seasonal_bases, lib_meta = build_basis_library(n, lib_cfg)
    
    # Normalize input for search
    y_centered = y_arr - np.mean(y_arr)
    y_norm = y_centered / (np.std(y_centered) + 1e-8)
    
    # Step 1: Find trend candidates and fit trend
    if _HAS_FAISS:
        trend_index = _build_faiss_index(trend_bases)
        trend_cand_idx = _search_candidates_faiss(
            y_norm, trend_index, min(lib_cfg.n_candidates, trend_bases.shape[0])
        )
    else:
        trend_cand_idx = _search_candidates_numpy(
            y_norm, trend_bases, min(lib_cfg.n_candidates, trend_bases.shape[0])
        )
    
    B_trend = trend_bases[trend_cand_idx].T
    c_trend = _sparse_regression(y_arr, B_trend, lib_cfg.sparsity_lambda)
    
    if len(c_trend) > 0:
        trend = B_trend @ c_trend
    else:
        trend = np.zeros(n)
    
    # Step 2: Find seasonal candidates on residual
    residual_after_trend = y_arr - trend
    
    if _HAS_FAISS:
        seasonal_index = _build_faiss_index(seasonal_bases)
        seasonal_cand_idx = _search_candidates_faiss(
            residual_after_trend, seasonal_index, min(lib_cfg.n_candidates, seasonal_bases.shape[0])
        )
    else:
        seasonal_cand_idx = _search_candidates_numpy(
            residual_after_trend, seasonal_bases, min(lib_cfg.n_candidates, seasonal_bases.shape[0])
        )
    
    B_seasonal = seasonal_bases[seasonal_cand_idx].T
    c_seasonal = _sparse_regression(residual_after_trend, B_seasonal, lib_cfg.sparsity_lambda)
    
    if len(c_seasonal) > 0:
        seasonal = B_seasonal @ c_seasonal
    else:
        seasonal = np.zeros(n)
    
    # Ensure seasonal is zero-mean
    seasonal = seasonal - np.mean(seasonal)
    
    # Final residual
    residual = y_arr - trend - seasonal
    
    extra = {
        'method': 'sl_lib',
        'n_trend_candidates': len(trend_cand_idx),
        'n_seasonal_candidates': len(seasonal_cand_idx),
        'n_active_trend': int(np.sum(np.abs(c_trend) > 1e-8)) if len(c_trend) > 0 else 0,
        'n_active_seasonal': int(np.sum(np.abs(c_seasonal) > 1e-8)) if len(c_seasonal) > 0 else 0,
        'used_faiss': _HAS_FAISS,
    }
    
    return DecompResult(
        trend=trend,
        season=seasonal,
        residual=residual,
        extra=extra,
    )
