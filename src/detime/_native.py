from __future__ import annotations

from importlib import import_module
from importlib import util as importlib_util
from importlib.machinery import EXTENSION_SUFFIXES
from importlib.metadata import PackageNotFoundError, distribution
import sys
from types import ModuleType
from typing import Any, Dict

_MODULE: ModuleType | None = None
_IMPORT_ERROR: Exception | None = None


def _load_installed_extension() -> ModuleType | None:
    """Load the packaged native extension when running from an unbuilt source tree."""
    try:
        dist = distribution("de-time")
    except PackageNotFoundError:
        return None

    for file in dist.files or ():
        path_parts = tuple(file.parts)
        if len(path_parts) != 2 or path_parts[0] != "detime":
            continue
        if not path_parts[1].startswith("_detime_native"):
            continue
        if not any(path_parts[1].endswith(suffix) for suffix in EXTENSION_SUFFIXES):
            continue

        extension_path = dist.locate_file(file)
        spec = importlib_util.spec_from_file_location("detime._detime_native", extension_path)
        if spec is None or spec.loader is None:
            continue
        module = importlib_util.module_from_spec(spec)
        sys.modules["detime._detime_native"] = module
        spec.loader.exec_module(module)
        return module
    return None


for _module_name in (
    "detime._detime_native",
    "_detime_native",
    "tsdecomp._tsdecomp_native",
    "_tsdecomp_native",
):
    try:
        _MODULE = import_module(_module_name)
        _IMPORT_ERROR = None
        break
    except Exception as exc:  # pragma: no cover - import error depends on env/build
        _IMPORT_ERROR = exc
if _MODULE is None:
    try:
        _MODULE = _load_installed_extension()
        _IMPORT_ERROR = None if _MODULE is not None else _IMPORT_ERROR
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
