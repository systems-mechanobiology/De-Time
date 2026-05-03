from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Dict, Optional, Sequence, Union

import numpy as np

from .core import DecompResult

COLORS = {
    "original": "#111827",
    "trend": "#2563eb",
    "season": "#0f766e",
    "residual": "#f97316",
    "error": "#dc2626",
    "muted": "#64748b",
}

SERIES_PALETTE = [
    "#2563eb",
    "#0f766e",
    "#f97316",
    "#7c3aed",
    "#db2777",
    "#0891b2",
    "#ca8a04",
    "#475569",
]


def _component_color(name: str, idx: int = 0) -> str:
    key = name.lower()
    if key in COLORS:
        return COLORS[key]
    return SERIES_PALETTE[idx % len(SERIES_PALETTE)]


def _style_axis(ax, *, title: str | None = None) -> None:
    if hasattr(ax, "set_facecolor"):
        ax.set_facecolor("#ffffff")
    ax.grid(True, axis="y", alpha=0.22, color="#94a3b8", linewidth=0.8)
    ax.grid(False, axis="x")
    if hasattr(ax, "spines"):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#cbd5e1")
        ax.spines["bottom"].set_color("#cbd5e1")
    if hasattr(ax, "tick_params"):
        ax.tick_params(colors="#334155", labelsize=9)
    if title:
        ax.set_title(title, loc="left", fontsize=11, fontweight="bold", color="#0f172a")


def _as_1d(array: np.ndarray, label: str) -> np.ndarray:
    arr = np.asarray(array)
    if arr.ndim != 1:
        raise ValueError(f"{label} must be 1D for this plot, got shape {arr.shape}.")
    return arr


def _as_2d(array: np.ndarray, label: str) -> np.ndarray:
    arr = np.asarray(array)
    if arr.ndim != 2:
        raise ValueError(f"{label} must be 2D for this plot, got shape {arr.shape}.")
    return arr


def _coerce_axes_grid(axes, nrows: int, ncols: int):
    arr = np.asarray(axes, dtype=object)
    if arr.ndim == 0:
        return arr.reshape(1, 1)
    if arr.ndim == 1:
        return arr.reshape(nrows, ncols)
    return arr


def _plt():
    return import_module("matplotlib.pyplot")


def _finalize_figure(fig, plt, save_path, interactive: bool) -> None:
    if hasattr(fig, "patch") and hasattr(fig.patch, "set_facecolor"):
        fig.patch.set_facecolor("#f8fafc")
    try:
        fig.tight_layout(rect=(0, 0, 1, 0.97))
    except Exception:
        pass
    if save_path is not None:
        out_path = Path(save_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs = {"dpi": 220, "bbox_inches": "tight"}
        if hasattr(fig, "get_facecolor"):
            save_kwargs["facecolor"] = fig.get_facecolor()
        try:
            fig.savefig(out_path, **save_kwargs)
        except TypeError:
            fig.savefig(out_path, dpi=220)
    if interactive:
        plt.show()
    else:
        plt.close(fig)


def _resolve_channel_names(
    width: int,
    channel_names: Optional[Sequence[str]] = None,
) -> list[str]:
    if channel_names is None:
        return [f"channel_{idx}" for idx in range(width)]
    names = list(channel_names)
    if len(names) != width:
        raise ValueError(
            f"channel_names length {len(names)} does not match channel count {width}."
        )
    return names


def plot_components(
    result: DecompResult,
    series: Optional[np.ndarray] = None,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    title: str = "Decomposition Result",
) -> None:
    """Plot trend, season, residual, and optionally the original series for 1D results."""
    plt = _plt()

    components = [
        _as_1d(result.trend, "trend"),
        _as_1d(result.season, "season"),
        _as_1d(result.residual, "residual"),
    ]
    names = ["Trend", "Season", "Residual"]

    if series is not None:
        components.insert(0, _as_1d(series, "series"))
        names.insert(0, "Original")

    nrows = len(components)
    fig, axes = plt.subplots(nrows, 1, figsize=(11, 2.25 * nrows), sharex=True)
    axes_grid = _coerce_axes_grid(axes, nrows, 1)

    for row, (comp, name) in enumerate(zip(components, names)):
        ax = axes_grid[row, 0]
        ax.plot(comp, label=name, linewidth=1.65, color=_component_color(name))
        ax.set_ylabel(name)
        ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
        _style_axis(ax, title=name)

    axes_grid[-1, 0].set_xlabel("Time")
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color="#0f172a")
    _finalize_figure(fig, plt, save_path, interactive)


def plot_error(
    result: DecompResult,
    series: np.ndarray,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    title: str = "Residual Magnitude",
) -> None:
    """Plot the absolute residual as a simple local error proxy."""
    plt = _plt()

    _ = _as_1d(series, "series")
    error = np.abs(_as_1d(result.residual, "residual"))

    fig, ax = plt.subplots(figsize=(11, 3.6))
    x = np.arange(error.size)
    if hasattr(ax, "fill_between"):
        ax.fill_between(x, error, color=COLORS["error"], alpha=0.14)
    ax.plot(error, color=COLORS["error"], label="|Residual|", linewidth=1.6)
    ax.set_ylabel("Absolute Error")
    ax.set_xlabel("Time")
    _style_axis(ax, title=title)
    ax.legend(frameon=True, framealpha=0.9)
    _finalize_figure(fig, plt, save_path, interactive)


