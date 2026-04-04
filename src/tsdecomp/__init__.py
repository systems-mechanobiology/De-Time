from ._compat import warn_deprecated_import

warn_deprecated_import()

from detime import MethodRegistry, __version__, decompose
from detime._native import native_capabilities, native_extension_available
from detime.core import DecompositionConfig, DecompResult

__all__ = [
    "DecompositionConfig",
    "DecompResult",
    "MethodRegistry",
    "__version__",
    "decompose",
    "native_capabilities",
    "native_extension_available",
]
