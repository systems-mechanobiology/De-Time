"""
Core synthetic time-series generator.

This module implements the configuration dataclass plus component builders for
trend, seasonal/cycle, noise, and events. The main entry point is
`generate_series`, which returns all components for downstream benchmarking.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class SeriesConfig:
    """Configuration describing a single synthetic time-series scenario."""

    length: int = 512
    dt: float = 1.0
    trend_type: str = "none"
    trend_params: Dict[str, Any] = field(default_factory=dict)
    cycle_types: List[str] = field(default_factory=list)
    cycle_params_list: List[Dict[str, Any]] = field(default_factory=list)
    noise_type: str = "white"
    noise_params: Dict[str, Any] = field(default_factory=dict)
    event_type: str = "none"
    event_params: Dict[str, Any] = field(default_factory=dict)
    snr_level: str = "medium"
    random_seed: Optional[int] = None


def make_time_axis(length: int, dt: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return time indices `t` and normalized time `u` in [0, 1].

    Args:
        length: Number of time steps.
        dt: Sampling interval.

    Returns:
        Tuple of (t, u) arrays with shape `(length,)`.
    """

    t = np.arange(length, dtype=float) * dt
    u = np.linspace(0.0, 1.0, length)
    return t, u


def _center_and_scale(x: np.ndarray, target_amp: float = 1.0) -> np.ndarray:
    """Center component and scale to target amplitude (max abs)."""

    if not np.any(x):
        return np.zeros_like(x)
    centered = x - np.mean(x)
    max_abs = np.max(np.abs(centered))
    if max_abs < 1e-12:
        return np.zeros_like(centered)
    return centered * (target_amp / max_abs)


def _moving_average(x: np.ndarray, window: int) -> np.ndarray:
    """Simple moving average with same-length output."""

    window = max(1, int(window))
    if window == 1:
        return x
    kernel = np.ones(window) / window
    return np.convolve(x, kernel, mode="same")


