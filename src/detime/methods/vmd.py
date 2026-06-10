from typing import Dict, Any, List, Optional
from time import perf_counter

import numpy as np

from .._native import invoke_native
from ..backends import finalize_result, resolve_backend, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry
from .utils import dominant_frequency

try:
    from vmdpy import VMD
    _HAS_VMD = True
    _VMD_IMPORT_ERROR = None
except Exception as exc:
    _HAS_VMD = False
    _VMD_IMPORT_ERROR = exc

def select_seasonal_modes(
    freqs: np.ndarray,
    primary_freq: Optional[float],
    num_modes: int,
) -> List[int]:
    if primary_freq and primary_freq > 0:
        order = np.argsort(np.abs(freqs - primary_freq))
    else:
        order = np.argsort(-freqs)  # choose higher-frequency modes if no hint
    selected = []
    for idx in order:
        idx_val = int(np.asarray(idx).ravel()[0])
        if idx_val not in selected:
            selected.append(idx_val)
        if len(selected) >= max(1, num_modes):
            break
    return selected


def _run_vmd_backend(
    y: np.ndarray,
    *,
    cfg: Dict[str, Any],
    backend: str,
    seed: int | None,
) -> tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    periods = cfg.get("periods", [])
    primary_period = cfg.get("primary_period")
    if not periods and primary_period:
        periods = [primary_period]
    n_periods = max(1, len(periods)) if periods else 1
    default_K = max(5, 2 * n_periods + 2)

    K = int(cfg.get("K", default_K))
    alpha = float(cfg.get("alpha", 300.0))
    tau = float(cfg.get("tau", 0.0))
    DC = int(cfg.get("DC", 0))
    init = int(cfg.get("init", 1))
    tol = float(cfg.get("tol", 1e-7))

    if backend == "native":
        payload = invoke_native(
            "vmd_decompose",
            np.asarray(y, dtype=float).ravel(),
            alpha=alpha,
            tau=tau,
            K=K,
            DC=DC,
            init=init,
            tol=tol,
            max_iter=int(cfg.get("max_iter", 500)),
            seed=42 if seed is None else int(seed),
        )
        modes = np.asarray(payload["modes"], dtype=float)
        omega = np.asarray(payload["omega"], dtype=float)
        meta = dict(payload.get("meta", {}) or {})
        return modes, omega, meta

    if not _HAS_VMD:
        raise ImportError("vmdpy is required for VMD decomposition.") from _VMD_IMPORT_ERROR

    modes, _, omega = VMD(y, alpha, tau, K, DC, init, tol)
    return np.asarray(modes, dtype=float), np.asarray(omega, dtype=float), {}


def _assemble_vmd_result(
    modes: np.ndarray,
    omega: np.ndarray,
    *,
    cfg: Dict[str, Any],
    backend_meta: Dict[str, Any],
) -> DecompResult:
    modes = np.asarray(modes, dtype=float)
    if modes.ndim == 1:
        modes = modes[np.newaxis, :]
    omega = np.asarray(omega, dtype=float)
    if omega.ndim == 2:
        omega = omega[-1]

    fs = float(cfg.get("fs", 1.0))
    scale = fs / (2 * np.pi) if fs > 0 else 1.0
    freqs = np.abs(omega) * scale
    dom_freqs = np.array([dominant_frequency(mode, fs) for mode in modes])

    primary_period = cfg.get("primary_period")
    primary_freq = 1.0 / float(primary_period) if primary_period else None

    freq_basis = dom_freqs if np.all(np.isfinite(dom_freqs)) and dom_freqs.any() else freqs

    trend_cutoff = cfg.get(
        "trend_freq_max",
        primary_freq / 5.0 if primary_freq else max(float(np.min(freq_basis)) * 1.5, 0.01),
    )
    trend_mask = freq_basis <= max(trend_cutoff, 1e-6)
    if not trend_mask.any():
        trend_mask[np.argmin(freq_basis)] = True
    trend_indices = np.where(trend_mask)[0].tolist()

    seasonal_num = int(cfg.get("seasonal_num_modes", 1))
    seasonal_indices = select_seasonal_modes(freq_basis, primary_freq, num_modes=seasonal_num)
    seasonal_indices = [idx for idx in seasonal_indices if idx not in trend_indices]
    if not seasonal_indices:
        alt = np.argsort(freqs)[::-1]
        for idx in alt:
            if idx not in trend_indices:
                seasonal_indices.append(int(idx))
            if len(seasonal_indices) >= seasonal_num:
                break

    season_mask = np.zeros(len(freqs), dtype=bool)
    for idx in seasonal_indices:
        season_mask[idx] = True
    
    season = modes[season_mask].sum(axis=0) if seasonal_indices else np.zeros_like(modes[0])
    noise_mask = ~(trend_mask | season_mask)
    residual = modes[noise_mask].sum(axis=0) if noise_mask.any() else np.zeros_like(season)
    # v1.1.0: Direct trend extraction from low-freq modes (not subtraction)
    trend = modes[trend_mask].sum(axis=0) if trend_mask.any() else np.zeros_like(season)
    
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components={"modes": modes},
        meta={
            "center_frequencies": freqs.tolist(),
            "dominant_frequencies": dom_freqs.tolist(),
            "trend_index": trend_indices,
            "season_indices": seasonal_indices,
            **backend_meta,
            "method": "VMD",
        }
    )


@MethodRegistry.register("VMD")
def vmd_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    backend = resolve_backend("VMD", runtime, native_methods=("vmd_decompose",))
    y_arr = np.asarray(y, dtype=float).ravel()
    modes, omega, backend_meta = _run_vmd_backend(
        y_arr,
        cfg=cfg,
        backend=backend,
        seed=runtime.seed,
    )
    result = _assemble_vmd_result(modes, omega, cfg=cfg, backend_meta=backend_meta)
    return finalize_result(
        result,
        method="VMD",
        runtime=runtime,
        backend_used=backend,
        started_at=started_at,
    )
