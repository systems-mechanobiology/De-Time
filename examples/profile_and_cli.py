from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    out_dir = Path("examples/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    t = np.arange(120, dtype=float)
    df_uni = pd.DataFrame(
        {"value": 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)}
    )
    df_uni.to_csv(out_dir / "example_series.csv", index=False)

    df_multi = pd.DataFrame(
        {
            "x0": 0.03 * t + np.sin(2.0 * np.pi * t / 12.0),
            "x1": -0.01 * t + 0.6 * np.sin(2.0 * np.pi * t / 12.0 + 0.4),
        }
    )
    df_multi.to_csv(out_dir / "example_multivariate.csv", index=False)

    print("Wrote:")
    print(out_dir / "example_series.csv")
    print(out_dir / "example_multivariate.csv")
    print()
    print("Example CLI commands:")
    print(
        "detime run --method STD --series examples/data/example_series.csv "
        "--col value --param period=12 --out_dir out/std_run"
    )
    print(
        "detime profile --method MSSA --series examples/data/example_multivariate.csv "
        "--cols x0,x1 --param window=24 --param primary_period=12"
    )


if __name__ == "__main__":
    main()
