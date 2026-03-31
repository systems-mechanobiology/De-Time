from __future__ import annotations

import numpy as np

from detime import DecompositionConfig, decompose


def main() -> None:
    t = np.arange(96, dtype=float)
    series = np.column_stack(
        [
            0.03 * t + np.sin(2.0 * np.pi * t / 12.0),
            -0.01 * t + 0.6 * np.sin(2.0 * np.pi * t / 12.0 + 0.4),
        ]
    )

    result = decompose(
        series,
        DecompositionConfig(
            method="MSSA",
            params={"window": 24, "rank": 8, "primary_period": 12},
            channel_names=["x0", "x1"],
        ),
    )

    print("trend shape:", result.trend.shape)
    print("modes shape:", result.components["modes"].shape)
    print("backend:", result.meta.get("backend_used"))


if __name__ == "__main__":
    main()
