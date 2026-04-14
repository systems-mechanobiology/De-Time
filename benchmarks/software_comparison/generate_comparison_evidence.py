from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from detime import __version__


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "assets" / "generated" / "evidence"


CAPABILITY_MATRIX = [
    {
        "package": "De-Time",
        "primary_scope": "workflow-oriented decomposition layer",
        "unified_config_object": "yes",
        "unified_result_object": "yes",
        "machine_readable_catalog": "yes",
        "batch_cli": "yes",
        "profiling_path": "yes",
        "multivariate_support": "yes",
        "maturity_labeling": "explicit",
        "compact_output": "yes",
        "mcp_tool_surface": "yes",
    },
    {
        "package": "statsmodels",
        "primary_scope": "classical decomposition and modeling",
        "unified_config_object": "no",
        "unified_result_object": "partial",
        "machine_readable_catalog": "no",
        "batch_cli": "no",
        "profiling_path": "no",
        "multivariate_support": "limited",
        "maturity_labeling": "implicit",
        "compact_output": "no",
        "mcp_tool_surface": "no",
    },
    {
        "package": "PyEMD",
        "primary_scope": "EMD-family toolkit",
        "unified_config_object": "no",
        "unified_result_object": "no",
        "machine_readable_catalog": "no",
        "batch_cli": "no",
        "profiling_path": "no",
        "multivariate_support": "family-specific",
        "maturity_labeling": "family-specific",
        "compact_output": "no",
        "mcp_tool_surface": "no",
    },
    {
        "package": "PyWavelets",
        "primary_scope": "wavelet toolkit",
        "unified_config_object": "no",
        "unified_result_object": "no",
        "machine_readable_catalog": "no",
        "batch_cli": "no",
        "profiling_path": "no",
        "multivariate_support": "transform-specific",
        "maturity_labeling": "family-specific",
        "compact_output": "no",
        "mcp_tool_surface": "no",
    },
    {
        "package": "PySDKit",
        "primary_scope": "signal decomposition toolkit",
        "unified_config_object": "partial",
        "unified_result_object": "partial",
        "machine_readable_catalog": "no",
        "batch_cli": "limited",
        "profiling_path": "no",
        "multivariate_support": "yes",
        "maturity_labeling": "less explicit",
        "compact_output": "no",
        "mcp_tool_surface": "no",
    },
    {
        "package": "SSALib",
        "primary_scope": "SSA specialist toolkit",
        "unified_config_object": "SSA-specific",
        "unified_result_object": "SSA-specific",
        "machine_readable_catalog": "no",
        "batch_cli": "no",
        "profiling_path": "no",
        "multivariate_support": "no",
        "maturity_labeling": "focused",
        "compact_output": "no",
        "mcp_tool_surface": "no",
    },
    {
        "package": "sktime",
        "primary_scope": "broad time-series ecosystem",
        "unified_config_object": "no",
        "unified_result_object": "no",
        "machine_readable_catalog": "no",
        "batch_cli": "no",
        "profiling_path": "no",
        "multivariate_support": "partial",
        "maturity_labeling": "ecosystem-level",
        "compact_output": "no",
        "mcp_tool_surface": "no",
    },
]

INSTALL_MATRIX = [
    {
        "package": "De-Time",
        "public_release_story": f"0.1.1 target from main",
        "pypi_path": "tag-driven publish workflow",
        "github_release": "de-time-v0.1.1",
        "wheels": "yes",
        "ci_platforms": "ubuntu, macOS, windows",
        "docs_website": "GitHub Pages",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "dual report",
        "reproducibility_script": "yes",
    },
    {
        "package": "statsmodels",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "yes",
        "ci_platforms": "yes",
        "docs_website": "yes",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "project-dependent",
    },
    {
        "package": "PyEMD",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "partial",
        "ci_platforms": "project-dependent",
        "docs_website": "partial",
        "tutorials": "partial",
        "api_docs": "partial",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "PyWavelets",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "yes",
        "ci_platforms": "yes",
        "docs_website": "yes",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "PySDKit",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "partial",
        "ci_platforms": "project-dependent",
        "docs_website": "yes",
        "tutorials": "partial",
        "api_docs": "partial",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "SSALib",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "partial",
        "ci_platforms": "project-dependent",
        "docs_website": "yes",
        "tutorials": "partial",
        "api_docs": "partial",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "sktime",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "yes",
        "ci_platforms": "yes",
        "docs_website": "yes",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "project-dependent",
    },
]

