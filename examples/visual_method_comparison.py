from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from detime import DecompositionConfig, decompose
from detime.viz import plot_component_overlay, plot_method_comparison


def build_series(length: int = 180) -> np.ndarray:
    t = np.arange(length, dtype=float)
    trend = 0.018 * t
    season = 1.0 * np.sin(2.0 * np.pi * t / 12.0)
    harmonic = 0.25 * np.sin(2.0 * np.pi * t / 6.0 + 0.8)
    drift = 0.35 * np.where(t > 120, (t - 120) / 60.0, 0.0)
    return trend + season + harmonic + drift


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare decomposition methods visually.")
    parser.add_argument("--out-dir", default="out/visual_method_comparison", help="Directory for generated figures.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    series = build_series()
    jobs = {
        "STD": DecompositionConfig(method="STD", params={"period": 12}),
        "STDR": DecompositionConfig(method="STDR", params={"period": 12}),
        "SSA": DecompositionConfig(
            method="SSA",
            params={"window": 36, "rank": 8, "primary_period": 12},
        ),
        "STL": DecompositionConfig(method="STL", params={"period": 12}),
    }
    results = {name: decompose(series, config) for name, config in jobs.items()}

    plot_method_comparison(
        results,
        series,
        save_path=out_dir / "method_grid.png",
        title="Visual method comparison on one synthetic series",
    )
    plot_component_overlay(
        results,
        component="trend",
        series=series,
        save_path=out_dir / "trend_overlay.png",
        title="Trend overlay across methods",
    )
    plot_component_overlay(
        results,
        component="season",
        series=series,
        save_path=out_dir / "season_overlay.png",
        title="Seasonal overlay across methods",
    )

    records = []
    for name, result in results.items():
        reconstruction = np.asarray(result.trend) + np.asarray(result.season) + np.asarray(result.residual)
        records.append(
            {
                "method": name,
                "backend_used": result.meta.get("backend_used"),
                "trend_mean": float(np.mean(result.trend)),
                "trend_std": float(np.std(result.trend)),
                "season_std": float(np.std(result.season)),
                "residual_rms": float(np.sqrt(np.mean(np.square(result.residual)))),
                "reconstruction_max_abs_error": float(np.max(np.abs(series - reconstruction))),
            }
        )
    pd.DataFrame.from_records(records).to_csv(out_dir / "comparison_summary.csv", index=False)

    print("Wrote:")
    print(out_dir / "method_grid.png")
    print(out_dir / "trend_overlay.png")
    print(out_dir / "season_overlay.png")
    print(out_dir / "comparison_summary.csv")


if __name__ == "__main__":
    main()
