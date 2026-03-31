from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

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

    print("Wrote:")
    print(out_dir / "ssa_components.png")
    print(out_dir / "ssa_residual_error.png")
    print("Backend used:", result.meta.get("backend_used"))


if __name__ == "__main__":
    main()
