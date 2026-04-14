from __future__ import annotations

import numpy as np

from detime import DecompositionConfig, decompose


def _shared_panel(length: int = 96) -> np.ndarray:
    t = np.arange(length, dtype=float)
    season = np.sin(2.0 * np.pi * t / 12.0)
    return np.column_stack(
        [
            0.03 * t + 0.9 * season,
            -0.01 * t + 0.6 * np.sin(2.0 * np.pi * t / 12.0 + 0.35) + 0.15 * np.cos(2.0 * np.pi * t / 6.0),
            0.02 * t + 0.5 * np.sin(2.0 * np.pi * t / 12.0 - 0.2) + 0.1 * np.cos(2.0 * np.pi * t / 4.0),
        ]
    )


def main() -> None:
    panel = _shared_panel()
    jobs = [
        ("MVMD", "modes"),
        ("MEMD", "imfs"),
    ]
    for method, component_name in jobs:
        try:
            result = decompose(
                panel,
                DecompositionConfig(
                    method=method,
                    params={"primary_period": 12},
                    backend="python",
                    channel_names=["x0", "x1", "x2"],
                ),
            )
        except ImportError as exc:
            raise SystemExit(
                f"{method} requires the optional multivariate backend. Install `de-time[multivar]` first."
            ) from exc

        print(f"{method} backend: {result.meta.get('backend_used')}")
        print(f"{method} trend shape: {result.trend.shape}")
        print(f"{method} {component_name} shape: {result.components[component_name].shape}")


if __name__ == "__main__":
    main()
