from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any, Dict

_MODULE: ModuleType | None = None
_IMPORT_ERROR: Exception | None = None

for _module_name in ("tsdecomp._tsdecomp_native", "_tsdecomp_native"):
    try:
        _MODULE = import_module(_module_name)
        _IMPORT_ERROR = None
        break
    except Exception as exc:  # pragma: no cover - import error depends on env/build
        _IMPORT_ERROR = exc


def native_extension_available() -> bool:
    return _MODULE is not None


def native_import_error() -> Exception | None:
    return _IMPORT_ERROR


def native_capabilities() -> Dict[str, bool]:
    if _MODULE is None:
        return {}
    if hasattr(_MODULE, "capabilities"):
        data = getattr(_MODULE, "capabilities")()
        if isinstance(data, dict):
            return {str(key): bool(val) for key, val in data.items()}
    return {
        name: hasattr(_MODULE, name)
        for name in (
            "ssa_decompose",
            "dr_ts_reg_decompose",
            "std_decompose",
            "gabor_stft_rfft",
            "gabor_istft_rfft",
            "gabor_cluster_decompose",
        )
    }


def has_native_method(name: str) -> bool:
    return _MODULE is not None and hasattr(_MODULE, name)


def invoke_native(name: str, *args: Any, **kwargs: Any) -> Any:
    if _MODULE is None:
        raise RuntimeError("Native extension is not available.") from _IMPORT_ERROR
    if not hasattr(_MODULE, name):
        raise AttributeError(f"Native extension does not export '{name}'.")
    return getattr(_MODULE, name)(*args, **kwargs)
