import os

from detime.cli import main as _detime_main

from ._compat import print_deprecated_cli_notice


def main():
    os.environ["DETIME_CLI_BRAND"] = "tsdecomp"
    print_deprecated_cli_notice()
    _detime_main()


__all__ = ["main"]
