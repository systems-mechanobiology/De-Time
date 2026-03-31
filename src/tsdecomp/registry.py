from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any, Literal

import numpy as np

from .backends import inject_runtime_params, runtime_options_from_config
from .core import DecompResult, DecompositionConfig

InputMode = Literal["univariate", "multivariate", "channelwise"]
MethodSignature = Callable[[np.ndarray, Dict[str, Any]], DecompResult]


@dataclass(frozen=True)
class MethodSpec:
    func: MethodSignature
    input_mode: InputMode = "univariate"


class MethodRegistry:
    _methods: Dict[str, MethodSpec] = {}

    @classmethod
    def register(cls, name: str, *, input_mode: InputMode = "univariate"):
        def decorator(func: MethodSignature):
            cls._methods[name.upper()] = MethodSpec(func=func, input_mode=input_mode)
            return func

        return decorator

    @classmethod
    def get_spec(cls, name: str) -> MethodSpec:
        name = name.upper()
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
        return list(cls._methods.keys())


def _normalize_input(series: np.ndarray) -> np.ndarray:
    arr = np.asarray(series, dtype=float)
    if arr.ndim == 0:
        return arr.reshape(1)
    if arr.ndim > 2:
        raise ValueError(
            f"tsdecomp expects a 1D or 2D array, got shape {arr.shape}."
        )
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
    """
    Main entry point for decomposition.
    """
    spec = MethodRegistry.get_spec(config.method)
    x = _normalize_input(series)
    _validate_input_mode(config.method, x, spec.input_mode)
    runtime = runtime_options_from_config(config)
    params = inject_runtime_params(config.params, runtime)
    result = spec.func(x, params)
    channel_names = list(config.channel_names or [])
    return _annotate_result_layout(result, x, channel_names or None)
