import numpy as np
from time import perf_counter
from typing import Dict, Any, List, Optional
from .._native import invoke_native
from ..backends import finalize_result, resolve_backend, result_from_native_payload, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry

from .utils import dominant_frequency

def _dominant_frequency(x: np.ndarray, fs: float = 1.0) -> float:
    return dominant_frequency(x, fs)

def _diagonal_averaging(matrix: np.ndarray) -> np.ndarray:
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

def _basic_ssa(y: np.ndarray, window: int, rank: int) -> List[np.ndarray]:
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

def _sum_components(components: List[np.ndarray], indices: List[int], length: int) -> np.ndarray:
    if not indices:
        return np.zeros(length)
    out = np.zeros(length)
    for idx in indices:
        if 0 <= idx < len(components):
            out += components[idx]
    return out

@MethodRegistry.register("SSA")
def ssa_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    y_arr = np.asarray(y, dtype=float)
    T = y_arr.shape[0]

    window = int(cfg.get("window", max(4, T // 4)))
    window = min(max(2, window), T - 1)
    rank = int(cfg.get("rank", 10))
    rank = max(1, min(rank, window, T - window + 1))

    fs = float(cfg.get("fs", 1.0))
    primary_period = cfg.get("primary_period")
    primary_period = float(primary_period) if primary_period not in (None, 0) else None
    backend = resolve_backend("SSA", runtime, native_methods=("ssa_decompose",))

    if backend == "native":
        payload = invoke_native(
            "ssa_decompose",
            y_arr,
            window=window,
            rank=rank,
            fs=fs,
            primary_period=primary_period,
            trend_components=list(cfg.get("trend_components", [])),
            season_components=list(cfg.get("season_components", [])),
            season_freq_tol_ratio=float(cfg.get("season_freq_tol_ratio", 0.25)),
            trend_freq_threshold=cfg.get("trend_freq_threshold"),
            speed_mode=runtime.speed_mode,
            power_iterations=int(cfg.get("power_iterations", 12)),
            seed=42 if runtime.seed is None else int(runtime.seed),
        )
        return finalize_result(
            result_from_native_payload(payload, method="SSA"),
            method="SSA",
            runtime=runtime,
            backend_used="native",
            started_at=started_at,
        )

    rc_list = _basic_ssa(y_arr, window=window, rank=rank)
    num_rc = len(rc_list)
    
    if num_rc == 0:
        zeros = np.zeros_like(y_arr)
        return finalize_result(
            DecompResult(
            trend=zeros,
            season=zeros,
            residual=y_arr.copy(),
            meta={"method": "SSA", "window": window, "rank": rank, "rc_list": []}
            ),
            method="SSA",
            runtime=runtime,
            backend_used="python",
            started_at=started_at,
        )

    trend_components = list(cfg.get("trend_components", []))
    season_components = list(cfg.get("season_components", []))
    
    # Auto-grouping logic
    if not trend_components and not season_components:
        if primary_period is not None and primary_period > 0:
            dom_freqs = [_dominant_frequency(rc, fs=fs) for rc in rc_list]
            f0 = 1.0 / primary_period
            tol = float(cfg.get("season_freq_tol_ratio", 0.25)) * f0
            low_freq_threshold = float(cfg.get("trend_freq_threshold", f0 / 4.0 if f0 else 0.05))

            for idx, f_dom in enumerate(dom_freqs):
                if f_dom <= max(low_freq_threshold, 1e-8):
                    trend_components.append(idx)
                elif f0 > 0 and abs(f_dom - f0) <= max(tol, 1e-8):
                    season_components.append(idx)
            
            # Fallback if empty
            if not trend_components and num_rc >= 1:
                trend_components.append(0)
            if not season_components:
                for idx in range(num_rc):
                    if idx not in trend_components:
                        season_components.append(idx)
                        break
        else:
            # Default heuristic
            if num_rc >= 1: trend_components.append(0)
            if num_rc >= 2: trend_components.append(1)
            if num_rc >= 4: season_components.extend([2, 3])
            elif num_rc >= 3: season_components.append(2)

    trend = _sum_components(rc_list, trend_components, T)
    season = _sum_components(rc_list, season_components, T)
    residual = y_arr - trend - season

    return finalize_result(
        DecompResult(
            trend=trend,
            season=season,
            residual=residual,
            meta={
                "method": "SSA",
                "window": window,
                "rank": rank,
                "trend_components": trend_components,
                "season_components": season_components
            }
        ),
        method="SSA",
        runtime=runtime,
        backend_used="python",
        started_at=started_at,
    )
