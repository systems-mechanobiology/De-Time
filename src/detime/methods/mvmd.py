from __future__ import annotations

from importlib import import_module
from time import perf_counter
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np

from ..backends import finalize_result, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry


def _ensure_multivariate_input(y: np.ndarray, method: str) -> np.ndarray:
    y_arr = np.asarray(y, dtype=float)
    if y_arr.ndim != 2:
        raise ValueError(f"{method} requires a 2D array with shape (time, channels).")
    if y_arr.shape[0] < 4 or y_arr.shape[1] < 2:
        raise ValueError(f"{method} requires at least 4 timesteps and 2 channels.")
    return y_arr


def _dominant_frequency(x: np.ndarray, fs: float = 1.0) -> float:
    arr = np.asarray(x, dtype=float).reshape(-1)
    if arr.size < 4:
        return 0.0
    centered = arr - float(np.mean(arr))
    spectrum = np.abs(np.fft.rfft(centered))
    if spectrum.size <= 1:
        return 0.0
    spectrum[0] = 0.0
    freqs = np.fft.rfftfreq(arr.size, d=1.0 / fs if fs > 0 else 1.0)
    idx = int(np.argmax(spectrum))
    return float(freqs[idx]) if 0 <= idx < freqs.size else 0.0


def _dominant_mode_frequencies(modes: np.ndarray, fs: float) -> np.ndarray:
    freq_list: List[float] = []
    for mode in modes:
        channel_freqs = [_dominant_frequency(mode[:, idx], fs=fs) for idx in range(mode.shape[1])]
        freq_list.append(float(np.mean(channel_freqs)) if channel_freqs else 0.0)
    return np.asarray(freq_list, dtype=float)


def _select_seasonal_modes(
    freqs: np.ndarray,
    primary_freq: float | None,
    num_modes: int,
) -> List[int]:
    if primary_freq and primary_freq > 0:
        order = np.argsort(np.abs(freqs - primary_freq))
    else:
        order = np.argsort(-freqs)
    selected: List[int] = []
    for idx in order:
        idx_val = int(np.asarray(idx).ravel()[0])
        if idx_val not in selected:
            selected.append(idx_val)
        if len(selected) >= max(1, num_modes):
            break
    return selected


def _aggregate_mode_stack(modes: np.ndarray, indices: Sequence[int]) -> np.ndarray:
    valid = [idx for idx in indices if 0 <= idx < modes.shape[0]]
    if not valid:
        return np.zeros_like(modes[0])
    return np.sum(modes[np.asarray(valid, dtype=int)], axis=0)


def _group_multivariate_modes(
    modes: np.ndarray,
    cfg: Dict[str, Any],
    *,
    method: str,
) -> DecompResult:
    fs = float(cfg.get("fs", 1.0))
    dom_freqs = _dominant_mode_frequencies(modes, fs=fs)
    primary_period = cfg.get("primary_period")
    primary_freq = 1.0 / float(primary_period) if primary_period not in (None, 0) else None

    trend_modes = [int(v) for v in cfg.get("trend_modes", cfg.get("trend_imfs", []))]
    season_modes = [int(v) for v in cfg.get("season_modes", cfg.get("season_imfs", []))]

    if not trend_modes and not season_modes:
        if primary_freq and primary_freq > 0:
            tol = float(cfg.get("season_freq_tol_ratio", 0.25)) * primary_freq
            low_thresh = float(cfg.get("trend_freq_threshold", primary_freq / 4.0))
            for idx, freq in enumerate(dom_freqs):
                if freq <= max(low_thresh, 1e-8):
                    trend_modes.append(idx)
                elif abs(freq - primary_freq) <= max(tol, 1e-8):
                    season_modes.append(idx)
            if not trend_modes:
                trend_modes.append(int(np.argmin(dom_freqs)))
            if not season_modes:
                season_modes.extend(_select_seasonal_modes(dom_freqs, primary_freq, int(cfg.get("seasonal_num_modes", 1))))
        else:
            trend_modes.append(int(np.argmin(dom_freqs)))
            season_modes.extend(_select_seasonal_modes(dom_freqs, None, int(cfg.get("seasonal_num_modes", 1))))

    trend_set = set(trend_modes)
    season_modes = [idx for idx in season_modes if idx not in trend_set]
    if not season_modes and modes.shape[0] > 1:
        season_modes = [idx for idx in range(modes.shape[0] - 1, -1, -1) if idx not in trend_set][:1]

    trend = _aggregate_mode_stack(modes, trend_modes)
    season = _aggregate_mode_stack(modes, season_modes)
    residual_indices = [idx for idx in range(modes.shape[0]) if idx not in trend_set and idx not in set(season_modes)]
    residual = _aggregate_mode_stack(modes, residual_indices)
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        components={"modes": np.asarray(modes, dtype=float)},
        meta={
            "method": method,
            "dominant_frequencies": dom_freqs.tolist(),
            "trend_components": list(trend_modes),
            "season_components": list(season_modes),
        },
    )


