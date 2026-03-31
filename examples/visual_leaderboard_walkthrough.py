from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from detime import DecompositionConfig, decompose
from tsdecomp.leaderboard import plot_heatmaps
from tsdecomp.metrics import compute_metrics


def build_scenarios(length: int = 144) -> dict[str, dict[str, np.ndarray]]:
    t = np.arange(length, dtype=float)

    trend_a = 0.018 * t
    season_a = 1.1 * np.sin(2.0 * np.pi * t / 12.0)

    trend_b = 0.010 * t + 0.004 * np.maximum(t - 70.0, 0.0)
    season_b = 0.9 * np.sin(2.0 * np.pi * t / 12.0 + 0.4)

    trend_c = 0.006 * t + 0.35 * np.sin(2.0 * np.pi * t / 72.0)
    season_c = 0.6 * np.sin(2.0 * np.pi * t / 6.0)

    return {
        "seasonal_ramp": {"trend": trend_a, "season": season_a, "y": trend_a + season_a},
        "shifted_season": {"trend": trend_b, "season": season_b, "y": trend_b + season_b},
        "multi_scale": {"trend": trend_c, "season": season_c, "y": trend_c + season_c},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a lightweight leaderboard-style visualization.")
    parser.add_argument("--out-dir", default="out/visual_leaderboard", help="Directory for generated summary tables and heatmaps.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    summary_dir = out_dir / "summary"
    figures_dir = out_dir / "figures"
    summary_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    methods = {
        "SSA": DecompositionConfig(method="SSA", params={"window": 36, "rank": 8, "primary_period": 12}),
        "STDR": DecompositionConfig(method="STDR", params={"period": 12}),
        "STL": DecompositionConfig(method="STL", params={"period": 12}),
    }

    records: list[dict[str, float | str]] = []
    for scenario_id, payload in build_scenarios().items():
        y = payload["y"]
        true_trend = payload["trend"]
        true_season = payload["season"]
        for method_name, config in methods.items():
            result = decompose(y, config)
            trend_metrics = compute_metrics(true_trend, np.asarray(result.trend), fs=1.0)
            season_metrics = compute_metrics(true_season, np.asarray(result.season), fs=1.0)
            records.append(
                {
                    "scenario_id": scenario_id,
                    "method": method_name,
                    "metric_T_r2_mean": trend_metrics["r2"],
                    "metric_T_dtw_mean": trend_metrics["dtw"],
                    "metric_S_spectral_corr_mean": season_metrics["spec_corr"],
                    "metric_S_maxlag_corr_mean": season_metrics["max_lag_corr"],
                    "coverage": 1.0,
                }
            )

    scenario_summary = pd.DataFrame.from_records(records)
    scenario_summary.to_csv(summary_dir / "mini_leaderboard_by_scenario.csv", index=False)
    plot_heatmaps(scenario_summary, figures_dir)

    print("Wrote:")
    print(summary_dir / "mini_leaderboard_by_scenario.csv")
    for path in sorted(figures_dir.glob("*.png")):
        print(path)


if __name__ == "__main__":
    main()
