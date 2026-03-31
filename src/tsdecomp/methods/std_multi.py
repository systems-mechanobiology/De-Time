import numpy as np
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from ..core import DecompResult
from .ssa import ssa_decompose

"""
Archived experimental prototypes.

These helpers are intentionally not registered in the public MethodRegistry and
are not part of the supported public method surface.
"""

@dataclass
class STDBasisCache:
    """
    Cache for STD bases.
    """
    bases: Dict[str, np.ndarray] # key -> basis matrix (L, K) or similar

    def fit(self, X_windows: np.ndarray):
        # Placeholder: fit bases from windows
        pass

    def project(self, window: np.ndarray) -> np.ndarray:
        # Placeholder: project window onto basis
        return window

    def save(self, path: str):
        np.savez(path, **self.bases)

    @staticmethod
    def load(path: str) -> "STDBasisCache":
        data = np.load(path)
        return STDBasisCache(bases={k: data[k] for k in data.files})

def std_multi_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """
    Multi-scale STD decomposition with caching.
    """
    # Check for faststd/fasttimes
    try:
        import fasttimes
        _HAS_FASTTIMES = True
    except ImportError:
        _HAS_FASTTIMES = False

    cfg = params.copy()
    mode = cfg.get("mode", "STD_MULTI") # or STD_FULL_ABLATION
    
    # If fasttimes is not available, we might fallback to SSA or raise error.
    # For this task, we will fallback to SSA if possible or just implement the structure.
    if not _HAS_FASTTIMES:
        # Fallback to SSA for now as per prompt hint "Placeholder for user-provided STD implementation"
        # But we should try to respect the structure.
        return ssa_decompose(y, params)

    # Real implementation would go here using fasttimes
    # ...
    
    return DecompResult(
        trend=np.zeros_like(y),
        season=np.zeros_like(y),
        residual=y,
        meta={"method": "STD_MULTI", "params": cfg, "note": "Mock implementation"}
    )

def std_full_ablation_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    return std_multi_decompose(y, {**params, "mode": "STD_FULL_ABLATION"})
