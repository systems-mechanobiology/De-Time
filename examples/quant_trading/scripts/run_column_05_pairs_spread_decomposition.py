from __future__ import annotations

"""Run Column 05: pair spread decomposition and stat-arb baselines."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT, ROOT / "examples"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import pandas as pd  # noqa: E402

from examples.quant_trading.data import (  # noqa: E402
    fetch_yahoo_ohlcv_panel,
    load_bundled_real_ohlcv_panel,
    market_data_manifest,
    ohlcv_audit_report,
)
from examples.quant_trading.strategy_pairs import (  # noqa: E402
    BUNDLED_REAL_PAIRS,
    DEFAULT_LIVE_PAIRS,
    make_classic_pair_weight_grid,
    make_detime_pair_weight_grid,
    pair_diagnostics,
    pair_feature_snapshot,
    run_classical_pair_baselines,
    run_detime_pair_baselines,
    walkforward_pair_spread_features,
)
from examples.quant_trading.validation import turnover_report, write_run_audit, write_run_manifest  # noqa: E402


BUNDLED_TICKERS = ["AUDUSD=X", "CADUSD=X", "CHFUSD=X", "EURUSD=X", "GBPUSD=X", "JPYUSD=X", "NZDUSD=X"]
LIVE_TICKERS = sorted({x for p in DEFAULT_LIVE_PAIRS for x in p})


def parse_pair_args(values: list[str] | None):
    if not values:
        return None
    pairs = []
    for item in values:
        if ":" not in item:
            raise ValueError("Pairs must be passed as ASSET_A:ASSET_B, for example KO:PEP")
        a, b = item.split(":", 1)
        pairs.append((a, b))
    return pairs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Column 05 pair spread decomposition tutorial.")
    p.add_argument("--tickers", nargs="+", default=LIVE_TICKERS)
    p.add_argument("--pairs", nargs="*", default=None, help="Pair specs as A:B.")
    p.add_argument("--start", default="2018-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--interval", default="1d")
    p.add_argument("--cache-dir", default="examples/quant_trading/data/cache")
    p.add_argument("--report-dir", default="examples/quant_trading/reports")
    p.add_argument("--method", default="STL")
    p.add_argument("--period", default="63")
    p.add_argument("--train-window", type=int, default=252)
    p.add_argument("--step", type=int, default=63)
    p.add_argument("--hedge-window", type=int, default=120)
    p.add_argument("--fee-bps", type=float, default=1.0)
    p.add_argument("--slippage-bps", type=float, default=2.0)
    p.add_argument("--use-bundled-sample", action="store_true", help="Use bundled real FX OHLCV for offline execution.")
    return p.parse_args()


def _load_ohlcv(args: argparse.Namespace):
    requested_pairs = parse_pair_args(args.pairs)
    if args.use_bundled_sample:
        pairs = tuple(requested_pairs or BUNDLED_REAL_PAIRS)
        tickers = sorted(set(BUNDLED_TICKERS) | {asset for pair in pairs for asset in pair})
        panels = load_bundled_real_ohlcv_panel(tickers, min_observations=120)
        manifest = market_data_manifest(tickers=tickers, start="2014-01-01", end="2018-01-02", interval="1d", source="Learn-Algorithmic-Trading bundled real Yahoo exports")
        return panels, manifest, pairs
    pairs = tuple(requested_pairs or DEFAULT_LIVE_PAIRS)
    tickers = sorted(set(args.tickers) | {asset for pair in pairs for asset in pair})
    panels = fetch_yahoo_ohlcv_panel(tickers, start=args.start, end=args.end, interval=args.interval, cache_dir=args.cache_dir, allow_partial=False)
    manifest = market_data_manifest(tickers=tickers, start=args.start, end=args.end, interval=args.interval)
    return panels, manifest, pairs


def main() -> int:
    args = parse_args()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    ohlcv, manifest, pairs = _load_ohlcv(args)
    prices = ohlcv["Close"]
    audit = ohlcv_audit_report(ohlcv)

    spread_features, spread_panel, beta_panel, pair_specs = walkforward_pair_spread_features(
        prices,
        pairs,
        hedge_window=args.hedge_window,
        method=args.method,
        period=args.period if str(args.period).lower() == "auto" else int(args.period),
        train_window=args.train_window,
        step=args.step,
        z_window=min(63, max(21, args.train_window // 3)),
    )
    spread_panel.to_csv(report_dir / "column_05_spread_panel.csv")
    beta_panel.to_csv(report_dir / "column_05_beta_panel.csv")
    pair_diagnostics(prices, pair_specs, hedge_window=args.hedge_window).to_csv(report_dir / "column_05_pair_diagnostics.csv", index=False)
    pair_feature_snapshot(spread_features, tail=5).to_csv(report_dir / "column_05_pair_feature_snapshot.csv", index=False)

    classical = run_classical_pair_baselines(prices, pair_specs, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    detime = run_detime_pair_baselines(
        prices,
        pair_specs,
        spread_features,
        spread_panel=spread_panel,
        beta_panel=beta_panel,
        fee_bps=args.fee_bps,
        slippage_bps=args.slippage_bps,
    )
    from examples.quant_trading.strategy_pairs import compare_pair_suites  # local import keeps CLI startup simple

    comparison = compare_pair_suites(classical, detime)
    comparison.to_csv(report_dir / "column_05_strategy_comparison.csv")
    weights = {}
    weights.update(make_classic_pair_weight_grid(prices, pair_specs))
    weights.update(make_detime_pair_weight_grid(prices, pair_specs, spread_features, spread_panel=spread_panel, beta_panel=beta_panel))
    turnover_report(weights).to_csv(report_dir / "column_05_turnover_report.csv")

    write_run_audit(report_dir, data_manifest=manifest, audit=audit, strategy_stats=comparison, prefix="column_05")
    write_run_manifest(
        report_dir / "column_05_run_manifest.json",
        command="python examples/quant_trading/scripts/run_column_05_pairs_spread_decomposition.py",
        dataset="market_ohlcv_pair_spreads",
        strategies=list(comparison.index),
        result_file=str(report_dir / "column_05_strategy_comparison.csv"),
    )
    print("Column 05 finished")
    print(comparison[["strategy_group", "cagr", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
