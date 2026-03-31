"""Plotting utilities for synthetic_ts_bench."""

from __future__ import annotations

from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np


def plot_series_components(series_dict: Dict[str, Any], title: str = "") -> None:
    """
    Plot observed series plus decomposed components.

    Args:
        series_dict: Output of ``generate_series``.
        title: Optional figure title.
    """

    t = series_dict["t"]
    y = series_dict["y"]
    trend = series_dict["trend"]
    season = series_dict["season"]
    clean = series_dict["clean"]
    events = series_dict["events"]
    noise = series_dict["noise"]

    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(t, y, label="Observed y", color="black")
    axes[0].set_ylabel("y")
    axes[0].legend(loc="upper right")

    axes[1].plot(t, trend, label="Trend", color="tab:blue")
    axes[1].plot(t, season, label="Season", color="tab:orange", alpha=0.8)
    axes[1].set_ylabel("Trend/Season")
    axes[1].legend(loc="upper right")

    axes[2].plot(t, clean, label="Clean (T+S+E)", color="tab:green")
    axes[2].plot(t, y, label="Observed", color="black", alpha=0.3)
    axes[2].set_ylabel("Clean vs y")
    axes[2].legend(loc="upper right")

    axes[3].plot(t, events, label="Events", color="tab:red")
    axes[3].plot(t, noise, label="Noise", color="tab:purple", alpha=0.7)
    axes[3].set_ylabel("Events/Noise")
    axes[3].set_xlabel("Time")
    axes[3].legend(loc="upper right")

    fig.suptitle(title or "Synthetic series components")
    fig.tight_layout()
    fig.subplots_adjust(top=0.92)


def plot_power_spectrum(
    series_dict: Dict[str, Any],
    component_key: str = "y",
    title: str = "Power spectrum",
) -> None:
    """
    Plot a simple power spectrum (FFT magnitude) of a chosen component.

    Args:
        series_dict: Output of ``generate_series``.
        component_key: Key to pick from the dict, e.g. ``"season"``.
        title: Plot title.
    """

    signal = np.asarray(series_dict.get(component_key))
    if signal is None:
        raise ValueError(f"Component '{component_key}' not found in series_dict.")

    t = series_dict["t"]
    dt = t[1] - t[0] if len(t) > 1 else 1.0
    freq = np.fft.rfftfreq(signal.size, d=dt)
    power = np.abs(np.fft.rfft(signal)) ** 2

    plt.figure(figsize=(8, 4))
    plt.plot(freq, power)
    plt.xlabel("Frequency")
    plt.ylabel("Power")
    plt.title(title)
    plt.tight_layout()

