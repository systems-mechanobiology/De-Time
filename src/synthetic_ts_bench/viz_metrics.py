"""Visualization utilities for metric bar plots."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

METRIC_DIRECTIONS = {
    "T_r2": "higher_better",
    "T_dtw": "lower_better",
    "S_spectral_corr": "higher_better",
    "S_maxlag_corr": "higher_better",
}


def plot_metric_bars_for_scenario(
    df_metrics: pd.DataFrame,
    scenario_name: str,
    metric_cols: List[str],
    output_dir: str | Path,
) -> List[Path]:
    """
    For a given scenario, create horizontal bar plots per metric.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    subset = df_metrics[df_metrics["scenario_name"] == scenario_name]
    if subset.empty:
        return []

    saved: List[Path] = []
    for metric in metric_cols:
        if metric not in subset.columns:
            continue
        direction = METRIC_DIRECTIONS.get(metric, "higher_better")
        ascending = direction in {"lower_better"}
        data = subset[["method", metric]].dropna()
        if data.empty:
            continue
        data = data.sort_values(metric, ascending=ascending)
        fig, ax = plt.subplots(figsize=(8, 0.4 * len(data) + 2))
        ax.barh(data["method"], data[metric], color="tab:blue")
        ax.set_title(f"{scenario_name} – {metric}")
        ax.set_xlabel(metric)
        best_value = data[metric].iloc[0] if ascending else data[metric].iloc[-1]
        ax.axvline(best_value, color="red", linestyle="--", linewidth=1.0, label="best")
        for idx, val in enumerate(data[metric]):
            ax.text(
                val,
                idx,
                f"{val:.3f}",
                va="center",
                ha="left" if val >= 0 else "right",
            )
        ax.legend(loc="lower right", fontsize="small")
        fig.tight_layout()
        out_path = output_dir / f"metric_{metric}_{scenario_name.replace(' ', '_')}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        saved.append(out_path)
    return saved
