from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detime import MethodRegistry, __version__

CARDS_OUTPUT = ROOT / "docs" / "method-cards.md"
REFERENCES_OUTPUT = ROOT / "docs" / "method-references.md"
MATRIX_OUTPUT = ROOT / "docs" / "method-matrix.md"
CONFIG_OUTPUT = ROOT / "docs" / "config-reference.md"

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


def _table_cell(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def _default_label(value: object, required: bool) -> str:
    if required:
        return "required"
    if value is None:
        return "`None`"
    return f"`{json.dumps(value)}`"


def _param_table(params: list[dict[str, object]]) -> str:
    if not params:
        return "No method-specific parameters declared."

    lines = [
        "| Parameter | Type | Required | Default | Description |",
        "|---|---|---:|---|---|",
    ]
    for param in params:
        required = bool(param.get("required", False))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_table_cell(param.get('name', ''))}`",
                    _table_cell(param.get("type", "")),
                    "yes" if required else "no",
                    _default_label(param.get("default"), required),
                    _table_cell(param.get("description", "")),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _common_params(params: list[dict[str, object]]) -> str:
    rendered: list[str] = []
    for param in params:
        if bool(param.get("common", True)) or bool(param.get("required", False)):
            name = str(param.get("name", ""))
            required = bool(param.get("required", False))
            default = "required" if required else json.dumps(param.get("default"))
            rendered.append(f"`{name}` ({default})")
    return ", ".join(rendered) if rendered else "none declared"


def _code_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def _render_method(entry: dict[str, object]) -> str:
    optional_dependencies = entry.get("optional_dependencies", [])
    optional_dep_text = ", ".join(optional_dependencies) if optional_dependencies else "none"
    references = list(entry.get("references", []))
    package_links = list(entry.get("package_links", []))
    params = list(entry.get("parameter_docs", []))
    outputs = list(entry.get("output_components", []))
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
            f"- Common parameters: {_common_params(params)}",
            f"- Output components: {', '.join(f'`{item}`' for item in outputs) if outputs else '`trend`, `season`, `residual`'}",
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
            "Parameter notes:",
            _param_table(params),
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


def _render_matrix(catalog: list[dict[str, object]]) -> str:
    lines = [
        "# Method Comparison Matrix",
        "",
        "This page is generated from `MethodRegistry.list_catalog()` and summarizes",
        "method-level behavior for onboarding, review, and machine-facing routing.",
        "",
        f"Current package version target: `{__version__}`.",
        "",
        "| Method | Input mode | Backend | Maturity | Required/common params | Optional deps | Native | Multivariate | Output components | Recommended use |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for entry in sorted(catalog, key=lambda item: str(item["name"])):
        optional_dependencies = entry.get("optional_dependencies", [])
        optional_dep_text = ", ".join(str(item) for item in optional_dependencies) if optional_dependencies else "none"
        outputs = entry.get("output_components", [])
        output_text = ", ".join(f"`{item}`" for item in outputs) if outputs else "`trend`, `season`, `residual`"
        recommended = entry.get("recommended_for", [])
        recommended_text = "; ".join(str(item) for item in list(recommended)[:2])
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_table_cell(entry['name'])}`",
                    f"`{_table_cell(entry['input_mode'])}`",
                    f"`{_table_cell(entry['implementation'])}`",
                    f"`{_table_cell(entry['maturity'])}`",
                    _table_cell(_common_params(list(entry.get("parameter_docs", [])))),
                    _table_cell(optional_dep_text),
                    "yes" if entry.get("native_backed") else "no",
                    f"`{_table_cell(entry['multivariate_support'])}`",
                    _table_cell(output_text),
                    _table_cell(recommended_text),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Use [Config Reference](config-reference.md) for full `DecompositionConfig`",
            "field semantics and per-method parameter descriptions.",
            "",
            "Use [Method References](method-references.md) for primary literature and",
            "official upstream package links.",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _render_config_reference(catalog: list[dict[str, object]]) -> str:
    lines = [
        "# Config Reference",
        "",
        "`DecompositionConfig` is the single runtime contract shared by Python, CLI,",
        "docs examples, and machine-facing schema exports.",
        "",
        f"Current package version target: `{__version__}`.",
        "",
        "## Top-level fields",
        "",
        "| Field | Type | Default | Semantics |",
        "|---|---|---|---|",
        "| `method` | `str` | required | Registered method name such as `SSA`, `STD`, `STDR`, or `MSSA`. |",
        "| `params` | `dict[str, Any]` | `{}` | Method-specific parameters documented below. |",
        "| `return_components` | `list[str] \\| None` | `None` | Compatibility field; retained methods return the normalized result object. |",
        "| `backend` | `auto \\| native \\| python \\| gpu` | `auto` | Backend preference. `native` requires an available native kernel. |",
        "| `speed_mode` | `exact \\| fast` | `exact` | Accuracy policy. Native `SSA` uses exact SVD in `exact` and an iterative approximation in `fast`. |",
        "| `profile` | `bool` | `False` | Attach runtime metadata or produce profile reports when routed through the profiler. |",
        "| `device` | `str \\| None` | `cpu` | Reserved device selector; retained methods are CPU workflows unless a wrapper says otherwise. |",
        "| `n_jobs` | `int` | `1` | Parallelism hint for wrappers that support it. |",
        "| `seed` | `int \\| None` | `42` | Seed used by approximate or randomized paths where relevant. |",
        "| `channel_names` | `list[str] \\| None` | `None` | Optional labels for aligned multivariate channels. |",
        "",
        "## Complete examples",
        "",
        "### Univariate SSA",
        "",
        "```json",
        _code_json(MethodRegistry.get_metadata("SSA")["example_config"]),
        "```",
        "",
        "### Seasonal STD",
        "",
        "```json",
        _code_json(MethodRegistry.get_metadata("STD")["example_config"]),
        "```",
        "",
        "### Multivariate MSSA",
        "",
        "```json",
        _code_json(MethodRegistry.get_metadata("MSSA")["example_config"]),
        "```",
        "",
        "## Method-specific parameters",
        "",
    ]
    for entry in sorted(catalog, key=lambda item: str(item["name"])):
        lines.extend(
            [
                f"### `{entry['name']}`",
                "",
                f"- Input mode: `{entry['input_mode']}`",
                f"- Maturity: `{entry['maturity']}`",
                f"- Output components: {', '.join(f'`{item}`' for item in list(entry.get('output_components', [])))}",
                "",
                _param_table(list(entry.get("parameter_docs", []))),
                "",
                "Example config:",
                "",
                "```json",
                _code_json(entry.get("example_config", {"method": entry["name"], "params": {}})),
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    catalog = MethodRegistry.list_catalog()
    CARDS_OUTPUT.write_text(_render_cards(catalog), encoding="utf-8")
    REFERENCES_OUTPUT.write_text(_render_references(catalog), encoding="utf-8")
    MATRIX_OUTPUT.write_text(_render_matrix(catalog), encoding="utf-8")
    CONFIG_OUTPUT.write_text(_render_config_reference(catalog), encoding="utf-8")
    print(f"wrote {CARDS_OUTPUT}")
    print(f"wrote {REFERENCES_OUTPUT}")
    print(f"wrote {MATRIX_OUTPUT}")
    print(f"wrote {CONFIG_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
