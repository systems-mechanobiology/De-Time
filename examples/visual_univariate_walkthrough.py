from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from detime import DecompositionConfig, decompose
from detime.viz import plot_components, plot_error


def build_series(length: int = 180) -> np.ndarray:
    t = np.arange(length, dtype=float)
    trend = 0.015 * t
    season = 1.2 * np.sin(2.0 * np.pi * t / 12.0)
    slow_cycle = 0.25 * np.cos(2.0 * np.pi * t / 48.0)
    pulse = np.where((t > 105) & (t < 120), 0.55, 0.0)
    return trend + season + slow_cycle + pulse


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a univariate decomposition walkthrough.")
    parser.add_argument("--out-dir", default="out/visual_univariate", help="Directory for generated figures.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    series = build_series()
    result = decompose(
        series,
        DecompositionConfig(
            method="SSA",
            params={"window": 36, "rank": 8, "primary_period": 12},
            profile=True,
        ),
    )

    plot_components(
        result,
        series=series,
        save_path=out_dir / "ssa_components.png",
        title="SSA decomposition walkthrough",
    )
    plot_error(
        result,
        series=series,
        save_path=out_dir / "ssa_residual_error.png",
        title="SSA residual magnitude",
    )

    summary = {
        "method": "SSA",
        "length": int(series.size),
        "window": 36,
        "rank": 8,
        "primary_period": 12,
        "backend_used": result.meta.get("backend_used"),
        "trend_mean": float(np.mean(result.trend)),
        "season_std": float(np.std(result.season)),
        "residual_rms": float(np.sqrt(np.mean(np.square(result.residual)))),
        "residual_peak_abs": float(np.max(np.abs(result.residual))),
        "reconstruction_max_abs_error": float(
            np.max(np.abs(series - np.asarray(result.trend) - np.asarray(result.season) - np.asarray(result.residual)))
        ),
    }
    pd.DataFrame([summary]).to_csv(out_dir / "ssa_summary.csv", index=False)
    (out_dir / "ssa_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Wrote:")
    print(out_dir / "ssa_components.png")
    print(out_dir / "ssa_residual_error.png")
    print(out_dir / "ssa_summary.csv")
    print(out_dir / "ssa_summary.json")
    print("Backend used:", result.meta.get("backend_used"))


if __name__ == "__main__":
    main()
