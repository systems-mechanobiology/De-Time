from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import PathFinder
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

spec = PathFinder.find_spec("detime", [str(SRC)])
if spec is not None and spec.loader is not None:
    module = importlib.util.module_from_spec(spec)
    sys.modules["detime"] = module
    spec.loader.exec_module(module)

from detime.schemas import write_schema_assets


def main() -> int:
    written = write_schema_assets()
    for name, path in written.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
