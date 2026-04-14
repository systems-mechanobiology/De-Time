from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "assets" / "generated" / "evidence"

SPECIALIST_GLUE = """\
import pandas as pd
from statsmodels.tsa.seasonal import STL
from ssalib import SingularSpectrumAnalysis

frame = pd.read_csv("examples/data/example_series.csv")
series = frame["value"].to_numpy()

stl = STL(series, period=12).fit()
ssa = SingularSpectrumAnalysis(window_size=24, rank=6)
ssa_components = ssa.fit_transform(series)

summary = {
    "trend_std": float(stl.trend.std()),
    "season_std": float(stl.seasonal.std()),
    "ssa_components": int(ssa_components.shape[1]),
}
"""

DETIME_WORKFLOW = """\
from detime import DecompositionConfig, decompose
from detime.io import read_series

series = read_series("examples/data/example_series.csv", col="value")
result = decompose(
    series,
    DecompositionConfig(method="SSA", params={"window": 24, "rank": 6, "primary_period": 12}),
)

summary = {
    "trend_std": float(result.trend.std()),
    "season_std": float(result.season.std()),
    "component_count": len(result.components),
}
"""


def _count_steps(snippet: str) -> int:
    return sum(1 for line in snippet.splitlines() if line.strip() and not line.strip().startswith("#"))


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "specialist_glue": {
            "packages": ["pandas", "statsmodels", "ssalib"],
            "step_count": _count_steps(SPECIALIST_GLUE),
            "snippet": SPECIALIST_GLUE,
        },
        "detime": {
            "packages": ["detime"],
            "step_count": _count_steps(DETIME_WORKFLOW),
            "snippet": DETIME_WORKFLOW,
        },
        "narrative": [
            "The specialist workflow mixes multiple imports, result objects, and package-specific APIs.",
            "The De-Time workflow keeps the same result contract and method switch path under one import surface.",
        ],
    }
    (OUTPUT_DIR / "workflow_comparison.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (ROOT / "examples" / "workflow_comparisons" / "README.md").write_text(
        "\n".join(
            [
                "# Workflow Comparisons",
                "",
                "This example contrasts a multi-package specialist glue workflow with the",
                "equivalent De-Time workflow. Run the script to materialize the JSON summary",
                "used by the docs comparison pages.",
                "",
                "```bash",
                "python examples/workflow_comparisons/compare_specialist_glue_vs_detime.py",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote workflow comparison evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
