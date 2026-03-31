from ._native import native_capabilities, native_extension_available
from .core import DecompositionConfig, DecompResult
from .registry import decompose, MethodRegistry

# Import all methods to trigger registration
from . import methods

__all__ = [
    "DecompositionConfig",
    "DecompResult",
    "MethodRegistry",
    "decompose",
    "native_capabilities",
    "native_extension_available",
]
