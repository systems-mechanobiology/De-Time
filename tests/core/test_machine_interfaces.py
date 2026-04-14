from __future__ import annotations

import json

import numpy as np

from detime import DecompResult
from detime.io import save_result
from detime.recommend import recommend_methods
from detime.registry import MethodRegistry
from detime.schemas import available_schemas, build_schema_bundle, get_schema, write_schema_assets
from detime.serialization import build_result_diagnostics, serialize_result


def _sample_result() -> DecompResult:
    series = np.linspace(0.0, 1.0, 8)
    return DecompResult(
        trend=series,
        season=np.zeros_like(series),
        residual=0.1 * np.ones_like(series),
        components={"detail": np.vstack([series, series]).T},
        meta={
            "method": "SSA",
            "backend_requested": "native",
            "backend_used": "python",
            "result_layout": "univariate",
            "n_channels": 1,
        },
    )


def test_registry_catalog_exposes_machine_metadata() -> None:
    catalog = MethodRegistry.list_catalog()
    names = {entry["name"] for entry in catalog}

    assert {"SSA", "STD", "STDR", "MSSA"}.issubset(names)

    ssa = MethodRegistry.get_metadata("SSA")
    assert ssa["maturity"] == "flagship"
    assert ssa["native_backed"] is True
    assert ssa["family"] == "SSA"
    assert ssa["assumptions"]
    assert ssa["not_recommended_for"]
    assert isinstance(ssa["optional_dependencies"], list)
    assert ssa["references"]
    assert any(link["url"].startswith("https://") for link in ssa["references"])


def test_serialization_modes_and_diagnostics() -> None:
    result = _sample_result()

    diagnostics = build_result_diagnostics(result)
    assert "backend_fallback:native->python" in diagnostics["warnings"]
    assert diagnostics["component_shapes"]["detail"] == [8, 2]

    full_payload = serialize_result(result, mode="full", fields="meta,diagnostics")
    assert full_payload["mode"] == "full"
    assert set(full_payload) == {"mode", "meta", "diagnostics"}

    summary_payload = serialize_result(result, mode="summary")
    assert summary_payload["trend"]["shape"] == [8]
    assert summary_payload["components"]["detail"]["shape"] == [8, 2]

    meta_payload = serialize_result(result, mode="meta")
    assert set(meta_payload) == {"mode", "meta", "diagnostics"}


def test_save_result_supports_summary_and_meta_modes(tmp_path) -> None:
    result = _sample_result()

    save_result(result, tmp_path, "case", output_mode="summary", fields="meta,diagnostics")
    summary_path = tmp_path / "case_summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "summary"
    assert "meta" in payload
    assert "diagnostics" in payload

    save_result(result, tmp_path, "case_meta", output_mode="meta")
    meta_path = tmp_path / "case_meta_meta.json"
    meta_payload = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta_payload["mode"] == "meta"


def test_schema_assets_are_packaged_and_regeneratable(tmp_path) -> None:
    assert set(available_schemas()) == {"config", "result", "meta", "method-registry"}

    config_schema = get_schema("config")
    assert config_schema["title"] == "DecompositionConfig"

    method_registry_schema = get_schema("method-registry")
    assert method_registry_schema["title"] == "MethodRegistryPayloadModel"
    assert "contract_version" in method_registry_schema["properties"]
    method_properties = method_registry_schema["$defs"]["MethodMetadataModel"]["properties"]
    assert "references" in method_properties
    assert "package_links" in method_properties
    assert method_registry_schema == build_schema_bundle()["method-registry"]

    written = write_schema_assets(tmp_path)
    assert (tmp_path / "config.schema.json") == written["config"]
    assert json.loads((tmp_path / "meta.schema.json").read_text(encoding="utf-8"))["title"] == "MetaPayloadModel"


def test_recommend_methods_prefers_multivariate_flagship() -> None:
    response = recommend_methods(
        {
            "length": 192,
            "channels": 3,
            "prefer": "accuracy",
            "allow_optional_backends": False,
            "require_native": False,
            "top_k": 3,
        }
    )

    assert response.recommendations
    assert response.recommendations[0].method == "MSSA"
    assert "optional_backend_disabled" in response.rejected_methods["MVMD"]


def test_recommend_methods_surface_reason_codes_and_rejections() -> None:
    short_balanced = recommend_methods(
        {
            "length": 16,
            "channels": 1,
            "prefer": "balanced",
            "allow_optional_backends": True,
            "require_native": False,
            "top_k": 5,
        }
    )
    std_item = next(item for item in short_balanced.recommendations if item.method == "STD")
    assert "balanced_flagship" in std_item.reason_codes
    assert "short_series_friendly" in std_item.reason_codes
    assert any("univariate_ready" in item.reason_codes for item in short_balanced.recommendations)
    assert short_balanced.rejected_methods["MSSA"] == "requires_multivariate_input"
    assert short_balanced.rejected_methods["SSA"].startswith("series_too_short")

    native_speed = recommend_methods(
        {
            "length": 128,
            "channels": 1,
            "prefer": "speed",
            "allow_optional_backends": False,
            "require_native": True,
            "top_k": 5,
        }
    )
    top_item = native_speed.recommendations[0]
    assert "speed_native_bonus" in top_item.reason_codes
    assert "speed_shortlist" in top_item.reason_codes
    assert native_speed.rejected_methods["MA_BASELINE"] == "native_required"
