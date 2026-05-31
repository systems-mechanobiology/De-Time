from __future__ import annotations

"""Run only Column 02: classical MA/MACD baselines vs De-Time rewrites."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from examples.quant_trading.data import (
    fetch_yahoo_ohlcv_panel,
    load_sample_goog_ohlcv,
    market_data_manifest,
    ohlcv_audit_report,
)
from examples.quant_trading.features import walkforward_decompose_ohlcv
from examples.quant_trading.strategy_baselines import run_classical_baselines
from examples.quant_trading.strategy_detime import compare_classical_and_detime, run_detime_trend_baselines
from examples.quant_trading.validation import write_run_audit


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Column 02 strategy comparison.")
    p.add_argument("--tickers", nargs="+", default=["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "XLK", "XLE", "TLT", "GLD"])
    p.add_argument("--start", default="2018-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--interval", default="1d")
    p.add_argument("--cache-dir", default="examples/quant_trading/data/cache")
    p.add_argument("--report-dir", default="examples/quant_trading/reports")
    p.add_argument("--method", default="STL")
    p.add_argument("--train-window", type=int, default=252)
    p.add_argument("--step", type=int, default=21)
    p.add_argument("--fee-bps", type=float, default=1.0)
    p.add_argument("--slippage-bps", type=float, default=2.0)
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
    prices = ohlcv["Close"]
    audit = ohlcv_audit_report(ohlcv)
    features = walkforward_decompose_ohlcv(
        ohlcv,
        method=args.method,
        period="auto",
        period_candidates=(21, 42, 63, 126),
        train_window=args.train_window,
        step=args.step,
    )
    classical = run_classical_baselines(prices, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    detime = run_detime_trend_baselines(prices, features, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    comparison = compare_classical_and_detime(classical, detime)
    comparison.to_csv(report_dir / "column_02_strategy_comparison.csv")
    write_run_audit(report_dir, data_manifest=manifest, audit=audit, strategy_stats=comparison, prefix="column_02")
    print("Column 02 finished")
    print(comparison[["strategy_group", "cagr", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
