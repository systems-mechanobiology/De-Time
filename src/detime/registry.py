from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Literal

import numpy as np

from .backends import inject_runtime_params, runtime_options_from_config
from .core import DecompResult, DecompositionConfig

InputMode = Literal["univariate", "multivariate", "channelwise"]
MethodSignature = Callable[[np.ndarray, Dict[str, Any]], DecompResult]

REMOVED_METHOD_HINTS: Dict[str, str] = {
    "DR_TS_REG": (
        "DR_TS_REG moved to the separate 'de-time-bench' repository. "
        "Install that package and use 'detime_bench' instead."
    ),
    "DR_TS_AE": (
        "DR_TS_AE moved to the separate 'de-time-bench' repository. "
        "Install that package and use 'detime_bench' instead."
    ),
    "SL_LIB": (
        "SL_LIB moved to the separate 'de-time-bench' repository. "
        "Install that package and use 'detime_bench' instead."
    ),
}

METHOD_METADATA: Dict[str, Dict[str, Any]] = {
    "SSA": {
        "family": "SSA",
        "maturity": "flagship",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": True,
        "min_length": 24,
        "summary": "Singular spectrum analysis for structured univariate decomposition.",
        "recommended_for": [
            "accuracy-first univariate decomposition",
            "component recovery",
            "season-trend separation with structured signals",
        ],
        "typical_failure_modes": [
            "window too small for the dominant period",
            "rank or grouping chosen inconsistently with the signal structure",
        ],
    },
    "STD": {
        "family": "SeasonalTrend",
        "maturity": "flagship",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "channelwise",
        "native_backed": True,
        "min_length": 8,
        "summary": "Fast seasonal-trend decomposition with dispersion-aware diagnostics.",
        "recommended_for": [
            "fast seasonal-trend baselines",
            "channelwise multivariate workflows",
            "native-backed production paths",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "shared seasonal structure changing too quickly across cycles",
        ],
    },
    "STDR": {
        "family": "SeasonalTrend",
        "maturity": "flagship",
        "implementation": "native-backed",
        "dependency_tier": "core",
        "multivariate_support": "channelwise",
        "native_backed": True,
        "min_length": 8,
        "summary": "Robust seasonal-trend decomposition for noisier periodic signals.",
        "recommended_for": [
            "robust seasonal-trend decomposition",
            "channelwise multivariate workflows",
            "native-backed seasonal structure recovery",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "heavy structural breaks that violate shared seasonal assumptions",
        ],
    },
    "MSSA": {
        "family": "SSA",
        "maturity": "flagship",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "shared-model",
        "native_backed": False,
        "min_length": 24,
        "summary": "Multivariate SSA for shared-structure decomposition across channels.",
        "recommended_for": [
            "multivariate component recovery",
            "shared seasonal structure across channels",
            "accuracy-first multivariate workflows",
        ],
        "typical_failure_modes": [
            "too few channels for MSSA",
            "window or rank too small for the shared structure",
        ],
    },
    "STL": {
        "family": "SeasonalTrend",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 12,
        "summary": "Classical STL wrapped into the De-Time workflow contract.",
        "recommended_for": [
            "classical seasonal-trend baselines",
            "statsmodels-compatible workflows",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "multiple seasonalities outside STL's basic assumptions",
        ],
    },
    "MSTL": {
        "family": "SeasonalTrend",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 24,
        "summary": "Statsmodels MSTL wrapped into the De-Time workflow surface.",
        "recommended_for": [
            "multiple seasonalities in univariate data",
            "classical decomposition baselines",
        ],
        "typical_failure_modes": [
            "seasonal periods not provided",
            "nonstationary structure beyond classical assumptions",
        ],
    },
    "ROBUST_STL": {
        "family": "SeasonalTrend",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 12,
        "summary": "Robust STL-style decomposition wrapped for reproducible workflows.",
        "recommended_for": [
            "outlier-prone seasonal-trend baselines",
            "classical robust decomposition",
        ],
        "typical_failure_modes": [
            "period omitted or mis-specified",
            "multiple strong seasonalities beyond the model assumptions",
        ],
    },
    "EMD": {
        "family": "EMD",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "Empirical mode decomposition under the De-Time result contract.",
        "recommended_for": [
            "adaptive decomposition of nonlinear signals",
            "IMF-oriented exploratory analysis",
        ],
        "typical_failure_modes": [
            "mode mixing",
            "short or heavily noisy series that destabilize IMF extraction",
        ],
    },
    "CEEMDAN": {
        "family": "EMD",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 24,
        "summary": "Noise-assisted EMD variant for more stable IMF extraction.",
        "recommended_for": [
            "noise-assisted EMD workflows",
            "adaptive decomposition with improved IMF stability",
        ],
        "typical_failure_modes": [
            "high runtime on long series",
            "parameter choices that over-fragment signal modes",
        ],
    },
    "VMD": {
        "family": "Variational",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 24,
        "summary": "Variational mode decomposition integrated into the common workflow layer.",
        "recommended_for": [
            "band-limited mode separation",
            "frequency-structured univariate workflows",
        ],
        "typical_failure_modes": [
            "number of modes chosen poorly",
            "penalty parameters not aligned with the signal bandwidth",
        ],
    },
    "WAVELET": {
        "family": "Wavelet",
        "maturity": "stable",
        "implementation": "wrapper",
        "dependency_tier": "core-upstream",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 8,
        "summary": "Wavelet-based decomposition exposed through the common output contract.",
        "recommended_for": [
            "multiscale exploratory analysis",
            "wavelet-style trend and detail separation",
        ],
        "typical_failure_modes": [
            "wavelet family mismatch",
            "boundary artifacts on short series",
        ],
    },
    "MA_BASELINE": {
        "family": "Baseline",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 4,
        "summary": "Simple moving-average baseline for smoke tests and lightweight workflows.",
        "recommended_for": [
            "sanity checks",
            "lightweight baseline decomposition",
        ],
        "typical_failure_modes": [
            "window too large for the series length",
            "oversmoothing when fine seasonal structure matters",
        ],
    },
    "GABOR_CLUSTER": {
        "family": "Experimental",
        "maturity": "experimental",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": "univariate",
        "native_backed": False,
        "min_length": 16,
        "summary": "Experimental clustering-based decomposition path.",
        "recommended_for": [
            "research prototypes",
            "exploratory clustering-style decomposition",
        ],
        "typical_failure_modes": [
            "unstable clustering assignments",
            "parameter sensitivity on short series",
        ],
    },
    "MVMD": {
        "family": "Variational",
        "maturity": "optional-backend",
        "implementation": "optional-backend",
        "dependency_tier": "optional-backend",
        "multivariate_support": "shared-model",
        "native_backed": False,
        "min_length": 24,
        "summary": "Optional multivariate VMD backend for shared frequency structure.",
        "recommended_for": [
            "multivariate variational decomposition",
            "shared frequency structure across channels",
        ],
        "typical_failure_modes": [
            "optional backend unavailable",
            "mode count or penalties not tuned to the signal family",
        ],
    },
    "MEMD": {
        "family": "EMD",
        "maturity": "optional-backend",
        "implementation": "optional-backend",
        "dependency_tier": "optional-backend",
        "multivariate_support": "shared-model",
        "native_backed": False,
        "min_length": 24,
        "summary": "Optional multivariate EMD backend for shared oscillatory structure.",
        "recommended_for": [
            "multivariate adaptive decomposition",
            "shared oscillatory modes across channels",
        ],
        "typical_failure_modes": [
            "optional backend unavailable",
            "high runtime or unstable mode alignment across channels",
        ],
    },
}


