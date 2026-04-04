"""De-Time public import surface."""

from importlib.metadata import PackageNotFoundError, version

from ._native import native_capabilities, native_extension_available
from .core import DecompositionConfig, DecompResult
from .registry import MethodRegistry, decompose

# Import methods so their registry decorators run on package import.
from . import methods  # noqa: F401

try:
    __version__ = version("de-time")
except PackageNotFoundError:  # pragma: no cover - editable source tree fallback
    __version__ = "0.1.0"

__all__ = [
    "DecompositionConfig",
    "DecompResult",
    "MethodRegistry",
    "__version__",
    "decompose",
    "native_capabilities",
    "native_extension_available",
]