def make_trend(
    t: np.ndarray,
    u: np.ndarray,
    trend_type: str,
    params: Dict[str, Any],
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Generate trend component T(t) according to `trend_type`.

    Supported trend_type:
      - "none"
      - "linear"
      - "poly"
      - "exp"
      - "logistic"
      - "piecewise"
      - "rw_smooth"
    """

    trend_type = (trend_type or "none").lower()
    params = dict(params or {})
    length = len(t)

    if trend_type == "none":
        return np.zeros(length), {}

    if trend_type == "linear":
        slope = params.get("slope", np.random.uniform(-2.0, 2.0))
        intercept = params.get("intercept", 0.0)
        raw = slope * (u - 0.5) + intercept
        amplitude = params.get("amplitude", 1.0)
        return _center_and_scale(raw, amplitude), {
            "slope": slope,
            "intercept": intercept,
            "amplitude": amplitude,
        }

    if trend_type == "poly":
        degree = int(params.get("degree", 2))
        coeffs = params.get("coeffs")
        if coeffs is None:
            coeffs = np.random.uniform(-1.0, 1.0, degree + 1)
        raw = np.polyval(coeffs, u * 2 - 1)
        amplitude = params.get("amplitude", 1.0)
        return _center_and_scale(raw, amplitude), {
            "degree": degree,
            "coeffs": list(np.asarray(coeffs).tolist()),
            "amplitude": amplitude,
        }

    if trend_type == "exp":
        alpha = params.get("alpha", 0.5)
        beta = params.get("beta", 2.0)
        raw = alpha * np.exp(beta * (u - 0.5))
        amplitude = params.get("amplitude", 1.0)
        return _center_and_scale(raw, amplitude), {
            "alpha": alpha,
            "beta": beta,
            "amplitude": amplitude,
        }

    if trend_type == "logistic":
        K = params.get("K", 1.0)
        r = params.get("r", 10.0)
        u0 = params.get("u0", 0.5)
        raw = K / (1.0 + np.exp(-r * (u - u0)))
        amplitude = params.get("amplitude", 1.0)
        return _center_and_scale(raw, amplitude), {
            "K": K,
            "r": r,
            "u0": u0,
            "amplitude": amplitude,
        }

    if trend_type == "piecewise":
        num_breaks = params.get("num_breaks", np.random.randint(1, 3))
        breakpoints = params.get(
            "breakpoints",
            sorted(np.random.uniform(0.2, 0.8, num_breaks)),
        )
        slopes = params.get(
            "slopes",
            np.random.uniform(-2.0, 2.0, len(breakpoints) + 1),
        )
        values = np.zeros_like(u)
        last_u = 0.0
        value = 0.0
        bp_iter = breakpoints + [1.0]
        for idx, bp in enumerate(bp_iter):
            mask = (u >= last_u) & (u <= bp)
            interval_u = u[mask] - last_u
            values[mask] = value + slopes[idx] * interval_u
            if interval_u.size:
                value = values[mask][-1]
            last_u = bp
        amplitude = params.get("amplitude", 1.0)
        return _center_and_scale(values, amplitude), {
            "breakpoints": breakpoints,
            "slopes": list(np.asarray(slopes).tolist()),
            "amplitude": amplitude,
        }

    if trend_type == "rw_smooth":
        step_scale = params.get("step_scale", 0.3)
        smooth_window = params.get("smooth_window", length // 20 or 5)
        increments = np.random.normal(0.0, step_scale, length)
        raw = np.cumsum(increments)
        smooth = _moving_average(raw, smooth_window)
        amplitude = params.get("amplitude", 1.0)
        return _center_and_scale(smooth, amplitude), {
            "step_scale": step_scale,
            "smooth_window": smooth_window,
            "amplitude": amplitude,
        }

    raise ValueError(f"Unsupported trend_type '{trend_type}'.")


def make_cycle(
    t: np.ndarray,
    u: np.ndarray,
    cycle_type: str,
    params: Dict[str, Any],
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Generate a single cycle component S(t) for a given cycle_type.

    Supported cycle_type:
      - "single_sine"
      - "multi_harmonic"
      - "sawtooth"
      - "square"
      - "multi_seasonal"
      - "amp_modulated"
      - "freq_drifting"
      - "regime_cycle"
    """

    length = len(t)
    cycle_type = (cycle_type or "single_sine").lower()
    params = dict(params or {})

    def _default_period() -> float:
        return params.get("period", np.random.uniform(20.0, 80.0))

    if cycle_type == "single_sine":
        period = _default_period()
        amplitude = params.get("amplitude", 1.0)
        phase = params.get("phase", np.random.uniform(0, 2 * np.pi))
        comp = amplitude * np.sin(2 * np.pi * t / period + phase)
        return comp, {"period": period, "amplitude": amplitude, "phase": phase}

    if cycle_type == "multi_harmonic":
        base_period = params.get("base_period", np.random.uniform(30.0, 60.0))
        harmonics = int(params.get("harmonics", 3))
        amplitude = params.get("amplitude", 1.0)
        coeffs = params.get("coeffs", np.random.uniform(0.3, 1.0, harmonics))
        comp = np.zeros(length)
        for idx in range(1, harmonics + 1):
            comp += coeffs[idx - 1] * np.sin(2 * np.pi * idx * t / base_period)
        comp = _center_and_scale(comp, amplitude)
        return comp, {
            "base_period": base_period,
            "harmonics": harmonics,
            "coeffs": list(np.asarray(coeffs).tolist()),
            "amplitude": amplitude,
        }

    if cycle_type == "sawtooth":
        period = _default_period()
        amplitude = params.get("amplitude", 1.0)
        saw = 2 * ((t / period) % 1) - 1
        return amplitude * saw, {"period": period, "amplitude": amplitude}

    if cycle_type == "square":
        period = _default_period()
        amplitude = params.get("amplitude", 1.0)
        square = np.sign(np.sin(2 * np.pi * t / period))
        return amplitude * square, {"period": period, "amplitude": amplitude}

    if cycle_type == "multi_seasonal":
        periods = params.get(
            "periods",
            [np.random.uniform(20.0, 40.0), np.random.uniform(60.0, 120.0)],
        )
        amplitudes = params.get("amplitudes", [0.7, 0.5])
        comp = np.zeros(length)
        used_periods: List[float] = []
        used_amplitudes: List[float] = []
        for per, amp in zip(periods, amplitudes):
            comp += amp * np.sin(2 * np.pi * t / per)
            used_periods.append(per)
            used_amplitudes.append(amp)
        return comp, {"periods": used_periods, "amplitudes": used_amplitudes}

    if cycle_type == "amp_modulated":
        carrier_period = params.get("carrier_period", _default_period())
        amp0 = params.get("amp0", 0.5)
        amp1 = params.get("amp1", 1.5)
        modulation = amp0 + (amp1 - amp0) * u
        comp = modulation * np.sin(2 * np.pi * t / carrier_period)
        return comp, {
            "carrier_period": carrier_period,
            "amp0": amp0,
            "amp1": amp1,
        }

    if cycle_type == "freq_drifting":
        period0 = params.get("period0", np.random.uniform(30.0, 70.0))
        delta = params.get("delta", np.random.uniform(-15.0, 15.0))
        amplitude = params.get("amplitude", 1.0)
        inst_period = period0 + delta * u
        inst_freq = 1.0 / np.maximum(inst_period, 1e-3)
        dt = t[1] - t[0] if len(t) > 1 else 1.0
        phase = 2 * np.pi * np.cumsum(inst_freq) * dt
        comp = amplitude * np.sin(phase)
        return comp, {
            "period0": period0,
            "delta": delta,
            "amplitude": amplitude,
        }

    if cycle_type == "regime_cycle":
        split = params.get("split", 0.5)
        amp_a = params.get("amp_a", 1.0)
        amp_b = params.get("amp_b", 0.4)
        per_a = params.get("period_a", np.random.uniform(25.0, 40.0))
        per_b = params.get("period_b", np.random.uniform(50.0, 80.0))
        comp = np.zeros(length)
        split_idx = int(length * split)
        comp[:split_idx] = amp_a * np.sin(2 * np.pi * t[:split_idx] / per_a)
        comp[split_idx:] = amp_b * np.sin(2 * np.pi * t[split_idx:] / per_b)
        return comp, {
            "split": split,
            "amp_a": amp_a,
            "amp_b": amp_b,
            "period_a": per_a,
            "period_b": per_b,
        }

    raise ValueError(f"Unsupported cycle_type '{cycle_type}'.")


def make_all_cycles(
    t: np.ndarray,
    u: np.ndarray,
    cycle_types: Sequence[str],
    cycle_params_list: Sequence[Dict[str, Any]],
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """Sum multiple cycle components, returning the aggregate and metadata."""

    cycle_types = list(cycle_types or [])
    cycle_params_list = list(cycle_params_list or [])
    if cycle_types and len(cycle_types) != len(cycle_params_list):
        raise ValueError("cycle_types and cycle_params_list must align in length.")

    if not cycle_types:
        return np.zeros(len(t)), []

    total = np.zeros(len(t))
    details: List[Dict[str, Any]] = []
    for c_type, c_params in zip(cycle_types, cycle_params_list):
        comp, used = make_cycle(t, u, c_type, c_params)
        total += comp
        details.append({"type": c_type, "params": used})
    return total, details


def make_noise(
    length: int,
    noise_type: str,
    params: Dict[str, Any],
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Generate noise sequence eps_t.

    Supported noise_type:
      - "none"
      - "white"
      - "ar1"
      - "arma"
      - "garch_like"
      - "bursty"
    """

    noise_type = (noise_type or "white").lower()
    params = dict(params or {})

    if noise_type == "none":
        return np.zeros(length), {}

    if noise_type == "white":
        sigma = params.get("sigma", 0.5)
        eps = np.random.normal(0.0, sigma, length)
        return eps, {"sigma": sigma}

    if noise_type == "ar1":
        phi = params.get("phi", 0.6)
        sigma = params.get("sigma", 0.5)
        eps = np.zeros(length)
        innovations = np.random.normal(0.0, sigma, length)
        for i in range(1, length):
            eps[i] = phi * eps[i - 1] + innovations[i]
        return eps, {"phi": phi, "sigma": sigma}

    if noise_type == "arma":
        phi = params.get("phi", 0.5)
        theta = params.get("theta", 0.4)
        sigma = params.get("sigma", 0.4)
        eps = np.zeros(length)
        innovations = np.random.normal(0.0, sigma, length)
        for i in range(1, length):
            eps[i] = phi * eps[i - 1] + innovations[i] + theta * innovations[i - 1]
        return eps, {"phi": phi, "theta": theta, "sigma": sigma}

    if noise_type == "garch_like":
        omega = params.get("omega", 0.1)
        alpha = params.get("alpha", 0.3)
        beta = params.get("beta", 0.5)
        sigma = np.zeros(length)
        eps = np.zeros(length)
        sigma[0] = math.sqrt(omega / (1 - alpha - beta + 1e-6))
        for i in range(1, length):
            sigma[i] = math.sqrt(
                omega + alpha * eps[i - 1] ** 2 + beta * sigma[i - 1] ** 2
            )
            eps[i] = sigma[i] * np.random.normal()
        return eps, {"omega": omega, "alpha": alpha, "beta": beta}

    if noise_type == "bursty":
        sigma = params.get("sigma", 0.3)
        burst_sigma = params.get("burst_sigma", 1.5)
        num_bursts = params.get("num_bursts", max(1, length // 100))
        burst_len = params.get("burst_len", max(3, length // 50))
        eps = np.random.normal(0.0, sigma, length)
        for _ in range(num_bursts):
            start = np.random.randint(0, length - burst_len + 1)
            eps[start : start + burst_len] += np.random.normal(
                0.0, burst_sigma, burst_len
            )
        return eps, {
            "sigma": sigma,
            "burst_sigma": burst_sigma,
            "num_bursts": num_bursts,
            "burst_len": burst_len,
        }

    raise ValueError(f"Unsupported noise_type '{noise_type}'.")


def make_events(
    length: int,
    event_type: str,
    params: Dict[str, Any],
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Generate event component E(t), e.g. level shifts and spikes.

    Supported event_type:
      - "none"
      - "level_shift"
      - "spikes"
      - "mixed"
    """

    event_type = (event_type or "none").lower()
    params = dict(params or {})

    if event_type == "none":
        return np.zeros(length), {}

    events = np.zeros(length)
    shift_points_used: List[int] = []
    spike_idx_used: List[int] = []

    if event_type in {"level_shift", "mixed"}:
        num_shifts = params.get("num_shifts", 1)
        shift_magnitude = params.get("shift_magnitude", 1.0)
        points = params.get("shift_points")
        if points is None:
            start = max(1, length // 4)
            end = max(start + 1, length - length // 4)
            candidate = np.arange(start, end)
            count = min(num_shifts, len(candidate))
            if count > 0:
                points = sorted(
                    np.random.choice(candidate, count, replace=False).tolist()
                )
            else:
                points = []
        shift_points_used = list(points)
        for idx, point in enumerate(points):
            events[point:] += shift_magnitude * (idx + 1)

    if event_type in {"spikes", "mixed"}:
        num_spikes = params.get("num_spikes", max(1, length // 40))
        spike_magnitude = params.get("spike_magnitude", 2.5)
        spike_idx = params.get("spike_idx")
        if spike_idx is None:
            count = min(num_spikes, length)
            if count > 0:
                spike_idx = np.random.choice(length, count, replace=False).tolist()
            else:
                spike_idx = []
        spike_idx_used = list(spike_idx)
        if spike_idx:
            events[spike_idx] += spike_magnitude * np.random.choice(
                [-1, 1], len(spike_idx)
            )

    used_params = {
        k: v
        for k, v in {
            "num_shifts": params.get("num_shifts", len(shift_points_used)),
            "shift_magnitude": params.get("shift_magnitude"),
            "shift_points": shift_points_used,
            "num_spikes": params.get("num_spikes", len(spike_idx_used)),
            "spike_magnitude": params.get("spike_magnitude"),
            "spike_idx": spike_idx_used,
        }.items()
        if v is not None
    }

    return events, used_params


def scale_noise_to_snr(
    signal: np.ndarray,
    noise: np.ndarray,
    snr_level: str = "medium",
) -> np.ndarray:
    """
    Rescale noise to achieve a rough SNR level ("low", "medium", "high").
    SNR here is defined as signal_rms / noise_rms.
    """

    snr_targets = {"high": 5.0, "medium": 2.0, "low": 1.0}
    target = snr_targets.get((snr_level or "medium").lower(), 2.0)

    signal_rms = np.sqrt(np.mean(signal**2)) if np.any(signal) else 0.0
    noise_rms = np.sqrt(np.mean(noise**2)) if np.any(noise) else 0.0

    if noise_rms == 0.0:
        return np.zeros_like(noise)

    if signal_rms == 0.0:
        return noise

    desired_noise_rms = signal_rms / target
    scale = desired_noise_rms / noise_rms
    return noise * scale


def generate_series(config: SeriesConfig) -> Dict[str, Any]:
    """
    Generate a synthetic time series with components y = T + S + E + eps.

    Args:
        config: Series configuration.

    Returns:
        Dict containing arrays for the components and metadata.
    """

    if config.random_seed is not None:
        np.random.seed(config.random_seed)

    t, u = make_time_axis(config.length, config.dt)

    trend, trend_info = make_trend(t, u, config.trend_type, config.trend_params)

    cycle_types = list(config.cycle_types or [])
    cycle_params_list = list(config.cycle_params_list or [])
    if len(cycle_params_list) < len(cycle_types):
        cycle_params_list.extend(
            {} for _ in range(len(cycle_types) - len(cycle_params_list))
        )
    elif len(cycle_params_list) > len(cycle_types):
        cycle_params_list = cycle_params_list[: len(cycle_types)]

    cycles, cycle_info = make_all_cycles(
        t,
        u,
        cycle_types,
        cycle_params_list,
    )
    events, event_info = make_events(
        config.length, config.event_type, config.event_params
    )
    noise, noise_info = make_noise(
        config.length, config.noise_type, config.noise_params
    )

    clean = trend + cycles + events
    noise_scaled = scale_noise_to_snr(clean, noise, config.snr_level)
    y = clean + noise_scaled

    meta = {
        "config": asdict(config),
        "trend": {"type": config.trend_type, "params": trend_info},
        "cycles": cycle_info,
        "events": {"type": config.event_type, "params": event_info},
        "noise": {"type": config.noise_type, "params": noise_info},
        "snr_level": config.snr_level,
    }

    return {
        "t": t,
        "y": y,
        "trend": trend,
        "season": cycles,
        "events": events,
        "noise": noise_scaled,
        "clean": clean,
        "meta": meta,
    }

