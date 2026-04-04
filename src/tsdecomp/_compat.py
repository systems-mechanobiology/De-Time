from __future__ import annotations

import sys
import warnings

IMPORT_MESSAGE = (
    "The 'tsdecomp' package is deprecated and will be removed in a future release. "
    "Install 'de-time' and import 'detime' instead."
)

CLI_MESSAGE = (
    "DeprecationWarning: 'tsdecomp' is a legacy CLI alias. Use 'detime' instead."
)


def warn_deprecated_import() -> None:
    warnings.warn(IMPORT_MESSAGE, DeprecationWarning, stacklevel=2)


def print_deprecated_cli_notice() -> None:
    warnings.warn(IMPORT_MESSAGE, DeprecationWarning, stacklevel=2)
    print(CLI_MESSAGE, file=sys.stderr)
