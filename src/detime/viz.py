from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Dict, Optional, Sequence, Union

import numpy as np

from .core import DecompResult


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
    plt.tight_layout()
    if save_path is not None:
        out_path = Path(save_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150)
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
    fig, axes = plt.subplots(nrows, 1, figsize=(10, 2.5 * nrows), sharex=True)
    axes_grid = _coerce_axes_grid(axes, nrows, 1)

    for row, (comp, name) in enumerate(zip(components, names)):
        ax = axes_grid[row, 0]
        ax.plot(comp, label=name, linewidth=1.5)
        ax.set_ylabel(name)
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)

    axes_grid[-1, 0].set_xlabel("Time")
    fig.suptitle(title)
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

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(error, color="red", label="|Residual|", linewidth=1.5)
    ax.set_ylabel("Absolute Error")
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
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

    fig, ax = plt.subplots(figsize=(11, 4))
    if series is not None:
        ax.plot(_as_1d(series, "series"), color="black", alpha=0.35, label="Original")

    for method_name, result in results.items():
        values = _as_1d(getattr(result, component), f"{method_name}.{component}")
        ax.plot(values, linewidth=1.6, label=method_name)

    ax.set_xlabel("Time")
    ax.set_ylabel(component.title())
    ax.set_title(title or f"{component.title()} overlay")
    ax.legend(loc="upper right", ncol=2)
    ax.grid(True, alpha=0.3)
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
        figsize=(3.8 * ncols, 2.6 * nrows),
        sharex=True,
    )
    axes_grid = _coerce_axes_grid(axes, nrows, ncols)

    for col, column_name in enumerate(columns):
        axes_grid[0, col].set_title(column_name)

    for row, (method_name, result) in enumerate(results.items()):
        row_data = [
            base_series,
            _as_1d(result.trend, f"{method_name}.trend"),
            _as_1d(result.season, f"{method_name}.season"),
            _as_1d(result.residual, f"{method_name}.residual"),
        ]
        for col, values in enumerate(row_data):
            ax = axes_grid[row, col]
            if col == 0:
                ax.plot(values, color="black", linewidth=1.4)
            else:
                ax.plot(values, linewidth=1.4)
            if col == 0:
                ax.set_ylabel(method_name)
            ax.grid(True, alpha=0.3)
        axes_grid[row, 0].legend([method_name], loc="upper right")

    for col in range(ncols):
        axes_grid[-1, col].set_xlabel("Time")

    fig.suptitle(title)
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
        figsize=(3.8 * ncols, 2.5 * nrows),
        sharex=True,
    )
    axes_grid = _coerce_axes_grid(axes, nrows, ncols)

    for col, (label, _) in enumerate(components):
        axes_grid[0, col].set_title(label)

    for row, channel_name in enumerate(names):
        for col, (_, values) in enumerate(components):
            ax = axes_grid[row, col]
            ax.plot(values[:, row], linewidth=1.4)
            if col == 0:
                ax.set_ylabel(channel_name)
            ax.grid(True, alpha=0.3)

    for col in range(ncols):
        axes_grid[-1, col].set_xlabel("Time")

    fig.suptitle(title)
    _finalize_figure(fig, plt, save_path, interactive)
