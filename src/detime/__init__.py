"""De-Time public import surface.

This package is a thin compatibility-first shim over the legacy ``tsdecomp``
implementation so the project can rebrand without immediately breaking older
imports or downstream integrations.
"""

from tsdecomp import MethodRegistry, decompose
from tsdecomp._native import native_capabilities, native_extension_available
from tsdecomp.core import DecompositionConfig, DecompResult

__all__ = [
    "DecompositionConfig",
    "DecompResult",
    "MethodRegistry",
    "decompose",
    "native_capabilities",
    "native_extension_available",
]
