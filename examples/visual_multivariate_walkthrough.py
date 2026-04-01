from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from detime import DecompResult, DecompositionConfig, decompose
from detime.viz import plot_component_overlay, plot_multivariate_components


def build_panel(length: int = 144) -> np.ndarray:
    t = np.arange(length, dtype=float)
    base = np.sin(2.0 * np.pi * t / 12.0)
    return np.column_stack(
        [
            0.020 * t + 1.00 * base,
            -0.008 * t + 0.75 * np.sin(2.0 * np.pi * t / 12.0 + 0.4),
            0.15 * np.cos(2.0 * np.pi * t / 24.0) + 0.60 * base,
        ]
    )


def select_channel(result: DecompResult, channel_idx: int, channel_name: str) -> DecompResult:
    return DecompResult(
        trend=np.asarray(result.trend)[:, channel_idx],
        season=np.asarray(result.season)[:, channel_idx],
        residual=np.asarray(result.residual)[:, channel_idx],
        meta={"channel_name": channel_name, **result.meta},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate multivariate decomposition figures.")
    parser.add_argument("--out-dir", default="out/visual_multivariate", help="Directory for generated figures.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    panel = build_panel()
    channel_names = ["sensor_a", "sensor_b", "sensor_c"]

    mssa = decompose(
        panel,
        DecompositionConfig(
            method="MSSA",
            params={"window": 36, "rank": 10, "primary_period": 12},
            channel_names=channel_names,
        ),
    )
    std = decompose(
        panel,
        DecompositionConfig(
            method="STD",
            params={"period": 12},
            channel_names=channel_names,
        ),
    )

    plot_multivariate_components(
        mssa,
        series=panel,
        channel_names=channel_names,
        save_path=out_dir / "mssa_multivariate.png",
        title="MSSA multivariate decomposition",
    )
    plot_multivariate_components(
        std,
        series=panel,
        channel_names=channel_names,
        save_path=out_dir / "std_channelwise_multivariate.png",
        title="Channelwise STD multivariate decomposition",
    )

    channel_idx = 0
    comparison = {
        "MSSA": select_channel(mssa, channel_idx, channel_names[channel_idx]),
        "STD": select_channel(std, channel_idx, channel_names[channel_idx]),
    }
    plot_component_overlay(
        comparison,
        component="trend",
        series=panel[:, channel_idx],
        save_path=out_dir / "channel0_trend_overlay.png",
        title=f"Trend overlay for {channel_names[channel_idx]}",
    )

    records = []
    for channel_idx, channel_name in enumerate(channel_names):
        mssa_residual = np.asarray(mssa.residual)[:, channel_idx]
        std_residual = np.asarray(std.residual)[:, channel_idx]
        trend_gap = np.asarray(mssa.trend)[:, channel_idx] - np.asarray(std.trend)[:, channel_idx]
        records.append(
            {
                "channel": channel_name,
                "mssa_backend": mssa.meta.get("backend_used"),
                "std_backend": std.meta.get("backend_used"),
                "mssa_residual_rms": float(np.sqrt(np.mean(np.square(mssa_residual)))),
                "std_residual_rms": float(np.sqrt(np.mean(np.square(std_residual)))),
                "trend_overlay_mean_abs_gap": float(np.mean(np.abs(trend_gap))),
            }
        )
    pd.DataFrame.from_records(records).to_csv(out_dir / "multivariate_summary.csv", index=False)

    print("Wrote:")
    print(out_dir / "mssa_multivariate.png")
    print(out_dir / "std_channelwise_multivariate.png")
    print(out_dir / "channel0_trend_overlay.png")
    print(out_dir / "multivariate_summary.csv")


if __name__ == "__main__":
    main()
