"""Benchmark configuration for TSComp v1.0.0 runbook."""

from __future__ import annotations

from typing import Dict, List, Sequence

BENCHMARK_VERSION = "1.0.0"

SUITES: Dict[str, List[str]] = {
    "core": [
        "trend_only_linear",
        "trend_plus_single_sine",
        "poly_trend_multi_harmonic",
        "logistic_trend_multi_seasonal",
        "rw_trend_freq_drifting_cycle",
        "piecewise_trend_regime_cycle_with_events",
    ],
    "full": [
        "trend_only_linear",
        "trend_plus_single_sine",
        "poly_trend_multi_harmonic",
        "logistic_trend_multi_seasonal",
        "rw_trend_freq_drifting_cycle",
        "piecewise_trend_regime_cycle_with_events",
    ],
}

SCENARIO_TIER: Dict[str, int] = {
    "trend_only_linear": 1,
    "trend_plus_single_sine": 1,
    "poly_trend_multi_harmonic": 2,
    "logistic_trend_multi_seasonal": 2,
    "rw_trend_freq_drifting_cycle": 3,
    "piecewise_trend_regime_cycle_with_events": 3,
}

# Protocol periods for injection (length=512, dt=1.0).
SCENARIO_PERIODS: Dict[str, List[int]] = {
    "trend_only_linear": [50],
    "trend_plus_single_sine": [50],
    "poly_trend_multi_harmonic": [48],
    "logistic_trend_multi_seasonal": [24, 168],
    "rw_trend_freq_drifting_cycle": [50],
    "piecewise_trend_regime_cycle_with_events": [40, 65],
}

CORE_METHODS: List[str] = [
    "stl",
    "mstl",
    "ssa",
    "emd",
    "ceemdan",
    "vmd",
    "wavelet",
]

DEFAULT_METHOD_CONFIGS: Dict[str, Dict[str, object]] = {
    "stl": {"period": None},
    "mstl": {"periods": None},
    "robuststl": {"period": None},
    "ssa": {"window": None, "rank": 10, "primary_period": None},
    "emd": {"primary_period": None},
    "ceemdan": {"primary_period": None},
    "vmd": {
        "K": None,  # v1.1.0: auto-calculated from periods (None triggers dynamic default)
        "alpha": 300.0,  # v1.1.0: reduced from 2000 for better mode separation
        "tau": 0.0,
        "DC": 0,
        "init": 1,
        "tol": 1e-7,
        "seasonal_num_modes": 1,
        "primary_period": None,
    },
    "wavelet": {"wavelet": "db4", "level": None},
    "ma_baseline": {"trend_window": None, "season_period": None},
    "dr_ts_reg": {
        "lambda_T": 5.0,  # v1.1.0: reduced from 100 to prevent over-smoothing
        "lambda_S": 50.0,
        "lambda_R": 0.1,
        "period": None,
    },
    "dr_ts_ae": {
        "model_path": None,
        "latent_dim": 16,
        "hidden_channels": [32, 64],
        "kernel_size": 7,
        "alpha_T": 10.0,
        "alpha_S": 5.0,
        "n_epochs": 50,
        "device": "cpu",
        "cache_model": True,
        # WARNING: ORACLE method - trains on test data
    },
    "sl_lib": {
        "library_size": 500,
        "n_trend_bases": 200,
        "n_seasonal_bases": 300,
        "n_candidates": 100,  # v1.1.0: increased from 50
        "sparsity_lambda": 0.001,  # v1.1.0: reduced from 0.01
        "max_poly_degree": 5,
        "min_period": 4,
        "max_period": 128,
    },
}


def list_suites() -> List[str]:
    return sorted(SUITES.keys())


def get_suite(suite: str) -> List[str]:
    key = suite.strip().lower()
    if key not in SUITES:
        raise ValueError(f"Unknown suite '{suite}'. Available: {list_suites()}")
    return list(SUITES[key])


def normalize_methods(methods: Sequence[str]) -> List[str]:
    return [m.strip().lower() for m in methods if m and m.strip()]


def resolve_methods(methods: str | Sequence[str]) -> List[str]:
    if isinstance(methods, str):
        raw = methods.strip().lower()
        if raw in {"core", "official"}:
            return list(CORE_METHODS)
        if raw in {"all", "full"}:
            return sorted(DEFAULT_METHOD_CONFIGS.keys())
        return normalize_methods(raw.split(","))
    return normalize_methods(methods)


def normalize_periods(periods: Sequence[int], length: int) -> List[int]:
    cleaned: List[int] = []
    max_period = max(2, length // 2)
    for val in periods:
        try:
            p = int(round(float(val)))
        except (TypeError, ValueError):
            continue
        p = max(2, min(p, max_period))
        if p not in cleaned:
            cleaned.append(p)
    return cleaned


def select_primary_period(periods: Sequence[int]) -> int | None:
    for val in periods:
        if val is None:
            continue
        try:
            p = int(round(float(val)))
        except (TypeError, ValueError):
            continue
        if p >= 2:
            return p
    return None
