from __future__ import annotations

"""Download real Yahoo Finance OHLCV data for the quant trading tutorials.

Example
-------
python examples/quant_trading/scripts/download_real_market_data.py \
  --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD \
  --start 2018-01-01 \
  --cache-dir examples/quant_trading/data/cache \
  --report-dir examples/quant_trading/reports
"""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from examples.quant_trading.data import fetch_yahoo_ohlcv_panel, market_data_manifest, ohlcv_audit_report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download real OHLCV data for De-Time quant tutorials.")
    p.add_argument("--tickers", nargs="+", default=["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "XLK", "XLE", "TLT", "GLD"])
    p.add_argument("--start", default="2018-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--interval", default="1d")
    p.add_argument("--cache-dir", default="examples/quant_trading/data/cache")
    p.add_argument("--report-dir", default="examples/quant_trading/reports")
    p.add_argument("--allow-partial", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cache_dir = Path(args.cache_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    ohlcv = fetch_yahoo_ohlcv_panel(
        args.tickers,
        start=args.start,
        end=args.end,
        interval=args.interval,
        cache_dir=cache_dir,
        allow_partial=args.allow_partial,
    )
    audit = ohlcv_audit_report(ohlcv)
    manifest = market_data_manifest(tickers=args.tickers, start=args.start, end=args.end, interval=args.interval)
    audit.to_csv(report_dir / "column_01_02_real_data_audit.csv", index=False)
    manifest.to_csv(report_dir / "column_01_02_real_data_manifest.csv", index=False)
    print(f"downloaded fields: {', '.join(k for k in ohlcv.keys() if not k.startswith('_'))}")
    print(f"cache dir: {cache_dir}")
    print(f"audit: {report_dir / 'column_01_02_real_data_audit.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
