"""Plotting helpers for comparing decomposition methods."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .decomp_methods import (
    DecompConfig,
    DecompMethodName,
    DecompResult,
    decompose_series,
)

METHOD_COLORS: Dict[str, str] = {
    "stl": "tab:blue",
    "mstl": "tab:orange",
    "robuststl": "tab:red",
    "ssa": "tab:green",
    "std": "tab:olive",
    "emd": "tab:purple",
    "ceemdan": "tab:brown",
    "vmd": "tab:pink",
    "wavelet": "tab:cyan",
    "ma_baseline": "tab:gray",
}


def _method_color(method: str) -> str:
    return METHOD_COLORS.get(method.lower(), "tab:gray")


def _chunk_list(values: Sequence[str], size: int) -> Iterable[List[str]]:
    size = max(1, size)
    for i in range(0, len(values), size):
        yield list(values[i : i + size])


def _component_ylim(arrays: List[np.ndarray]) -> Optional[tuple[float, float]]:
    filtered = [np.asarray(arr, dtype=float).ravel() for arr in arrays if arr is not None and np.asarray(arr).size]
    if not filtered:
        return None
    data = np.concatenate(filtered)
    lo, hi = float(np.min(data)), float(np.max(data))
    pad = 0.05 * (hi - lo) if hi > lo else 1.0
    return lo - pad, hi + pad


def compare_decompositions_on_series(
    y: np.ndarray,
    methods: List[Dict[str, Any]],
    title: str = "",
    fs: float = 1.0,
    meta: Optional[Dict[str, Any]] = None,
) -> plt.Figure:
    """
    Plot a side-by-side comparison of multiple decompositions on the same series.
    """

    series = np.asarray(y, dtype=float).reshape(-1)
    if not methods:
        raise ValueError("Provide at least one method to compare.")

    results: List[Dict[str, Any]] = []
    for entry in methods:
        name = entry.get("name")
        if name is None:
            raise ValueError("Each method entry must include a 'name' key.")
        config = entry.get("config")
        label = entry.get("label", name)
        res = decompose_series(series, method=name, config=config, fs=fs, meta=meta)
        results.append({"label": label, "result": res})

    fig, axes = plt.subplots(4, 1, sharex=True, figsize=(10, 8))
    axes[0].plot(series, color="black", label="observed")
    axes[0].set_title("Observed series")
    axes[0].legend(loc="upper right")

    axes[1].set_title("Trend components")
    axes[2].set_title("Seasonal components")
    axes[3].set_title("Residual components")

    for item in results:
        label = item["label"]
        res: DecompResult = item["result"]
        axes[1].plot(res.trend, label=label)
        axes[2].plot(res.season, label=label)
        axes[3].plot(res.residual, label=label)

    for ax in axes[1:]:
        ax.legend(loc="upper right")

    if title:
        fig.suptitle(title)
    axes[-1].set_xlabel("Time index")
    plt.tight_layout()
    return fig


def plot_decomposition_overlays_paginated(
    scenario_name: str,
    observed: np.ndarray,
    true_components: Dict[str, np.ndarray],
    components_by_method: Dict[str, Dict[str, np.ndarray]],
    output_dir: str | Path,
    methods: Optional[List[str]] = None,
    max_methods_per_figure: int = 4,
) -> List[Path]:
    """
    Create paginated overlay plots (observed + T/S/R) for a subset of methods.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    methods = methods or sorted(components_by_method.keys())
    saved_paths: List[Path] = []
    slug = scenario_name.replace(" ", "_")
    for page_idx, chunk in enumerate(_chunk_list(methods, max_methods_per_figure), start=1):
        fig, axes = plt.subplots(4, 1, sharex=True, figsize=(11, 8))
        axes[0].plot(observed, color="black", label="observed")
        axes[0].set_title("Observed series")
        axes[0].legend(loc="upper right")
        components = ["trend", "seasonal", "residual"]
        titles = ["Trend components", "Seasonal components", "Residual components"]

        for ax, comp, title in zip(axes[1:], components, titles):
            ax.set_title(title)
            true_comp = true_components.get(comp)
            if true_comp is not None:
                ax.plot(true_comp, color="black", linewidth=1.6, label="true")

        for method in chunk:
            result = components_by_method.get(method)
            if not result:
                continue
            color = _method_color(method)
            for ax, comp in zip(axes[1:], components):
                comp_data = result.get(comp)
                if comp_data is not None:
                    ax.plot(comp_data, color=color, linewidth=1.0, alpha=0.9, label=method)

        axes[1].legend(loc="upper right", ncol=1, fontsize="small")
        axes[-1].set_xlabel("Time index")
        fig.suptitle(f"Scenario: {scenario_name} – Methods {', '.join(chunk)}", fontsize=14)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        out_path = output_dir / f"decomp_overlay_{slug}_page{page_idx}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        saved_paths.append(out_path)
    return saved_paths


