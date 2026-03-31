"""DR-TS-REG: Regularized Trend + Seasonal + Residual Decomposition.

This module implements a convex optimization approach to decompose a time series
into trend, seasonal, and residual components using regularization penalties.

Objective:
    min_{τ, s, r}  ||x - τ - s - r||² + λ_T*||Δ²τ||² + λ_S*||s - s_{lag P}||² + λ_R*||r||²

Where:
    - τ is the trend (smooth via second-order differences)
    - s is the seasonal component (periodic with period P)
    - r is the residual
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


@dataclass
class DRTSREGConfig:
    """Configuration for DR-TS-REG decomposition.
    
    Attributes
    ----------
    lambda_T : float
        Regularization weight for trend smoothness (second-order diff).
        v1.1.0: Reduced from 100.0 to 5.0 to prevent over-smoothing.
    lambda_S : float
        Regularization weight for seasonal periodicity.
    lambda_R : float
        Regularization weight for residual.
    period : int or None
        Seasonal period. If None, will be estimated or use metadata.
    max_period_search : int
        Maximum period to search if auto-detecting.
    """
    lambda_T: float = 5.0  # v1.1.0: reduced from 100.0
    lambda_S: float = 50.0
    lambda_R: float = 0.1
    period: Optional[int] = None
    max_period_search: int = 128


def _build_second_diff_matrix(n: int) -> sparse.csr_matrix:
    """Build sparse second-order difference matrix D2 of shape (n-2, n).
    
    D2[i, :] computes x[i] - 2*x[i+1] + x[i+2]
    """
    if n < 3:
        return sparse.csr_matrix((0, n))
    
    rows = np.arange(n - 2)
    data = np.ones((n - 2) * 3)
    data[1::3] = -2  # middle coefficient
    
    row_idx = np.repeat(rows, 3)
    col_idx = np.column_stack([rows, rows + 1, rows + 2]).ravel()
    
    return sparse.csr_matrix((data, (row_idx, col_idx)), shape=(n - 2, n))


def _build_seasonal_lag_matrix(n: int, period: int) -> sparse.csr_matrix:
    """Build sparse matrix S_P of shape (n-P, n) for seasonal periodicity.
    
    S_P[i, :] computes s[i] - s[i+P]
    """
    if period >= n or period < 1:
        return sparse.csr_matrix((0, n))
    
    m = n - period
    rows = np.arange(m)
    row_idx = np.concatenate([rows, rows])
    col_idx = np.concatenate([rows, rows + period])
    data = np.concatenate([np.ones(m), -np.ones(m)])
    
    return sparse.csr_matrix((data, (row_idx, col_idx)), shape=(m, n))


def _estimate_dominant_period(y: np.ndarray, max_period: int = 128) -> int:
    """Estimate dominant period from FFT of the signal."""
    y_centered = y - np.mean(y)
    n = len(y_centered)
    
    if n < 4:
        return max(1, n // 2)
    
    # FFT magnitude (skip DC component)
    fft_mag = np.abs(np.fft.rfft(y_centered))
    freqs = np.fft.rfftfreq(n)
    
    if len(fft_mag) < 2:
        return max(1, n // 4)
    
    fft_mag[0] = 0  # ignore DC
    
    # Find peak frequency
    peak_idx = np.argmax(fft_mag)
    if peak_idx == 0 or freqs[peak_idx] < 1e-10:
        return max(1, min(n // 4, max_period))
    
    period = int(round(1.0 / freqs[peak_idx]))
    period = max(2, min(period, max_period, n // 2))
    
    return period


def dr_ts_reg_solve(
    y: np.ndarray,
    period: int,
    lambda_T: float = 5.0,  # v1.1.0: reduced from 100
    lambda_S: float = 50.0,
    lambda_R: float = 0.1,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve the regularized decomposition problem.
    
    The problem is reformulated as a linear system by stacking the variables:
    z = [τ; s] (length 2n), and solving for the minimum.
    
    The residual is then r = y - τ - s.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series of length n.
    period : int
        Seasonal period P.
    lambda_T : float
        Trend smoothness regularization.
    lambda_S : float
        Seasonal periodicity regularization.
    lambda_R : float
        Residual regularization.
        
    Returns
    -------
    trend : np.ndarray
        Estimated trend component.
    seasonal : np.ndarray
        Estimated seasonal component.
    residual : np.ndarray
        Residual = y - trend - seasonal.
    """
    n = len(y)
    y = np.asarray(y, dtype=float).ravel()
    
    if n < 3:
        # Trivial case
        return y.copy(), np.zeros(n), np.zeros(n)
    
    # Ensure period is valid
    period = max(1, min(period, n - 1))
    
    # Build regularization matrices
    D2 = _build_second_diff_matrix(n)  # (n-2, n) for trend
    SP = _build_seasonal_lag_matrix(n, period)  # (n-P, n) for seasonal
    
    # Identity matrices
    I_n = sparse.eye(n, format='csr')
    Z_n = sparse.csr_matrix((n, n))
    
    # The objective is:
    # ||y - τ - s||² + λ_T||D2*τ||² + λ_S||SP*s||² + λ_R||y - τ - s||²
    # 
    # Let's denote the reconstruction as r = y - τ - s.
    # The reconstruction term becomes (1 + λ_R) * ||y - τ - s||²
    # 
    # Taking derivatives and setting to zero:
    # For τ: 2(1+λ_R)(τ + s - y) + 2*λ_T*D2'*D2*τ = 0
    # For s: 2(1+λ_R)(τ + s - y) + 2*λ_S*SP'*SP*s = 0
    #
    # This gives the linear system:
    # [(1+λ_R)*I + λ_T*D2'D2,    (1+λ_R)*I           ] [τ]   [(1+λ_R)*y]
    # [(1+λ_R)*I,                (1+λ_R)*I + λ_S*S'S ] [s] = [(1+λ_R)*y]
    
    alpha = 1.0 + lambda_R
    
    # Build the blocks
    D2TD2 = D2.T @ D2  # (n, n)
    STPSP = SP.T @ SP  # (n, n)
    
    A11 = alpha * I_n + lambda_T * D2TD2
    A12 = alpha * I_n
    A21 = alpha * I_n
    A22 = alpha * I_n + lambda_S * STPSP
    
    # Build full system matrix [A11, A12; A21, A22]
    A_top = sparse.hstack([A11, A12])
    A_bot = sparse.hstack([A21, A22])
    A = sparse.vstack([A_top, A_bot]).tocsr()
    
    # Right-hand side
    b = np.concatenate([alpha * y, alpha * y])
    
    # Solve
    try:
        z = spsolve(A, b)
    except Exception:
        # Fallback: simple decomposition
        trend = np.convolve(y, np.ones(max(3, n // 10)) / max(3, n // 10), mode='same')
        seasonal = np.zeros(n)
        residual = y - trend
        return trend, seasonal, residual
    
    trend = z[:n]
    seasonal = z[n:]
    residual = y - trend - seasonal
    
    return trend, seasonal, residual


def dr_ts_reg_decompose(
    y: np.ndarray,
    config: Optional[Dict[str, Any]] = None,
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> "DecompResult":
    """DR-TS-REG decomposition: regularized trend + seasonal + residual.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series.
    config : dict, optional
        Configuration with keys: lambda_T, lambda_S, lambda_R, period.
    fs : float
        Sampling frequency (not directly used but kept for interface consistency).
    meta : dict, optional
        Metadata containing scenario info (e.g., primary_period).
        
    Returns
    -------
    DecompResult
        Decomposition result with trend, season, residual, and extra info.
    """
    from .decomp_methods import DecompResult
    
    y_arr = np.asarray(y, dtype=float).ravel()
    n = len(y_arr)
    cfg = dict(config or {})
    
    # Extract hyperparameters
    lambda_T = float(cfg.get('lambda_T', 5.0))  # v1.1.0: default 5.0
    lambda_S = float(cfg.get('lambda_S', 50.0))
    lambda_R = float(cfg.get('lambda_R', 0.1))
    
    # Determine period
    period = cfg.get('period')
    if period is None and meta:
        period = meta.get('primary_period')
    if period is None:
        max_search = int(cfg.get('max_period_search', 128))
        period = _estimate_dominant_period(y_arr, max_period=max_search)
    period = int(period)
    
    # Solve
    trend, seasonal, residual = dr_ts_reg_solve(
        y_arr,
        period=period,
        lambda_T=lambda_T,
        lambda_S=lambda_S,
        lambda_R=lambda_R,
    )
    
    extra = {
        'method': 'dr_ts_reg',
        'params': {
            'lambda_T': lambda_T,
            'lambda_S': lambda_S,
            'lambda_R': lambda_R,
            'period': period,
        },
    }
    
    return DecompResult(
        trend=trend,
        season=seasonal,
        residual=residual,
        extra=extra,
    )
