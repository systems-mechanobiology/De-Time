from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
EXAMPLES = ROOT / "examples"
for path in (SRC, EXAMPLES):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from quant_trading.data import DEFAULT_UNIVERSES, resolve_universe  # noqa: E402
from quant_trading.backtest import summarize_returns  # noqa: E402


def main() -> int:
    assert "us_large_cap" in DEFAULT_UNIVERSES
    assert "005930.KS" in resolve_universe("korea_large_cap")
    stats = summarize_returns(__import__("pandas").Series([0.01, -0.005, 0.002]))
    assert "sharpe" in stats
    print("quant trading tutorial smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
