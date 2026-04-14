from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Literal

from pydantic import BaseModel, ConfigDict, Field

from ._metadata import CANONICAL_IMPORT, MACHINE_CONTRACT_VERSION, installed_version
from .core import DecompositionConfig
from .registry import MethodRegistry

SchemaName = Literal["config", "result", "meta", "method-registry"]
SCHEMA_FILENAMES: Dict[SchemaName, str] = {
    "config": "config.schema.json",
    "result": "result.schema.json",
    "meta": "meta.schema.json",
    "method-registry": "method-registry.schema.json",
}

class ArraySummaryModel(BaseModel):
    shape: list[int] = Field(default_factory=list)
    mean: float
    std: float
    min: float
    max: float
    l2_norm: float


class DiagnosticsModel(BaseModel):
    component_count: int = 0
    component_names: list[str] = Field(default_factory=list)
    component_shapes: Dict[str, list[int]] = Field(default_factory=dict)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ResultPayloadModel(BaseModel):
    mode: Literal["full"] = "full"
    trend: list[Any]
    season: list[Any]
    residual: list[Any]
    components: Dict[str, list[Any]] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: DiagnosticsModel = Field(default_factory=DiagnosticsModel)


class SummaryResultPayloadModel(BaseModel):
    mode: Literal["summary"] = "summary"
    trend: ArraySummaryModel
    season: ArraySummaryModel
    residual: ArraySummaryModel
    components: Dict[str, ArraySummaryModel] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: DiagnosticsModel = Field(default_factory=DiagnosticsModel)


class MetaPayloadModel(BaseModel):
    mode: Literal["meta"] = "meta"
    meta: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: DiagnosticsModel = Field(default_factory=DiagnosticsModel)


class MethodMetadataModel(BaseModel):
    name: str
    family: str
    input_mode: Literal["univariate", "multivariate", "channelwise"]
    maturity: Literal["flagship", "stable", "optional-backend", "experimental"]
    implementation: Literal["native-backed", "python", "wrapper", "optional-backend"]
    dependency_tier: Literal["core", "core-upstream", "optional-backend"]
    multivariate_support: Literal["univariate", "channelwise", "shared-model"]
    native_backed: bool
    min_length: int = Field(default=8, ge=1)
    summary: str
    recommended_for: list[str] = Field(default_factory=list)
    typical_failure_modes: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    not_recommended_for: list[str] = Field(default_factory=list)
    optional_dependencies: list[str] = Field(default_factory=list)


class MethodRegistryPayloadModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    package: Literal["detime"] = CANONICAL_IMPORT
    version: str
    contract_version: str = MACHINE_CONTRACT_VERSION
    methods: list[MethodMetadataModel] = Field(default_factory=list)


class RecommendationRequestModel(BaseModel):
    length: int = Field(ge=1)
    channels: int = Field(default=1, ge=1)
    prefer: Literal["speed", "balanced", "accuracy"] = "balanced"
    allow_optional_backends: bool = False
    require_native: bool = False
    top_k: int = Field(default=5, ge=1, le=20)


class RecommendationItemModel(BaseModel):
    method: str
    score: float
    rank: int
    reason_codes: list[str] = Field(default_factory=list)
    summary: str
    metadata: MethodMetadataModel


class RecommendationResponseModel(BaseModel):
    request: RecommendationRequestModel
    recommendations: list[RecommendationItemModel] = Field(default_factory=list)
    rejected_methods: Dict[str, str] = Field(default_factory=dict)


def _catalog_payload() -> MethodRegistryPayloadModel:
    methods = [MethodMetadataModel.model_validate(entry) for entry in MethodRegistry.list_catalog()]
    return MethodRegistryPayloadModel(version=installed_version(), methods=methods)


def build_schema_bundle() -> Dict[SchemaName, Dict[str, Any]]:
    result_variants = [
        ResultPayloadModel.model_json_schema(),
        SummaryResultPayloadModel.model_json_schema(),
    ]
    return {
        "config": DecompositionConfig.model_json_schema(),
        "result": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "DeTimeResultPayload",
            "description": "Serialized De-Time decomposition result in full or summary mode.",
            "oneOf": result_variants,
        },
        "meta": MetaPayloadModel.model_json_schema(),
        "method-registry": MethodRegistryPayloadModel.model_json_schema(),
    }


def available_schemas() -> list[SchemaName]:
    return list(SCHEMA_FILENAMES.keys())


def schema_asset_dir() -> Path:
    resource = resources.files("detime").joinpath("schema_assets")
    return Path(str(resource))


def get_schema(name: SchemaName) -> Dict[str, Any]:
    if name not in SCHEMA_FILENAMES:
        raise ValueError(f"Unknown schema '{name}'. Available: {available_schemas()}")

    resource = resources.files("detime").joinpath("schema_assets").joinpath(SCHEMA_FILENAMES[name])
    try:
        with resource.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:  # pragma: no cover - source tree fallback
        return build_schema_bundle()[name]


def write_schema_assets(output_dir: str | Path | None = None) -> dict[str, Path]:
    bundle = build_schema_bundle()
    target_dir = Path(output_dir) if output_dir is not None else schema_asset_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for name, filename in SCHEMA_FILENAMES.items():
        path = target_dir / filename
        path.write_text(json.dumps(bundle[name], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written[name] = path
    return written
