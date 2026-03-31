from __future__ import annotations

import numpy as np

from tsdecomp import DecompositionConfig, MethodRegistry, decompose


def main() -> None:
    t = np.arange(96, dtype=float)
    series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)
    panel = np.column_stack([series, 0.8 * series + 0.2 * np.cos(2.0 * np.pi * t / 6.0)])

    jobs = [
        ("STD", series, {"period": 12}),
        ("STDR", series, {"period": 12}),
        ("SSA", series, {"window": 24, "rank": 6, "primary_period": 12}),
        ("MA_BASELINE", series, {"trend_window": 11, "season_period": 12}),
        ("MSSA", panel, {"window": 24, "rank": 6, "primary_period": 12}),
    ]

    print("Registered methods:", len(MethodRegistry.list_methods()))
    for method, data, params in jobs:
        result = decompose(data, DecompositionConfig(method=method, params=params))
        print(
            method,
            "trend_shape=",
            np.asarray(result.trend).shape,
            "backend=",
            result.meta.get("backend_used"),
        )


if __name__ == "__main__":
    main()