def _fallback_metadata(name: str, input_mode: InputMode) -> Dict[str, Any]:
    multivariate_support = "univariate"
    if input_mode == "multivariate":
        multivariate_support = "shared-model"
    elif input_mode == "channelwise":
        multivariate_support = "channelwise"
    return {
        "family": "Other",
        "maturity": "stable",
        "implementation": "python",
        "dependency_tier": "core",
        "multivariate_support": multivariate_support,
        "native_backed": False,
        "min_length": 8,
        "summary": f"{name} decomposition exposed through the De-Time workflow surface.",
        "recommended_for": ["general decomposition workflows"],
        "typical_failure_modes": ["parameter choices misaligned with the signal structure"],
    }


def _metadata_for_method(name: str, input_mode: InputMode) -> Dict[str, Any]:
    base = dict(METHOD_METADATA.get(name, _fallback_metadata(name, input_mode)))
    base["input_mode"] = input_mode
    return base


@dataclass(frozen=True)
class MethodSpec:
    func: MethodSignature
    input_mode: InputMode = "univariate"
    metadata: Dict[str, Any] = field(default_factory=dict)


class MethodRegistry:
    _methods: Dict[str, MethodSpec] = {}

    @classmethod
    def register(cls, name: str, *, input_mode: InputMode = "univariate"):
        normalized = name.upper()
        if normalized in REMOVED_METHOD_HINTS:
            raise RuntimeError(REMOVED_METHOD_HINTS[normalized])

        def decorator(func: MethodSignature):
            cls._methods[normalized] = MethodSpec(
                func=func,
                input_mode=input_mode,
                metadata=_metadata_for_method(normalized, input_mode),
            )
            return func

        return decorator

    @classmethod
    def get_spec(cls, name: str) -> MethodSpec:
        name = name.upper()
        if name in REMOVED_METHOD_HINTS:
            raise ValueError(REMOVED_METHOD_HINTS[name])
        if name not in cls._methods:
            raise ValueError(
                f"Unknown decomposition method: {name}. Available: {list(cls._methods.keys())}"
            )
        return cls._methods[name]

    @classmethod
    def get(cls, name: str) -> MethodSignature:
        return cls.get_spec(name).func

    @classmethod
    def get_input_mode(cls, name: str) -> InputMode:
        return cls.get_spec(name).input_mode

    @classmethod
    def is_multivariate_method(cls, name: str) -> bool:
        return cls.get_input_mode(name) != "univariate"

    @classmethod
    def list_methods(cls):
        return sorted(name for name in cls._methods.keys() if name not in REMOVED_METHOD_HINTS)

    @classmethod
    def get_metadata(cls, name: str) -> Dict[str, Any]:
        return dict(cls.get_spec(name).metadata)

    @classmethod
    def list_catalog(cls) -> list[Dict[str, Any]]:
        catalog: list[Dict[str, Any]] = []
        for name in cls.list_methods():
            spec = cls.get_spec(name)
            entry = {"name": name}
            entry.update(spec.metadata)
            catalog.append(entry)
        return catalog


