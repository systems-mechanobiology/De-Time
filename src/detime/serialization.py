from __future__ import annotations

from typing import Any, Literal, Sequence

import numpy as np

from .core import DecompResult

SerializationMode = Literal["full", "summary", "meta"]


def normalize_fields(fields: str | Sequence[str] | None) -> list[str] | None:
    if fields is None:
        return None
    if isinstance(fields, str):
        candidates = [part.strip() for part in fields.split(",")]
    else:
        candidates = [str(part).strip() for part in fields]
    selected = [part for part in candidates if part]
    return selected or None


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {str(key): _to_jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


def _array_summary(value: np.ndarray) -> dict[str, Any]:
    arr = np.asarray(value, dtype=float)
    if arr.size == 0:
        return {
            "shape": [int(v) for v in arr.shape],
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "l2_norm": 0.0,
        }
    return {
        "shape": [int(v) for v in arr.shape],
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "l2_norm": float(np.linalg.norm(arr)),
    }


def build_result_diagnostics(result: DecompResult) -> dict[str, Any]:
    meta = dict(result.meta or {})
    component_shapes = {
        name: [int(v) for v in np.asarray(value).shape]
        for name, value in result.components.items()
    }
    residual = np.asarray(result.residual, dtype=float)
    trend = np.asarray(result.trend, dtype=float)
    season = np.asarray(result.season, dtype=float)
    denominator = max(float(np.linalg.norm(trend + season) + 1e-12), 1e-12)
    quality_metrics = {
        "trend_l2_norm": float(np.linalg.norm(trend)),
        "season_l2_norm": float(np.linalg.norm(season)),
        "residual_l2_norm": float(np.linalg.norm(residual)),
        "residual_ratio": float(np.linalg.norm(residual) / denominator),
    }

    warnings: list[str] = []
    requested = meta.get("backend_requested")
    used = meta.get("backend_used")
    if requested and used and requested != "auto" and requested != used:
        warnings.append(f"backend_fallback:{requested}->{used}")
    if meta.get("result_layout") == "multivariate" and int(meta.get("n_channels", 1)) <= 1:
        warnings.append("multivariate_layout_without_multiple_channels")
    if not result.components:
        warnings.append("no_named_components")

    limitations = list(meta.get("limitations", []) or [])

    return {
        "component_count": len(result.components),
        "component_names": sorted(result.components.keys()),
        "component_shapes": component_shapes,
        "quality_metrics": quality_metrics,
        "warnings": warnings,
        "limitations": limitations,
    }


def serialize_result(
    result: DecompResult,
    *,
    mode: SerializationMode = "full",
    fields: str | Sequence[str] | None = None,
) -> dict[str, Any]:
    selected_fields = normalize_fields(fields)
    diagnostics = build_result_diagnostics(result)
    meta = _to_jsonable(dict(result.meta or {}))

    if mode == "full":
        payload: dict[str, Any] = {
            "mode": "full",
            "trend": _to_jsonable(np.asarray(result.trend)),
            "season": _to_jsonable(np.asarray(result.season)),
            "residual": _to_jsonable(np.asarray(result.residual)),
            "components": {name: _to_jsonable(np.asarray(value)) for name, value in result.components.items()},
            "meta": meta,
            "diagnostics": diagnostics,
        }
    elif mode == "summary":
        payload = {
            "mode": "summary",
            "trend": _array_summary(np.asarray(result.trend)),
            "season": _array_summary(np.asarray(result.season)),
            "residual": _array_summary(np.asarray(result.residual)),
            "components": {
                name: _array_summary(np.asarray(value))
                for name, value in result.components.items()
            },
            "meta": meta,
            "diagnostics": diagnostics,
        }
    elif mode == "meta":
        payload = {
            "mode": "meta",
            "meta": meta,
            "diagnostics": diagnostics,
        }
    else:  # pragma: no cover - guarded by CLI choices and tests
        raise ValueError(f"Unsupported serialization mode: {mode}")

    if not selected_fields:
        return payload
    return {
        key: value
        for key, value in payload.items()
        if key == "mode" or key in selected_fields
    }