def plot_component_overlay(
    results: Dict[str, DecompResult],
    component: str = "trend",
    series: Optional[np.ndarray] = None,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    title: Optional[str] = None,
) -> None:
    """Overlay one component from multiple univariate methods on a shared axis."""
    plt = _plt()

    if component not in {"trend", "season", "residual"}:
        raise ValueError("component must be one of: trend, season, residual")
    if not results:
        raise ValueError("results must contain at least one method.")

    fig, ax = plt.subplots(figsize=(11, 3.8))
    if series is not None:
        ax.plot(
            _as_1d(series, "series"),
            color=COLORS["original"],
            alpha=0.28,
            linewidth=1.7,
            label="Original",
        )

    for idx, (method_name, result) in enumerate(results.items()):
        values = _as_1d(getattr(result, component), f"{method_name}.{component}")
        ax.plot(values, linewidth=1.8, label=method_name, color=_component_color(method_name, idx))

    ax.set_xlabel("Time")
    ax.set_ylabel(component.title())
    _style_axis(ax, title=title or f"{component.title()} overlay")
    ax.legend(loc="upper right", ncol=2, frameon=True, framealpha=0.92, fontsize=9)
    _finalize_figure(fig, plt, save_path, interactive)


def plot_method_comparison(
    results: Dict[str, DecompResult],
    series: np.ndarray,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    title: str = "Method Comparison",
) -> None:
    """Compare multiple univariate methods in a row-by-column panel layout."""
    plt = _plt()

    if not results:
        raise ValueError("results must contain at least one method.")

    base_series = _as_1d(series, "series")
    columns = ["Original", "Trend", "Season", "Residual"]
    nrows = len(results)
    ncols = len(columns)
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(4.0 * ncols, 2.5 * nrows),
        sharex=True,
    )
    axes_grid = _coerce_axes_grid(axes, nrows, ncols)

    for col, column_name in enumerate(columns):
        axes_grid[0, col].set_title(column_name, fontsize=11, fontweight="bold", color="#0f172a")

    for row, (method_name, result) in enumerate(results.items()):
        row_data = [
            base_series,
            _as_1d(result.trend, f"{method_name}.trend"),
            _as_1d(result.season, f"{method_name}.season"),
            _as_1d(result.residual, f"{method_name}.residual"),
        ]
        for col, values in enumerate(row_data):
            ax = axes_grid[row, col]
            component_name = columns[col]
            if col == 0:
                ax.plot(values, color=COLORS["original"], linewidth=1.45)
            else:
                ax.plot(values, linewidth=1.45, color=_component_color(component_name))
            if col == 0:
                ax.set_ylabel(method_name)
            _style_axis(ax)

    for col in range(ncols):
        axes_grid[-1, col].set_xlabel("Time")

    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color="#0f172a")
    _finalize_figure(fig, plt, save_path, interactive)


def plot_multivariate_components(
    result: DecompResult,
    series: Optional[np.ndarray] = None,
    channel_names: Optional[Sequence[str]] = None,
    save_path: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    title: str = "Multivariate Decomposition Result",
) -> None:
    """Plot per-channel trend, season, residual, and optionally original series."""
    plt = _plt()

    trend = _as_2d(result.trend, "trend")
    season = _as_2d(result.season, "season")
    residual = _as_2d(result.residual, "residual")
    if trend.shape != season.shape or trend.shape != residual.shape:
        raise ValueError("trend, season, and residual must share the same shape.")

    if series is not None:
        series_arr = _as_2d(series, "series")
        if series_arr.shape != trend.shape:
            raise ValueError(
                f"series shape {series_arr.shape} does not match component shape {trend.shape}."
            )
    else:
        series_arr = None

    components: list[tuple[str, np.ndarray]] = []
    if series_arr is not None:
        components.append(("Original", series_arr))
    components.extend(
        [
            ("Trend", trend),
            ("Season", season),
            ("Residual", residual),
        ]
    )

    n_channels = trend.shape[1]
    names = _resolve_channel_names(
        n_channels,
        channel_names or result.meta.get("channel_names"),
    )
    nrows = n_channels
    ncols = len(components)
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(4.0 * ncols, 2.35 * nrows),
        sharex=True,
    )
    axes_grid = _coerce_axes_grid(axes, nrows, ncols)

    for col, (label, _) in enumerate(components):
        axes_grid[0, col].set_title(label, fontsize=11, fontweight="bold", color="#0f172a")

    for row, channel_name in enumerate(names):
        for col, (_, values) in enumerate(components):
            ax = axes_grid[row, col]
            ax.plot(values[:, row], linewidth=1.45, color=_component_color(components[col][0], row))
            if col == 0:
                ax.set_ylabel(channel_name)
            _style_axis(ax)

    for col in range(ncols):
        axes_grid[-1, col].set_xlabel("Time")

    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color="#0f172a")
    _finalize_figure(fig, plt, save_path, interactive)
