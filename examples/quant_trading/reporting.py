from __future__ import annotations

"""Reporting helpers for the De-Time quant trading tutorials."""

from pathlib import Path
from typing import Mapping

import pandas as pd


def save_backtest_artifacts(result, output_dir: str | Path, *, prefix: str = "strategy") -> dict[str, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "returns": out / f"{prefix}_returns.csv",
        "equity": out / f"{prefix}_equity.csv",
        "weights": out / f"{prefix}_weights.csv",
        "costs": out / f"{prefix}_costs.csv",
        "turnover": out / f"{prefix}_turnover.csv",
        "stats": out / f"{prefix}_stats.csv",
    }
    result.returns.to_csv(paths["returns"])
    result.equity.to_csv(paths["equity"])
    result.weights.to_csv(paths["weights"])
    result.costs.to_csv(paths["costs"])
    result.turnover.to_csv(paths["turnover"])
    pd.DataFrame([result.stats]).to_csv(paths["stats"], index=False)
    return paths


def markdown_metric_report(stats: Mapping[str, float], *, title: str = "De-Time Quant Strategy Report") -> str:
    lines = [f"# {title}", "", "This report is generated from tutorial code and is not investment advice.", "", "## Metrics", ""]
    for key, value in stats.items():
        try:
            lines.append(f"- **{key}**: {float(value):.6g}")
        except Exception:
            lines.append(f"- **{key}**: {value}")
    return "\n".join(lines) + "\n"
