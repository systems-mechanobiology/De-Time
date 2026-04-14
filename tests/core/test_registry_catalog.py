from __future__ import annotations

from detime.registry import MethodRegistry
from detime.schemas import MethodMetadataModel, MethodRegistryPayloadModel


REQUIRED_FIELDS = {
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
    "references",
    "package_links",
}


def test_registry_catalog_contract_is_complete() -> None:
    catalog = MethodRegistry.list_catalog()
    assert catalog

    for entry in catalog:
        assert REQUIRED_FIELDS.issubset(entry.keys())
        validated = MethodMetadataModel.model_validate(entry)
        assert validated.name == entry["name"]


def test_registry_catalog_covers_flagship_wrapper_and_optional_paths() -> None:
    ssa = MethodRegistry.get_metadata("SSA")
    stl = MethodRegistry.get_metadata("STL")
    mvmd = MethodRegistry.get_metadata("MVMD")

    assert ssa["maturity"] == "flagship"
    assert ssa["references"]
    assert stl["implementation"] == "wrapper"
    assert stl["package_links"]
    assert mvmd["dependency_tier"] == "optional-backend"
    assert mvmd["optional_dependencies"] == ["PySDKit"]


def test_registry_payload_model_roundtrip() -> None:
    payload = MethodRegistryPayloadModel(
        package="detime",
        version="0.1.1",
        contract_version="0.1",
        methods=[MethodMetadataModel.model_validate(entry) for entry in MethodRegistry.list_catalog()],
    )
    assert payload.package == "detime"
    assert payload.contract_version == "0.1"
    assert payload.methods
