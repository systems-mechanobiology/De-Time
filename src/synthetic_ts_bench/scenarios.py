"""Scenario presets and dataset utilities for synthetic_ts_bench."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from .generator import SeriesConfig, generate_series

SCENARIO_REGISTRY: Dict[str, Callable[[int, Optional[int]], SeriesConfig]] = {}


def register_scenario(name: str) -> Callable[[Callable[[int, Optional[int]], SeriesConfig]], Callable[[int, Optional[int]], SeriesConfig]]:
    """
    Decorator to register a scenario factory under a given name.
    """

    def decorator(
        fn: Callable[[int, Optional[int]], SeriesConfig]
    ) -> Callable[[int, Optional[int]], SeriesConfig]:
        SCENARIO_REGISTRY[name] = fn
        return fn

    return decorator


def make_scenario(
    name: str,
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    """
    Create a SeriesConfig for a named scenario.
    """

    if name not in SCENARIO_REGISTRY:
        raise ValueError(
            f"Unknown scenario name: {name}. "
            f"Available: {sorted(SCENARIO_REGISTRY.keys())}"
        )
    return SCENARIO_REGISTRY[name](length, random_seed)


def list_scenarios() -> List[str]:
    """Return a sorted list of available scenario names."""

    return sorted(SCENARIO_REGISTRY.keys())


@register_scenario("trend_only_linear")
def trend_only_linear(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    return SeriesConfig(
        length=length,
        trend_type="linear",
        cycle_types=[],
        cycle_params_list=[],
        noise_type="white",
        noise_params={"sigma": 0.1},
        event_type="none",
        snr_level="high",
        random_seed=random_seed,
    )


@register_scenario("trend_plus_single_sine")
def trend_plus_single_sine(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    return SeriesConfig(
        length=length,
        trend_type="poly",
        trend_params={"degree": 2},
        cycle_types=["single_sine"],
        cycle_params_list=[{"period": 50, "amplitude": 1.0}],
        noise_type="white",
        noise_params={"sigma": 0.3},
        event_type="none",
        snr_level="medium",
        random_seed=random_seed,
    )


@register_scenario("poly_trend_plus_multi_seasonal")
def poly_trend_plus_multi_seasonal(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    return SeriesConfig(
        length=length,
        trend_type="poly",
        trend_params={"degree": 3},
        cycle_types=["multi_seasonal"],
        cycle_params_list=[
            {
                "periods": [24, 64],
                "amplitudes": [0.8, 0.4],
            }
        ],
        noise_type="arma",
        noise_params={"phi": 0.4, "theta": 0.3, "sigma": 0.2},
        event_type="level_shift",
        event_params={"num_shifts": 1, "shift_magnitude": 0.8},
        snr_level="medium",
        random_seed=random_seed,
    )


@register_scenario("regime_cycle_piecewise_trend_bursty")
def regime_cycle_piecewise_trend_bursty(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    return SeriesConfig(
        length=length,
        trend_type="piecewise",
        cycle_types=["regime_cycle"],
        cycle_params_list=[{}],
        noise_type="bursty",
        noise_params={"sigma": 0.2, "burst_sigma": 1.0},
        event_type="mixed",
        event_params={"num_spikes": max(1, length // 60)},
        snr_level="low",
        random_seed=random_seed,
    )


@register_scenario("rw_trend_freq_drifting_cycle_low_snr")
def rw_trend_freq_drifting_cycle_low_snr(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    return SeriesConfig(
        length=length,
        trend_type="rw_smooth",
        cycle_types=["freq_drifting"],
        cycle_params_list=[{"period0": 40, "delta": 20}],
        noise_type="garch_like",
        noise_params={"omega": 0.05, "alpha": 0.2, "beta": 0.6},
        event_type="spikes",
        event_params={"num_spikes": max(1, length // 80), "spike_magnitude": 2.0},
        snr_level="low",
        random_seed=random_seed,
    )


@register_scenario("poly_trend_multi_harmonic")
def poly_trend_multi_harmonic(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    """
    Polynomial trend plus multi-harmonic seasonal structure with moderate noise.
    """

    return SeriesConfig(
        length=length,
        trend_type="poly",
        trend_params={"degree": 3},
        cycle_types=["multi_harmonic"],
        cycle_params_list=[
            {
                "base_period": 48,
                "harmonics": 3,
                "amplitude": 1.0,
            }
        ],
        noise_type="white",
        noise_params={"sigma": 0.12},
        event_type="none",
        snr_level="medium",
        random_seed=random_seed,
    )


@register_scenario("logistic_trend_multi_seasonal")
def logistic_trend_multi_seasonal(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    """
    Logistic growth trend combined with multi-seasonal cycles (e.g., daily + weekly).
    """

    return SeriesConfig(
        length=length,
        trend_type="logistic",
        trend_params={"K": 1.0, "r": 8.0, "u0": 0.5, "amplitude": 1.0},
        cycle_types=["multi_seasonal"],
        cycle_params_list=[
            {
                "periods": [24, 168],
                "amplitudes": [0.6, 0.35],
            }
        ],
        noise_type="white",
        noise_params={"sigma": 0.1},
        event_type="none",
        snr_level="medium",
        random_seed=random_seed,
    )


@register_scenario("rw_trend_freq_drifting_cycle")
def rw_trend_freq_drifting_cycle(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    """
    Random-walk-like smooth trend with a drifting-frequency sinusoidal cycle.
    """

    return SeriesConfig(
        length=length,
        trend_type="rw_smooth",
        trend_params={"smooth_window": max(5, length // 30), "step_scale": 0.2},
        cycle_types=["freq_drifting"],
        cycle_params_list=[
            {"period0": 50, "delta": 15, "amplitude": 1.0}
        ],
        noise_type="white",
        noise_params={"sigma": 0.18},
        event_type="none",
        snr_level="medium",
        random_seed=random_seed,
    )


@register_scenario("piecewise_trend_regime_cycle_with_events")
def piecewise_trend_regime_cycle_with_events(
    length: int = 512,
    random_seed: Optional[int] = None,
) -> SeriesConfig:
    """
    Piecewise trend with regime-switching cycles plus mixed events (shifts & spikes).
    """

    return SeriesConfig(
        length=length,
        trend_type="piecewise",
        trend_params={"num_breaks": 2},
        cycle_types=["regime_cycle"],
        cycle_params_list=[
            {
                "split": 0.55,
                "amp_a": 1.0,
                "amp_b": 0.6,
                "period_a": 40,
                "period_b": 65,
            }
        ],
        noise_type="white",
        noise_params={"sigma": 0.12},
        event_type="mixed",
        event_params={
            "num_shifts": 1,
            "shift_magnitude": 0.8,
            "num_spikes": 5,
            "spike_magnitude": 2.0,
        },
        snr_level="medium",
        random_seed=random_seed,
    )


def generate_dataset(
    scenario_names: List[str],
    n_per_scenario: int,
    length: int = 512,
    base_seed: int = 0,
    save_dir: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Generate a dataset of synthetic time series for multiple scenarios.

    Returns a list of series dicts (the same format as generate_series),
    with additional fields in ``meta`` describing the scenario context. If
    ``save_dir`` is provided, each sample is also saved as a ``.npz`` file.
    """

    results: List[Dict[str, Any]] = []
    output_path: Optional[Path] = Path(save_dir) if save_dir else None
    if output_path:
        output_path.mkdir(parents=True, exist_ok=True)

    for scenario_idx, scenario_name in enumerate(scenario_names):
        for sample_idx in range(n_per_scenario):
            seed = base_seed + scenario_idx * n_per_scenario + sample_idx
            cfg = make_scenario(scenario_name, length=length, random_seed=seed)
            series = generate_series(cfg)
            series["meta"]["scenario_name"] = scenario_name
            series["meta"]["index_within_scenario"] = sample_idx
            series["meta"]["global_seed"] = seed
            results.append(series)

            if output_path:
                file_path = output_path / f"{scenario_name}_{sample_idx:04d}.npz"
                np.savez(
                    file_path,
                    t=series["t"],
                    y=series["y"],
                    trend=series["trend"],
                    season=series["season"],
                    events=series["events"],
                    noise=series["noise"],
                    clean=series["clean"],
                    meta=json.dumps(series["meta"]),
                )

    return results
