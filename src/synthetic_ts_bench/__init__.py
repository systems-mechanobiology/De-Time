"""Public API surface for synthetic_ts_bench."""

from .generator import SeriesConfig, generate_series
from .plotting import plot_power_spectrum, plot_series_components
from .scenarios import generate_dataset, list_scenarios, make_scenario
from .decomp_methods import (
    DecompResult,
    DecompConfig,
    DecompMethodName,
    decompose_series,
)
from .decomp_eval import (
    compute_time_domain_metrics,
    compute_freq_metrics,
    compute_event_metrics,
    evaluate_decomposition_on_series,
    evaluate_methods_on_scenarios,
)
from .decomp_plotting import compare_decompositions_on_series

__all__ = [
    "SeriesConfig",
    "generate_series",
    "plot_series_components",
    "plot_power_spectrum",
    "make_scenario",
    "list_scenarios",
    "generate_dataset",
    "DecompResult",
    "DecompConfig",
    "DecompMethodName",
    "decompose_series",
    "compute_time_domain_metrics",
    "compute_freq_metrics",
    "compute_event_metrics",
    "evaluate_decomposition_on_series",
    "evaluate_methods_on_scenarios",
    "compare_decompositions_on_series",
]
