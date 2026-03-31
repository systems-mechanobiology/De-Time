from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict, Mapping, Sequence

import numpy as np

from ._native import has_native_method, native_extension_available, native_import_error
from .core import DecompResult, DecompositionConfig

RUNTIME_KEY = "__tsdecomp_runtime__"
VALID_BACKENDS = {"auto", "native", "python", "gpu"}
VALID_SPEED_MODES = {"exact", "fast"}


@dataclass(frozen=True)
class RuntimeOptions:
    backend: str = "auto"
    speed_mode: str = "exact"
    profile: bool = False
    device: str = "cpu"
    n_jobs: int = 1
    seed: int | None = 42


def _normalize_backend(name: Any) -> str:
    value = str(name or "auto").strip().lower()
    if value not in VALID_BACKENDS:
        raise ValueError(f"Unsupported backend '{name}'. Valid backends: {sorted(VALID_BACKENDS)}")
    return value


def _normalize_speed_mode(name: Any) -> str:
    value = str(name or "exact").strip().lower()
    if value not in VALID_SPEED_MODES:
        raise ValueError(
            f"Unsupported speed_mode '{name}'. Valid modes: {sorted(VALID_SPEED_MODES)}"
        )
    return value


def runtime_options_from_config(config: DecompositionConfig) -> RuntimeOptions:
    return RuntimeOptions(
        backend=_normalize_backend(config.backend),
        speed_mode=_normalize_speed_mode(config.speed_mode),
        profile=bool(config.profile),
        device=str(config.device or "cpu"),
        n_jobs=max(1, int(config.n_jobs)),
        seed=None if config.seed is None else int(config.seed),
    )


def inject_runtime_params(params: Dict[str, Any], runtime: RuntimeOptions) -> Dict[str, Any]:
    out = dict(params or {})
    out[RUNTIME_KEY] = {
        "backend": runtime.backend,
        "speed_mode": runtime.speed_mode,
        "profile": runtime.profile,
        "device": runtime.device,
        "n_jobs": runtime.n_jobs,
        "seed": runtime.seed,
    }
    return out


def split_runtime_params(params: Dict[str, Any] | None) -> tuple[Dict[str, Any], RuntimeOptions]:
    cfg = dict(params or {})
    runtime_raw = cfg.pop(RUNTIME_KEY, {}) or {}
    runtime = RuntimeOptions(
        backend=_normalize_backend(runtime_raw.get("backend", "auto")),
        speed_mode=_normalize_speed_mode(runtime_raw.get("speed_mode", "exact")),
        profile=bool(runtime_raw.get("profile", False)),
        device=str(runtime_raw.get("device", "cpu")),
        n_jobs=max(1, int(runtime_raw.get("n_jobs", 1))),
        seed=runtime_raw.get("seed"),
    )
    return cfg, runtime


def resolve_backend(
    method: str,
    runtime: RuntimeOptions,
    *,
    native_methods: Sequence[str] = (),
) -> str:
    if runtime.backend == "python":
        return "python"
    if runtime.backend == "gpu":
        raise ValueError(f"{method} does not provide a GPU backend.")

    native_ready = native_extension_available() and all(
        has_native_method(name) for name in native_methods
    )
    if runtime.backend == "native":
        if native_ready:
            return "native"
        import_error = native_import_error()
        detail = f" Native import error: {import_error}" if import_error else ""
        missing = [name for name in native_methods if not has_native_method(name)]
        raise RuntimeError(
            f"{method} requested backend='native' but the native implementation is unavailable."
            f" Missing exports: {missing}.{detail}"
        )

    if runtime.backend == "auto" and native_ready:
        return "native"
    return "python"


def result_from_native_payload(payload: Any, *, method: str) -> DecompResult:
    if isinstance(payload, DecompResult):
        return payload

    if isinstance(payload, Mapping):
        meta = dict(payload.get("meta", {}) or {})
        payload_method = meta.get("method")
        if payload_method not in (None, method):
            meta.setdefault("native_method", str(payload_method))
        meta["method"] = method
        return DecompResult(
            trend=np.asarray(payload.get("trend", []), dtype=float),
            season=np.asarray(payload.get("season", []), dtype=float),
            residual=np.asarray(payload.get("residual", []), dtype=float),
            components={
                str(key): np.asarray(val, dtype=float)
                for key, val in dict(payload.get("components", {}) or {}).items()
            },
            meta=meta,
        )

    if isinstance(payload, (tuple, list)) and len(payload) >= 3:
        return DecompResult(
            trend=np.asarray(payload[0], dtype=float),
            season=np.asarray(payload[1], dtype=float),
            residual=np.asarray(payload[2], dtype=float),
            meta={"method": method},
        )

    raise TypeError(f"Unsupported native payload for method '{method}': {type(payload)!r}")


def finalize_result(
    result: DecompResult,
    *,
    method: str,
    runtime: RuntimeOptions,
    backend_used: str,
    started_at: float | None = None,
) -> DecompResult:
    meta = dict(result.meta or {})
    meta.setdefault("method", method)
    meta["backend_requested"] = runtime.backend
    meta["backend_used"] = backend_used
    meta["speed_mode"] = runtime.speed_mode
    if runtime.profile and started_at is not None:
        meta["runtime_ms"] = round((perf_counter() - started_at) * 1000.0, 3)
    result.meta = meta
    return result
