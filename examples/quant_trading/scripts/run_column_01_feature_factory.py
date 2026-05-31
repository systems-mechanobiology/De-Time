from __future__ import annotations

"""Run only Column 01: real OHLCV audit and De-Time price/volume features."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import pandas as pd

from examples.quant_trading.data import (
    fetch_yahoo_ohlcv_panel,
    load_sample_goog_ohlcv,
    market_data_manifest,
    ohlcv_audit_report,
)
from examples.quant_trading.features import (
    build_feature_table,
    feature_coverage_report,
    period_score_table,
    walkforward_decompose_ohlcv,
)
from examples.quant_trading.validation import write_run_audit


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Column 01 feature factory.")
    p.add_argument("--tickers", nargs="+", default=["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "XLK", "XLE", "TLT", "GLD"])
    p.add_argument("--start", default="2018-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--interval", default="1d")
    p.add_argument("--cache-dir", default="examples/quant_trading/data/cache")
    p.add_argument("--report-dir", default="examples/quant_trading/reports")
    p.add_argument("--method", default="STL")
    p.add_argument("--train-window", type=int, default=252)
    p.add_argument("--step", type=int, default=21)
    p.add_argument("--use-bundled-sample", action="store_true", help="Use bundled real GOOG OHLCV for offline smoke tests.")
    return p.parse_args()


def _load_ohlcv(args: argparse.Namespace):
    if args.use_bundled_sample:
        sample = load_sample_goog_ohlcv(trim_start="2014-01-01")
        ticker = str(sample.attrs.get("symbol", "GOOG"))
        panels = {field: sample[[field]].rename(columns={field: ticker}) for field in ["Open", "High", "Low", "Close", "Volume"]}
        manifest = market_data_manifest(tickers=[ticker], start="2014-01-01", end="2018-01-02", interval="1d", source=sample.attrs.get("source", "bundled real sample"))
        return panels, manifest
    panels = fetch_yahoo_ohlcv_panel(args.tickers, start=args.start, end=args.end, interval=args.interval, cache_dir=args.cache_dir)
    manifest = market_data_manifest(tickers=args.tickers, start=args.start, end=args.end, interval=args.interval)
    return panels, manifest


def main() -> int:
    args = parse_args()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    ohlcv, manifest = _load_ohlcv(args)
    close = ohlcv["Close"]
    audit = ohlcv_audit_report(ohlcv)
    period_tables = []
    for ticker in close.columns:
        table = period_score_table(close[ticker], candidates=(21, 42, 63, 126), transform="log")
        table.insert(0, "ticker", ticker)
        period_tables.append(table)
    period_table = pd.concat(period_tables, ignore_index=True)
    period_table.to_csv(report_dir / "column_01_period_candidates.csv", index=False)
    features = walkforward_decompose_ohlcv(
        ohlcv,
        method=args.method,
        period="auto",
        period_candidates=(21, 42, 63, 126),
        train_window=args.train_window,
        step=args.step,
    )
    feature_table = build_feature_table(close, features)
    coverage = feature_coverage_report(features)
    feature_table.tail(120).to_csv(report_dir / "column_01_feature_table_tail.csv")
    coverage.to_csv(report_dir / "column_01_feature_coverage.csv", index=False)
    write_run_audit(report_dir, data_manifest=manifest, audit=audit, prefix="column_01")
    print("Column 01 finished")
    print(coverage.sort_values("coverage", ascending=False).head(12).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