def _normalize_input(series: np.ndarray) -> np.ndarray:
    arr = np.asarray(series, dtype=float)
    if arr.ndim == 0:
        return arr.reshape(1)
    if arr.ndim > 2:
        raise ValueError(f"detime expects a 1D or 2D array, got shape {arr.shape}.")
    return arr


def _validate_input_mode(method: str, x: np.ndarray, input_mode: InputMode) -> None:
    if x.ndim == 1:
        if input_mode == "multivariate":
            raise ValueError(
                f"{method} requires 2D input with shape (T, C). Received 1D input with shape {x.shape}."
            )
        return
    if input_mode in {"multivariate", "channelwise"}:
        return
    raise ValueError(
        f"{method} only supports 1D input. Received 2D input with shape {x.shape}. "
        "Use a multivariate method such as MSSA/MVMD/MEMD or a channelwise-capable method."
    )


def _annotate_result_layout(
    result: DecompResult,
    x: np.ndarray,
    channel_names: list[str] | None,
) -> DecompResult:
    meta = dict(result.meta or {})
    meta.setdefault("input_shape", [int(v) for v in x.shape])
    if x.ndim == 1:
        meta.setdefault("result_layout", "univariate")
        meta.setdefault("n_channels", 1)
        if channel_names:
            meta.setdefault("channel_names", channel_names[:1])
    else:
        meta.setdefault("result_layout", "multivariate")
        meta.setdefault("n_channels", int(x.shape[1]))
        if channel_names:
            meta.setdefault("channel_names", channel_names)
    result.meta = meta
    return result


def decompose(series: np.ndarray, config: DecompositionConfig) -> DecompResult:
    """Main entry point for decomposition."""
    spec = MethodRegistry.get_spec(config.method)
    x = _normalize_input(series)
    _validate_input_mode(config.method, x, spec.input_mode)
    runtime = runtime_options_from_config(config)
    params = inject_runtime_params(config.params, runtime)
    result = spec.func(x, params)
    channel_names = list(config.channel_names or [])
    return _annotate_result_layout(result, x, channel_names or None)
