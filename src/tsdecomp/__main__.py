import os

from .cli import main


if __name__ == "__main__":
    os.environ["DETIME_CLI_BRAND"] = "tsdecomp"
    main()
