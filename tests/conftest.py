from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _install_pywt_stub() -> None:
    if "pywt" in sys.modules:
        return
    sys.modules["pywt"] = ModuleType("pywt")


_install_pywt_stub()
