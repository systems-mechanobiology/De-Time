from __future__ import annotations

"""Compatibility smoke entrypoint for the quant-trading examples."""

from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT / "examples"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

if __name__ == "__main__":
    target = Path(__file__).with_name("smoke_quant_columns_01_02.py")
    ns = runpy.run_path(str(target))
    raise SystemExit(ns["main"]())
