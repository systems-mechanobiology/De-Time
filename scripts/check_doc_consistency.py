from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BANNED_PATTERNS: dict[str, list[str]] = {
    "README.md": [
        "reviewed snapshot",
        "GitHub source install",
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
        "GitHub source install",
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
        "GitHub source install",
        "still pending",
        "not created yet",
        "reviewed snapshot",
    ],
    "JMLR_MLOSS_CHECKLIST.md": [
        "submission checklist for `tsdecomp`",
        "`DR_TS_REG`",
    ],
    "JMLR_SOFTWARE_IMPROVEMENTS.md": [
        "`DR_TS_REG`",
    ],
}

REQUIRED_PATTERNS: dict[str, list[str]] = {
    "README.md": ["pip install de-time", "detime schema", "detime recommend"],
    "docs/install.md": ["pip install de-time", "tsdecomp` executable"],
    "docs/reproducibility.md": ["core-plus-flagship", "release_smoke_matrix.py", "generate_performance_snapshot.py"],
    "docs/comparisons.md": ["PySDKit", "SSALib", "sktime"],
}

PUBLIC_DOCS = [
    "README.md",
    "docs/index.md",
    "docs/why.md",
    "docs/install.md",
    "docs/comparisons.md",
    "docs/methods.md",
    "docs/api.md",
]

PUBLIC_BENCHMARK_BANS = [
    "visual-benchmark",
    "leaderboard walkthrough",
    "Benchmark heatmap walkthrough",
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

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("documentation consistency checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
