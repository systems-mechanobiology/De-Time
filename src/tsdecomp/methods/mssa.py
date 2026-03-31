from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, List

import numpy as np

from ..backends import finalize_result, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry
from .utils import dominant_frequency

try:
    from sklearn.utils.extmath import randomized_svd

    _HAS_RANDOMIZED_SVD = True
    _RANDOMIZED_SVD_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - optional import path
    randomized_svd = None
    _HAS_RANDOMIZED_SVD = False
    _RANDOMIZED_SVD_IMPORT_ERROR = exc


def _diagonal_averaging(matrix: np.ndarray) -> np.ndarray:
    rows, cols = matrix.shape
    length = rows + cols - 1
    recon = np.zeros(length, dtype=float)
    counts = np.zeros(length, dtype=float)
    for i in range(rows):
        for j in range(cols):
            recon[i + j] += matrix[i, j]
            counts[i + j] += 1.0
    counts[counts == 0.0] = 1.0
    return recon / counts


def _build_mssa_trajectory(y: np.ndarray, window: int) -> np.ndarray:
    length, n_channels = y.shape
    k = length - window + 1
    trajectory = np.empty((window * n_channels, k), dtype=float)
    for channel_idx in range(n_channels):
        offset = channel_idx * window
        channel = y[:, channel_idx]
        for col in range(k):
            trajectory[offset : offset + window, col] = channel[col : col + window]
    return trajectory


def _reconstruct_mode(mode_matrix: np.ndarray, window: int, n_channels: int, length: int) -> np.ndarray:
    mode = np.empty((length, n_channels), dtype=float)
    for channel_idx in range(n_channels):
        start = channel_idx * window
        stop = start + window
        mode[:, channel_idx] = _diagonal_averaging(mode_matrix[start:stop, :])[:length]
    return mode


def _fit_svd(
    trajectory: np.ndarray,
    rank: int,
    speed_mode: str,
    seed: int | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    max_rank = min(rank, trajectory.shape[0], trajectory.shape[1])
    if max_rank <= 0:
        raise ValueError("MSSA rank must be positive.")

    if speed_mode == "fast":
        if not _HAS_RANDOMIZED_SVD:
            raise ImportError(
                "MSSA speed_mode='fast' requires scikit-learn randomized_svd."
            ) from _RANDOMIZED_SVD_IMPORT_ERROR
        n_iter = 5 if max_rank <= 8 else 7
        U, s, Vt = randomized_svd(
            trajectory,
            n_components=max_rank,
            n_iter=n_iter,
            random_state=seed,
        )
        return U, s, Vt

    U, s, Vt = np.linalg.svd(trajectory, full_matrices=False)
    return U[:, :max_rank], s[:max_rank], Vt[:max_rank, :]


def _dominant_frequency_2d(mode: np.ndarray, fs: float) -> float:
    aggregate = np.mean(np.asarray(mode, dtype=float), axis=1)
    return dominant_frequency(aggregate, fs=fs)


def _sum_modes(modes: np.ndarray, indices: List[int], shape: tuple[int, int]) -> np.ndarray:
    if not indices:
        return np.zeros(shape, dtype=float)
    valid = [idx for idx in indices if 0 <= idx < modes.shape[0]]
    if not valid:
        return np.zeros(shape, dtype=float)
    return np.sum(modes[valid, :, :], axis=0)


def _auto_group_modes(
    modes: np.ndarray,
    *,
    fs: float,
    primary_period: float | None,
    trend_components: List[int],
    season_components: List[int],
    cfg: Dict[str, Any],
) -> tuple[List[int], List[int], List[float]]:
    dom_freqs = [_dominant_frequency_2d(mode, fs=fs) for mode in modes]
    if trend_components or season_components:
        return trend_components, season_components, dom_freqs

    num_modes = modes.shape[0]
    if primary_period is not None and primary_period > 0:
        f0 = 1.0 / primary_period
        tol = float(cfg.get("season_freq_tol_ratio", 0.25)) * f0
        low_freq_threshold = float(cfg.get("trend_freq_threshold", f0 / 4.0 if f0 else 0.05))

        for idx, f_dom in enumerate(dom_freqs):
            if f_dom <= max(low_freq_threshold, 1e-8):
                trend_components.append(idx)
            elif f0 > 0 and abs(f_dom - f0) <= max(tol, 1e-8):
                season_components.append(idx)

        if not trend_components and num_modes >= 1:
            trend_components.append(0)
        if not season_components:
            for idx in range(num_modes):
                if idx not in trend_components:
                    season_components.append(idx)
                    break
    else:
        if num_modes >= 1:
            trend_components.append(0)
        if num_modes >= 2:
            trend_components.append(1)
        if num_modes >= 4:
            season_components.extend([2, 3])
        elif num_modes >= 3:
            season_components.append(2)

    return trend_components, season_components, dom_freqs


@MethodRegistry.register("MSSA", input_mode="multivariate")
def mssa_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    if runtime.backend == "native":
        raise RuntimeError("MSSA does not provide a native backend.")
    if runtime.backend == "gpu":
        raise ValueError("MSSA does not provide a GPU backend.")

    y_arr = np.asarray(y, dtype=float)
    if y_arr.ndim != 2:
        raise ValueError("MSSA requires a 2D input array with shape (T, C).")

    length, n_channels = y_arr.shape
    if length < 4:
        raise ValueError("MSSA requires length >= 4.")
    if n_channels < 2:
        raise ValueError("MSSA requires at least two channels.")

    window = int(cfg.get("window", max(4, length // 4)))
    window = min(max(2, window), length - 1)
    rank = int(cfg.get("rank", min(10, window * n_channels, length - window + 1)))
    rank = max(1, min(rank, window * n_channels, length - window + 1))

    fs = float(cfg.get("fs", 1.0))
    primary_period = cfg.get("primary_period")
    primary_period = float(primary_period) if primary_period not in (None, 0) else None

    trajectory = _build_mssa_trajectory(y_arr, window=window)
    U, s, Vt = _fit_svd(trajectory, rank=rank, speed_mode=runtime.speed_mode, seed=runtime.seed)

    modes = []
    for idx in range(len(s)):
        mode_matrix = np.outer(U[:, idx], s[idx] * Vt[idx, :])
        modes.append(_reconstruct_mode(mode_matrix, window=window, n_channels=n_channels, length=length))

    if modes:
        mode_array = np.stack(modes, axis=0)
    else:
        mode_array = np.zeros((0, length, n_channels), dtype=float)

    trend_components = list(cfg.get("trend_components", []))
    season_components = list(cfg.get("season_components", []))
    trend_components, season_components, dom_freqs = _auto_group_modes(
        mode_array,
        fs=fs,
        primary_period=primary_period,
        trend_components=trend_components,
        season_components=season_components,
        cfg=cfg,
    )

    trend = _sum_modes(mode_array, trend_components, y_arr.shape)
    season = _sum_modes(mode_array, season_components, y_arr.shape)
    residual = y_arr - trend - season

    result = DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components={"modes": mode_array},
        meta={
            "method": "MSSA",
            "window": window,
            "rank": rank,
            "n_channels": n_channels,
            "singular_values": [float(val) for val in s.tolist()],
            "trend_components": trend_components,
            "season_components": season_components,
            "dominant_frequencies": dom_freqs,
        },
    )
    return finalize_result(
        result,
        method="MSSA",
        runtime=runtime,
        backend_used="python",
        started_at=started_at,
    )