def _coerce_mode_stack(raw_modes: Any, n_time: int, n_channels: int, label: str) -> np.ndarray:
    modes = np.asarray(raw_modes, dtype=float)
    if modes.ndim != 3:
        raise ValueError(f"{label} backend returned unsupported ndim={modes.ndim}; expected 3D modes.")
    if modes.shape[1:] == (n_time, n_channels):
        return modes
    if modes.shape[1:] == (n_channels, n_time):
        return np.transpose(modes, (0, 2, 1))
    if modes.shape[:2] == (n_channels, n_time):
        return np.transpose(modes, (2, 1, 0))
    if modes.shape[:2] == (n_time, n_channels):
        return np.transpose(modes, (2, 0, 1))
    raise ValueError(
        f"{label} backend returned shape {modes.shape}, which cannot be normalized to (K, T, C)."
    )


def _load_optional_backend(method_name: str):
    candidates = {
        "MVMD": (
            ("pysdkit", "MVMD"),
            ("PySDKit", "MVMD"),
            ("pysdkit._vmd.mvmd", "MVMD"),
        ),
        "MEMD": (
            ("pysdkit", "MEMD"),
            ("PySDKit", "MEMD"),
            ("pysdkit._emd.memd", "MEMD"),
        ),
    }
    last_error: Exception | None = None
    for module_name, attr_name in candidates[method_name]:
        try:
            module = import_module(module_name)
            if hasattr(module, attr_name):
                return getattr(module, attr_name)
        except Exception as exc:  # pragma: no cover - import path depends on optional dep
            last_error = exc
    install_hint = "reinstall De-Time with the `multivar` extra"
    raise ImportError(
        f"{method_name} requires an optional multivariate backend. "
        f"To use it, {install_hint}."
    ) from last_error


def _instantiate_backend(backend_cls: Any, cfg: Dict[str, Any]) -> Any:
    backend_kwargs = {
        key: value
        for key, value in cfg.items()
        if key
        not in {
            "fs",
            "primary_period",
            "trend_modes",
            "season_modes",
            "seasonal_num_modes",
            "season_freq_tol_ratio",
            "trend_freq_threshold",
            "backend",
            "speed_mode",
            "profile",
            "device",
            "n_jobs",
            "seed",
        }
    }
    return backend_cls(**backend_kwargs) if isinstance(backend_cls, type) else backend_cls


def _call_backend(instance: Any, y_arr: np.ndarray, method_name: str) -> Any:
    attempts = (
        ("fit_transform", y_arr),
        ("fit_transform", y_arr.T),
        ("transform", y_arr),
        ("transform", y_arr.T),
        ("decompose", y_arr),
        ("decompose", y_arr.T),
    )
    for attr_name, arg in attempts:
        if hasattr(instance, attr_name):
            fn = getattr(instance, attr_name)
            try:
                return fn(arg)
            except TypeError:
                continue
    if callable(instance):
        for arg in (y_arr, y_arr.T):
            try:
                return instance(arg)
            except TypeError:
                continue
    raise RuntimeError(f"Could not execute the optional backend for {method_name}.")


def _run_backend(method_name: str, y_arr: np.ndarray, cfg: Dict[str, Any]) -> np.ndarray:
    backend_cls = _load_optional_backend(method_name)
    instance = _instantiate_backend(backend_cls, cfg)
    raw = _call_backend(instance, y_arr, method_name)
    if isinstance(raw, dict):
        for key in ("modes", "imfs", "components"):
            if key in raw:
                raw = raw[key]
                break
    elif isinstance(raw, (list, tuple)) and raw:
        raw = raw[0]
    return _coerce_mode_stack(raw, y_arr.shape[0], y_arr.shape[1], method_name)


@MethodRegistry.register("MVMD", input_mode="multivariate")
def mvmd_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    if runtime.backend == "native":
        raise RuntimeError("MVMD does not provide a native backend yet; use backend='python' or 'auto'.")
    if runtime.backend == "gpu":
        raise ValueError("MVMD does not provide a GPU backend.")

    y_arr = _ensure_multivariate_input(y, "MVMD")
    modes = _run_backend("MVMD", y_arr, cfg)
    result = _group_multivariate_modes(modes, cfg, method="MVMD")
    return finalize_result(
        result,
        method="MVMD",
        runtime=runtime,
        backend_used="python",
        started_at=started_at,
    )
