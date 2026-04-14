from __future__ import annotations

import sys
import warnings

from detime._metadata import (
    CANONICAL_IMPORT,
    DISTRIBUTION_NAME,
    LEGACY_COMPATIBILITY_SERIES,
    LEGACY_EARLIEST_REMOVAL,
    LEGACY_IMPORT,
)

IMPORT_MESSAGE = (
    f"The '{LEGACY_IMPORT}' package is deprecated, supported only through "
    f"{LEGACY_COMPATIBILITY_SERIES}, and may be removed in {LEGACY_EARLIEST_REMOVAL}. "
    f"Install '{DISTRIBUTION_NAME}' and import '{CANONICAL_IMPORT}' instead."
)

CLI_MESSAGE = (
    f"DeprecationWarning: '{LEGACY_IMPORT}' is a legacy CLI alias supported only through "
    f"{LEGACY_COMPATIBILITY_SERIES}. Use '{CANONICAL_IMPORT}' instead."
)


def warn_deprecated_import() -> None:
    warnings.warn(IMPORT_MESSAGE, DeprecationWarning, stacklevel=2)


def print_deprecated_cli_notice() -> None:
    warnings.warn(IMPORT_MESSAGE, DeprecationWarning, stacklevel=2)
    print(CLI_MESSAGE, file=sys.stderr)
