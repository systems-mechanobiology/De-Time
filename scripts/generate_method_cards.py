from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from detime import MethodRegistry, __version__


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "method-cards.md"

SECTION_ORDER = [
    ("flagship", "Flagship methods"),
    ("stable", "Stable wrappers and retained methods"),
    ("optional-backend", "Optional backend methods"),
    ("experimental", "Experimental methods"),
]


def _bullet_list(values: list[str]) -> str:
    if not values:
        return "- none declared"
    return "\n".join(f"- {value}" for value in values)


def _render_method(entry: dict[str, object]) -> str:
    optional_dependencies = entry.get("optional_dependencies", [])
    optional_dep_text = ", ".join(optional_dependencies) if optional_dependencies else "none"
    return "\n".join(
        [
            f"### `{entry['name']}`",
            "",
            f"- Family: `{entry['family']}`",
            f"- Input mode: `{entry['input_mode']}`",
            f"- Maturity: `{entry['maturity']}`",
            f"- Implementation: `{entry['implementation']}`",
            f"- Dependency tier: `{entry['dependency_tier']}`",
            f"- Multivariate support: `{entry['multivariate_support']}`",
            f"- Native-backed: `{entry['native_backed']}`",
            f"- Minimum length hint: `{entry['min_length']}`",
            f"- Optional dependencies: {optional_dep_text}",
            f"- Summary: {entry['summary']}",
            "",
            "Assumptions:",
            _bullet_list(list(entry.get("assumptions", []))),
            "",
            "Recommended for:",
            _bullet_list(list(entry.get("recommended_for", []))),
            "",
            "Typical failure modes:",
            _bullet_list(list(entry.get("typical_failure_modes", []))),
            "",
            "Not recommended for:",
            _bullet_list(list(entry.get("not_recommended_for", []))),
            "",
        ]
    )


def main() -> int:
    catalog = MethodRegistry.list_catalog()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in catalog:
        grouped[str(entry["maturity"])].append(entry)

    lines = [
        "# Method Cards",
        "",
        "This page is generated from `MethodRegistry.list_catalog()` so the human-facing",
        "method cards stay aligned with the machine-facing catalog contract.",
        "",
        f"Current package version target: `{__version__}`.",
        "",
        "The `tsdecomp` top-level alias remains compatibility-only through `0.1.x` and is",
        "not the canonical surface for any method listed below.",
        "",
    ]

    for maturity, title in SECTION_ORDER:
        items = sorted(grouped.get(maturity, []), key=lambda item: str(item["name"]))
        if not items:
            continue
        lines.extend([f"## {title}", ""])
        for entry in items:
            lines.append(_render_method(entry))

    OUTPUT.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
