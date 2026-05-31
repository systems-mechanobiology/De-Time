from __future__ import annotations

"""Run the first two decomposition-first quant columns end to end."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.quant_trading.data import (
    fetch_yahoo_ohlcv_panel,
    load_sample_goog_ohlcv,
    market_data_manifest,
    ohlcv_audit_report,
)
from examples.quant_trading.decomposition_features import build_feature_table, estimate_dominant_period
from examples.quant_trading.features import walkforward_decompose_ohlcv
from examples.quant_trading.strategy_baselines import run_classical_baselines
from examples.quant_trading.strategy_detime import compare_classical_and_detime, run_detime_trend_baselines
from examples.quant_trading.validation import write_run_audit


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Quant Column 01 and 02 with real data.")
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
    p.add_argument(
        "--use-bundled-sample",
        action="store_true",
        help="Use the bundled historical GOOG sample for offline execution.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    if args.use_bundled_sample:
        sample = load_sample_goog_ohlcv(trim_start="2014-01-01")
        ticker = str(sample.attrs.get("symbol", "GOOG"))
        ohlcv = {field: sample[[field]].rename(columns={field: ticker}) for field in ["Open", "High", "Low", "Close", "Volume"]}
        source = sample.attrs.get("source", "bundled real sample")
        manifest = market_data_manifest(tickers=[ticker], start="2014-01-01", end="2018-01-02", interval="1d", source=source)
    else:
        ohlcv = fetch_yahoo_ohlcv_panel(args.tickers, start=args.start, end=args.end, interval=args.interval, cache_dir=args.cache_dir)
        manifest = market_data_manifest(tickers=args.tickers, start=args.start, end=args.end, interval=args.interval)

    close = ohlcv["Close"]
    audit = ohlcv_audit_report(ohlcv)

    period_rows = []
    for ticker in close.columns:
        scored = estimate_dominant_period(close[ticker], candidates=(21, 42, 63, 126), use_log=True)
        period_rows.append({"ticker": ticker, "period": scored.period, "score": scored.score, "source": scored.source})
    import pandas as pd

    period_table = pd.DataFrame(period_rows)
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
    feature_table.tail(60).to_csv(report_dir / "column_01_feature_table_tail.csv")

    classical = run_classical_baselines(close, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    detime = run_detime_trend_baselines(close, features, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    comparison = compare_classical_and_detime(classical, detime)
    write_run_audit(report_dir, data_manifest=manifest, audit=audit, strategy_stats=comparison, prefix="column_01_02")
    print(comparison[["strategy_group", "cagr", "sharpe", "max_drawdown", "average_turnover"]].round(4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
