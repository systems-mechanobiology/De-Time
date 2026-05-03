from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BANNED_PATTERNS: dict[str, list[str]] = {
    "README.md": [
        "reviewed snapshot",
    ],
    "PUBLISHING.md": [
        "reviewed snapshot",
        "pre-release review state",
        "not yet",
        "still pending",
    ],
    "CHANGELOG.md": [
        "Reviewed snapshot",
        "not yet tagged or published",
        "still pending",
    ],
    "docs/install.md": [
        "not yet available",
        "reviewed snapshot",
    ],
    "docs/reproducibility.md": [
        "GitHub source install",
        "reviewed snapshot",
        "still pending",
    ],
    "docs/citation.md": [
        "not yet a tagged GitHub release",
        "Formal release steps remain pending",
    ],
    "submission/cover_letter_jmlr_mloss.md": [
        "still pending",
        "have not yet created",
    ],
    "submission/software_evidence.md": [
        "still pending",
        "not created yet",
        "reviewed snapshot",
    ],
}

REQUIRED_PATTERNS: dict[str, list[str]] = {
    "README.md": [
        'python -m pip install "git+https://github.com/systems-mechanobiology/De-Time.git"',
        "examples/notebooks/de_time_method_gallery.ipynb",
        "docs/method-matrix.md",
        "detime schema",
        "detime recommend",
    ],
    "docs/install.md": [
        'python -m pip install "git+https://github.com/systems-mechanobiology/De-Time.git"',
        "Planned PyPI install after the release",
        "tsdecomp` executable",
    ],
    "docs/notebook-gallery.md": ["de_time_method_gallery.ipynb", "generate_notebook_gallery.py"],
    "docs/method-matrix.md": ["Required/common params", "Optional deps", "Output components"],
    "docs/config-reference.md": ["Top-level fields", "Method-specific parameters", "Univariate SSA"],
    "docs/reproducibility.md": ["core-plus-flagship", "release_smoke_matrix.py", "generate_performance_snapshot.py"],
    "docs/comparisons.md": ["PySDKit", "SSALib", "sktime"],
    "docs/tutorials/visual-univariate.md": ["$env:PYTHONPATH='src'", "python examples/visual_univariate_walkthrough.py"],
    "docs/tutorials/visual-multivariate.md": ["$env:PYTHONPATH='src'", "python examples/visual_multivariate_walkthrough.py"],
    "docs/tutorials/visual-comparison.md": ["$env:PYTHONPATH='src'", "python examples/visual_method_comparison.py"],
}

PUBLIC_DOCS = [
    "README.md",
    "docs/index.md",
    "docs/why.md",
    "docs/install.md",
    "docs/comparisons.md",
    "docs/methods.md",
    "docs/method-matrix.md",
    "docs/config-reference.md",
    "docs/notebook-gallery.md",
    "docs/api.md",
]

PUBLIC_BENCHMARK_BANS = [
    "visual-benchmark",
    "leaderboard walkthrough",
    "Benchmark heatmap walkthrough",
]

TUTORIAL_PLACEHOLDER_BANS = {
    "docs/tutorials/cli-and-profiling.md": [
        "data/monthly.csv",
        "data/panel.csv",
        "data/*.csv",
    ],
}

POSIX_ONLY_VISUAL_BANS = {
    "docs/tutorials/visual-univariate.md": [
        "PYTHONPATH=src python3",
    ],
    "docs/tutorials/visual-multivariate.md": [
        "PYTHONPATH=src python3",
    ],
    "docs/tutorials/visual-comparison.md": [
        "PYTHONPATH=src python3",
    ],
}

DOC_INDEX_PATH_CHECKS = [
    "DOCS_INDEX.md",
]


def _check_patterns(path: Path, patterns: list[str], *, expect_present: bool) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for pattern in patterns:
        found = pattern in text
        if expect_present and not found:
            failures.append(f"{path}: required pattern missing: {pattern}")
        if not expect_present and found:
            failures.append(f"{path}: banned pattern present: {pattern}")
    return failures


def _check_backticked_repo_paths(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for candidate in re.findall(r"`([^`\n]+)`", text):
        if "://" in candidate or "*" in candidate:
            continue
        if "/" not in candidate:
            continue
        repo_path = ROOT / candidate
        if not repo_path.exists():
            failures.append(f"{path}: referenced path does not exist: {candidate}")
    return failures


def main() -> int:
    failures: list[str] = []

    for relative_path, patterns in BANNED_PATTERNS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path, patterns in REQUIRED_PATTERNS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=True))

    for relative_path in PUBLIC_DOCS:
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, PUBLIC_BENCHMARK_BANS, expect_present=False))

    for relative_path, patterns in TUTORIAL_PLACEHOLDER_BANS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path, patterns in POSIX_ONLY_VISUAL_BANS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path in DOC_INDEX_PATH_CHECKS:
        path = ROOT / relative_path
        failures.extend(_check_backticked_repo_paths(path))

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("documentation consistency checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