def plot_decomposition_facets(
    scenario_name: str,
    observed: np.ndarray,
    true_components: Dict[str, np.ndarray],
    components_by_method: Dict[str, Dict[str, np.ndarray]],
    output_dir: str | Path,
    methods: Optional[List[str]] = None,
    max_methods_per_page: int = 4,
) -> List[Path]:
    """
    Create per-method facet plots (observed row + method-specific T/S/R rows).
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    methods = methods or sorted(components_by_method.keys())
    saved_paths: List[Path] = []
    slug = scenario_name.replace(" ", "_")

    for page_idx, chunk in enumerate(_chunk_list(methods, max_methods_per_page), start=1):
        n_methods = len(chunk)
        n_rows = 1 + 3 * n_methods
        fig, axes = plt.subplots(n_rows, 1, sharex=True, figsize=(12, 3 + 2.4 * n_methods))

        axes[0].plot(observed, color="black")
        axes[0].set_title("Observed series")

        trend_arrays = [components_by_method[m].get("trend") for m in chunk if m in components_by_method]
        season_arrays = [components_by_method[m].get("seasonal") for m in chunk if m in components_by_method]
        resid_arrays = [components_by_method[m].get("residual") for m in chunk if m in components_by_method]

        trend_ylim = _component_ylim([true_components.get("trend")] + trend_arrays)
        season_ylim = _component_ylim([true_components.get("seasonal")] + season_arrays)
        resid_ylim = _component_ylim([true_components.get("residual")] + resid_arrays)

        for idx, method in enumerate(chunk):
            base_idx = 1 + idx * 3
            result = components_by_method.get(method)
            if not result:
                continue
            color = _method_color(method)

            # Trend
            ax_trend = axes[base_idx]
            if true_components.get("trend") is not None:
                ax_trend.plot(true_components["trend"], color="black", linewidth=1.5, label="true")
            ax_trend.plot(result.get("trend"), color=color, label=method)
            ax_trend.set_ylabel(method)
            ax_trend.set_title(f"Trend – {method}")
            if trend_ylim:
                ax_trend.set_ylim(trend_ylim)

            # Seasonal
            ax_season = axes[base_idx + 1]
            if true_components.get("seasonal") is not None:
                ax_season.plot(true_components["seasonal"], color="black", linewidth=1.5)
            ax_season.plot(result.get("seasonal"), color=color)
            ax_season.set_title(f"Seasonal – {method}")
            if season_ylim:
                ax_season.set_ylim(season_ylim)

            # Residual
            ax_resid = axes[base_idx + 2]
            if true_components.get("residual") is not None:
                ax_resid.plot(true_components["residual"], color="black", linewidth=1.2)
            ax_resid.plot(result.get("residual"), color=color)
            ax_resid.set_title(f"Residual – {method}")
            if resid_ylim:
                ax_resid.set_ylim(resid_ylim)

        axes[-1].set_xlabel("Time index")
        fig.suptitle(f"Scenario: {scenario_name} – methods {', '.join(chunk)}", fontsize=14)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        out_path = output_dir / f"decomp_facets_{slug}_page{page_idx}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        saved_paths.append(out_path)

    return saved_paths


def plot_component_error_timeseries(
    scenario_name: str,
    true_components: Dict[str, np.ndarray],
    components_by_method: Dict[str, Dict[str, np.ndarray]],
    output_dir: str | Path,
    component: str = "trend",
    methods_to_show: Optional[List[str]] = None,
) -> Path:
    """
    Plot absolute error over time for a given component across methods.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    methods = methods_to_show or sorted(components_by_method.keys())
    true_array = true_components.get(component)
    if true_array is None:
        raise ValueError(f"No ground-truth component '{component}' available.")
    true_series = np.asarray(true_array, dtype=float).reshape(-1)

    fig, ax = plt.subplots(figsize=(12, 4))
    for method in methods:
        result = components_by_method.get(method)
        if not result or component not in result:
            continue
        est = np.asarray(result[component], dtype=float).reshape(-1)
        length = min(len(est), len(true_series))
        if length == 0:
            continue
        abs_err = np.abs(est[:length] - true_series[:length])
        ax.plot(abs_err, label=method, color=_method_color(method))

    ax.set_title(f"{scenario_name} – {component} absolute error over time")
    ax.set_xlabel("Time index")
    ax.set_ylabel("|estimate - true|")
    ax.legend(loc="upper right", ncol=2, fontsize="small")
    fig.tight_layout()
    out_path = output_dir / f"error_timeseries_{component}_{scenario_name.replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_component_error_heatmap(
    scenario_name: str,
    true_components: Dict[str, np.ndarray],
    components_by_method: Dict[str, Dict[str, np.ndarray]],
    output_dir: str | Path,
    component: str = "trend",
    methods_to_show: Optional[List[str]] = None,
) -> Path:
    """
    Plot heatmap of absolute errors over time for multiple methods.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    methods = methods_to_show or sorted(components_by_method.keys())
    true_array = true_components.get(component)
    if true_array is None:
        raise ValueError(f"No ground-truth component '{component}' available.")
    true_series = np.asarray(true_array, dtype=float).reshape(-1)

    error_matrix = []
    valid_methods = []
    for method in methods:
        result = components_by_method.get(method)
        if not result or component not in result:
            continue
        est = np.asarray(result[component], dtype=float).reshape(-1)
        length = min(len(est), len(true_series))
        if length == 0:
            continue
        abs_err = np.abs(est[:length] - true_series[:length])
        error_matrix.append(abs_err)
        valid_methods.append(method)

    if not error_matrix:
        raise ValueError("No valid error series to plot.")

    data = np.vstack(error_matrix)
    fig, ax = plt.subplots(figsize=(12, 0.5 * len(valid_methods) + 2))
    im = ax.imshow(data, aspect="auto", interpolation="nearest", cmap="viridis")
    ax.set_title(f"{scenario_name} – {component} absolute error heatmap")
    ax.set_xlabel("Time index")
    ax.set_yticks(range(len(valid_methods)))
    ax.set_yticklabels(valid_methods)
    fig.colorbar(im, ax=ax, shrink=0.75, label="abs error")
    fig.tight_layout()
    out_path = output_dir / f"error_heatmap_{component}_{scenario_name.replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
