from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from detime.mcp import server


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "assets" / "generated" / "evidence"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _case_list_methods() -> dict[str, object]:
    payload = server.call_tool("list_methods", {"include_optional_backends": False})["structuredContent"]
    names = {item["name"] for item in payload["methods"]}
    _assert({"SSA", "STD", "STDR", "MSSA"}.issubset(names), "flagship methods missing")
    required_keys = {
        "family",
        "maturity",
        "implementation",
        "dependency_tier",
        "multivariate_support",
        "native_backed",
        "min_length",
        "summary",
        "recommended_for",
        "typical_failure_modes",
    }
    for item in payload["methods"]:
        _assert(required_keys.issubset(item.keys()), f"catalog contract missing keys for {item['name']}")
    return {"case": "list_methods", "status": "pass", "details": "stable catalog keys present"}


def _case_recommend_method() -> dict[str, object]:
    payload = server.call_tool(
        "recommend_method",
        {"length": 192, "channels": 3, "prefer": "accuracy", "top_k": 3},
    )["structuredContent"]
    _assert(payload["recommendations"][0]["method"] == "MSSA", "MSSA should lead multivariate accuracy case")
    return {"case": "recommend_method", "status": "pass", "details": "MSSA leads multivariate accuracy routing"}


def _case_get_schema() -> dict[str, object]:
    payload = server.call_tool("get_schema", {"name": "method-registry"})["structuredContent"]
    schema = payload["schema"]
    _assert(schema["title"] == "MethodRegistryPayloadModel", "unexpected schema title")
    return {"case": "get_schema", "status": "pass", "details": "method-registry schema resolved"}


def _case_summary_first_decompose() -> dict[str, object]:
    payload = server.call_tool(
        "run_decomposition",
        {
            "series": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
            "config": {"method": "MA_BASELINE", "params": {"window": 2}},
            "output_mode": "summary",
        },
    )["structuredContent"]
    _assert(payload["mode"] == "summary", "expected summary mode")
    _assert("diagnostics" in payload and "trend" in payload, "summary payload incomplete")
    return {"case": "summary_first_decompose", "status": "pass", "details": "summary payload returned without full arrays"}


def _case_bounded_context_report() -> dict[str, object]:
    payload = server.call_tool(
        "run_decomposition",
        {
            "series_path": str(ROOT / "examples" / "data" / "example_series.csv"),
            "col": "value",
            "config": {"method": "STD", "params": {"period": 12}},
            "output_mode": "meta",
        },
    )["structuredContent"]
    diagnostics = payload["diagnostics"]
    _assert(payload["mode"] == "meta", "expected meta mode")
    _assert(diagnostics["component_count"] >= 0, "diagnostics missing")
    return {"case": "bounded_context_report", "status": "pass", "details": "meta payload supports bounded-context reporting"}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = [
        _case_list_methods(),
        _case_recommend_method(),
        _case_get_schema(),
        _case_summary_first_decompose(),
        _case_bounded_context_report(),
    ]
    passed = sum(1 for case in cases if case["status"] == "pass")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "passed": passed,
            "failed": len(cases) - passed,
            "total": len(cases),
        },
        "cases": cases,
    }

    json_path = OUTPUT_DIR / "agent_eval_summary.json"
    csv_path = OUTPUT_DIR / "agent_eval_summary.csv"
    markdown_path = OUTPUT_DIR / "agent_eval_summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case", "status", "details"])
        writer.writeheader()
        writer.writerows(cases)
    markdown_path.write_text(
        "\n".join(
            [
                "# Agent eval summary",
                "",
                f"Passed `{passed}` / `{len(cases)}` deterministic MCP workflow checks.",
                "",
                "| case | status | details |",
                "| --- | --- | --- |",
                *[f"| {case['case']} | {case['status']} | {case['details']} |" for case in cases],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
