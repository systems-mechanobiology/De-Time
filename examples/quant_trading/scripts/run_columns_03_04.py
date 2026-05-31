from __future__ import annotations

"""Run Columns 03-04 end to end on one shared OHLCV feature set."""

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT, ROOT / "examples"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from examples.quant_trading.data import fetch_yahoo_ohlcv_panel, load_sample_goog_ohlcv, market_data_manifest, ohlcv_audit_report
from examples.quant_trading.features import build_feature_table, walkforward_decompose_ohlcv
from examples.quant_trading.strategy_breakout import (
    breakout_diagnostic_table,
    compare_breakout_suites,
    run_classical_breakout_baselines,
    run_detime_breakout_baselines,
)
from examples.quant_trading.strategy_mean_reversion import (
    compare_mean_reversion_suites,
    run_classical_mean_reversion_baselines,
    run_detime_mean_reversion_baselines,
)
from examples.quant_trading.validation import write_run_audit, write_run_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Quant Columns 03 and 04 with real data.")
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
    p.add_argument("--allow-short", action="store_true", default=False, help="Allow symmetric short positions where supported.")
    p.add_argument("--use-bundled-sample", action="store_true", help="Use bundled real GOOG OHLCV for offline execution.")
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
    build_feature_table(prices, features).tail(120).to_csv(report_dir / "column_03_04_feature_table_tail.csv")

    classical_03 = run_classical_mean_reversion_baselines(prices, allow_short=args.allow_short, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    detime_03 = run_detime_mean_reversion_baselines(prices, features, allow_short=args.allow_short, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    comparison_03 = compare_mean_reversion_suites(classical_03, detime_03)
    comparison_03.to_csv(report_dir / "column_03_strategy_comparison.csv")
    write_run_audit(report_dir, data_manifest=manifest, audit=audit, strategy_stats=comparison_03, prefix="column_03")

    classical_04 = run_classical_breakout_baselines(ohlcv, allow_short=args.allow_short, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    detime_04 = run_detime_breakout_baselines(ohlcv, features, allow_short=args.allow_short, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    comparison_04 = compare_breakout_suites(classical_04, detime_04)
    comparison_04.to_csv(report_dir / "column_04_strategy_comparison.csv")
    breakout_diagnostic_table(ohlcv, features).to_csv(report_dir / "column_04_breakout_diagnostics.csv", index=False)
    write_run_audit(report_dir, data_manifest=manifest, audit=audit, strategy_stats=comparison_04, prefix="column_04")

    merged = pd.concat([comparison_03.assign(column="03_residual_mean_reversion"), comparison_04.assign(column="04_breakout")], axis=0)
    merged.to_csv(report_dir / "column_03_04_strategy_comparison.csv")
    write_run_manifest(
        report_dir / "column_03_04_run_manifest.json",
        command="python examples/quant_trading/scripts/run_columns_03_04.py",
        dataset="market_ohlcv",
        strategies=list(merged.index),
        result_file=str(report_dir / "column_03_04_strategy_comparison.csv"),
    )
    print("Columns 03-04 finished")
    print(merged[["column", "strategy_group", "cagr", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
