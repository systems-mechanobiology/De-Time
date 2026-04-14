from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

PRODUCT_NAME = "De-Time"
DISTRIBUTION_NAME = "de-time"
CANONICAL_IMPORT = "detime"
LEGACY_IMPORT = "tsdecomp"
FALLBACK_VERSION = "0.1.1"
LEGACY_COMPATIBILITY_SERIES = "0.1.x"
LEGACY_EARLIEST_REMOVAL = "0.2.0"
MACHINE_CONTRACT_VERSION = "0.1"


def installed_version() -> str:
    try:
        return version(DISTRIBUTION_NAME)
    except PackageNotFoundError:  # pragma: no cover - editable source tree fallback
        return FALLBACK_VERSION

