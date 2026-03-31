from __future__ import annotations

import numpy as np

from detime import DecompositionConfig, decompose


def main() -> None:
    t = np.arange(120, dtype=float)
    series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)

    result = decompose(
        series,
        DecompositionConfig(
            method="SSA",
            params={"window": 24, "rank": 6, "primary_period": 12},
        ),
    )

    print("trend shape:", result.trend.shape)
    print("season shape:", result.season.shape)
    print("residual shape:", result.residual.shape)
    print("backend:", result.meta.get("backend_used"))


if __name__ == "__main__":
    main()
