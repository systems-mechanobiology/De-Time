"""De-Time public import surface."""

from ._native import native_capabilities, native_extension_available
from ._metadata import installed_version
from .core import DecompositionConfig, DecompResult
from .registry import MethodRegistry, decompose

# Import methods so their registry decorators run on package import.
from . import methods  # noqa: F401

__version__ = installed_version()

__all__ = [
    "DecompositionConfig",
    "DecompResult",
    "MethodRegistry",
    "__version__",
    "decompose",
    "native_capabilities",
    "native_extension_available",
]