FAMILY_FAIRNESS = [
    {
        "family": "classical decomposition",
        "specialist": "statsmodels",
        "specialist_deeper_strength": "deeper classical decomposition and statistical modeling",
        "de_time_position": "wraps STL and MSTL under one config/result/CLI layer",
    },
    {
        "family": "SSA",
        "specialist": "SSALib",
        "specialist_deeper_strength": "deeper SSA-only environment with SSA-specific tooling",
        "de_time_position": "uses SSA as one flagship method inside a cross-family workflow layer",
    },
    {
        "family": "EMD family",
        "specialist": "PyEMD",
        "specialist_deeper_strength": "deeper EMD-family tooling",
        "de_time_position": "exposes EMD and CEEMDAN through the same contract used for other families",
    },
    {
        "family": "wavelet workflows",
        "specialist": "PyWavelets",
        "specialist_deeper_strength": "deeper wavelet transforms and transform-specific APIs",
        "de_time_position": "uses wavelets as one workflow option rather than a wavelet-first toolkit",
    },
    {
        "family": "unified toolkit layer",
        "specialist": "PySDKit",
        "specialist_deeper_strength": "broader signal-decomposition toolkit with optional multivariate backends",
        "de_time_position": "focuses on time-series decomposition workflows, machine-facing contracts, and compact outputs",
    },
]

AGENT_MATRIX = [
    {
        "package": "De-Time",
        "json_schema_assets": "yes",
        "compact_result_modes": "full/summary/meta",
        "recommend_interface": "yes",
        "machine_readable_catalog": "yes",
        "mcp_surface": "local-first",
        "artifact_contract": "yes",
        "token_benchmark": "yes",
        "tool_evals": "yes",
    },
    {
        "package": "statsmodels",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "recommend_interface": "no",
        "machine_readable_catalog": "no",
        "mcp_surface": "no",
        "artifact_contract": "no",
        "token_benchmark": "no",
        "tool_evals": "no",
    },
    {
        "package": "PyEMD",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "recommend_interface": "no",
        "machine_readable_catalog": "no",
        "mcp_surface": "no",
        "artifact_contract": "no",
        "token_benchmark": "no",
        "tool_evals": "no",
    },
    {
        "package": "PyWavelets",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "recommend_interface": "no",
        "machine_readable_catalog": "no",
        "mcp_surface": "no",
        "artifact_contract": "no",
        "token_benchmark": "no",
        "tool_evals": "no",
    },
    {
        "package": "PySDKit",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "recommend_interface": "no",
        "machine_readable_catalog": "no",
        "mcp_surface": "no",
        "artifact_contract": "no",
        "token_benchmark": "no",
        "tool_evals": "no",
    },
    {
        "package": "SSALib",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "recommend_interface": "no",
        "machine_readable_catalog": "no",
        "mcp_surface": "no",
        "artifact_contract": "no",
        "token_benchmark": "no",
        "tool_evals": "no",
    },
    {
        "package": "sktime",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "recommend_interface": "no",
        "machine_readable_catalog": "no",
        "mcp_surface": "no",
        "artifact_contract": "no",
        "token_benchmark": "no",
        "tool_evals": "no",
    },
]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _markdown_table(rows: list[dict[str, object]]) -> list[str]:
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[key]) for key in headers) + " |")
    return lines


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    runtime_snapshot_csv = OUTPUT_DIR / "performance_snapshot.csv"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_target_version": __version__,
        "capability_matrix": CAPABILITY_MATRIX,
        "install_matrix": INSTALL_MATRIX,
        "family_fairness": FAMILY_FAIRNESS,
        "agent_matrix": AGENT_MATRIX,
        "runtime_snapshot_csv": str(runtime_snapshot_csv.relative_to(ROOT)),
    }

    json_path = OUTPUT_DIR / "comparison_evidence.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_csv(OUTPUT_DIR / "comparison_capability_matrix.csv", CAPABILITY_MATRIX)
    _write_csv(OUTPUT_DIR / "comparison_install_matrix.csv", INSTALL_MATRIX)
    _write_csv(OUTPUT_DIR / "comparison_family_fairness.csv", FAMILY_FAIRNESS)
    _write_csv(OUTPUT_DIR / "comparison_agent_matrix.csv", AGENT_MATRIX)

    markdown_lines = [
        "# Comparison Evidence",
        "",
        f"Generated for De-Time `{__version__}` on {payload['generated_at']}.",
        "",
        "## Capability matrix",
        "",
        *_markdown_table(CAPABILITY_MATRIX),
        "",
        "## Install and reproducibility matrix",
        "",
        *_markdown_table(INSTALL_MATRIX),
        "",
        "## Family-fairness notes",
        "",
        *_markdown_table(FAMILY_FAIRNESS),
        "",
        "## Agent-facing matrix",
        "",
        *_markdown_table(AGENT_MATRIX),
        "",
        "## Runtime snapshot source",
        "",
        f"- `{runtime_snapshot_csv.relative_to(ROOT)}`",
        "",
    ]
    (OUTPUT_DIR / "comparison_evidence.md").write_text(
        "\n".join(markdown_lines).strip() + "\n",
        encoding="utf-8",
    )
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
