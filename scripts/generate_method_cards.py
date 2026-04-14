from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detime import MethodRegistry, __version__

CARDS_OUTPUT = ROOT / "docs" / "method-cards.md"
REFERENCES_OUTPUT = ROOT / "docs" / "method-references.md"

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


def _link_list(items: list[dict[str, object]]) -> str:
    if not items:
        return "- none declared"
    rendered: list[str] = []
    for item in items:
        title = str(item["title"])
        url = str(item["url"])
        note = str(item.get("note", "")).strip()
        line = f"- [{title}]({url})"
        if note:
            line = f"{line} - {note}"
        rendered.append(line)
    return "\n".join(rendered)


def _render_method(entry: dict[str, object]) -> str:
    optional_dependencies = entry.get("optional_dependencies", [])
    optional_dep_text = ", ".join(optional_dependencies) if optional_dependencies else "none"
    references = list(entry.get("references", []))
    package_links = list(entry.get("package_links", []))
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
            "Method references:",
            _link_list(references),
            "",
            "Related package links:",
            _link_list(package_links),
            "",
        ]
    )


def _render_cards(catalog: list[dict[str, object]]) -> str:
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
        "Source citations and official upstream package links are collected in",
        "[Method References](method-references.md).",
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

    return "\n".join(lines).strip() + "\n"


def _render_references(catalog: list[dict[str, object]]) -> str:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in catalog:
        grouped[str(entry["maturity"])].append(entry)

    lines = [
        "# Method References",
        "",
        "This page is generated from `MethodRegistry.list_catalog()` so citations,",
        "upstream package links, and method metadata stay aligned.",
        "",
        f"Current package version target: `{__version__}`.",
        "",
        "These links cover the method families and upstream packages used or compared",
        "in the public De-Time workflow surface. `MA_BASELINE` is an in-package smoke",
        "baseline and therefore has no separate upstream citation.",
        "",
    ]

    for maturity, title in SECTION_ORDER:
        items = sorted(grouped.get(maturity, []), key=lambda item: str(item["name"]))
        if not items:
            continue
        lines.extend([f"## {title}", ""])
        for entry in items:
            optional_dependencies = entry.get("optional_dependencies", [])
            optional_dep_text = ", ".join(optional_dependencies) if optional_dependencies else "none"
            lines.extend(
                [
                    f"### `{entry['name']}`",
                    "",
                    f"- Summary: {entry['summary']}",
                    f"- Optional/runtime dependencies: {optional_dep_text}",
                    "",
                    "Primary references:",
                    _link_list(list(entry.get("references", []))),
                    "",
                    "Related packages:",
                    _link_list(list(entry.get("package_links", []))),
                    "",
                ]
            )

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    catalog = MethodRegistry.list_catalog()
    CARDS_OUTPUT.write_text(_render_cards(catalog), encoding="utf-8")
    REFERENCES_OUTPUT.write_text(_render_references(catalog), encoding="utf-8")
    print(f"wrote {CARDS_OUTPUT}")
    print(f"wrote {REFERENCES_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
