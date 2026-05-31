from __future__ import annotations

"""Run Column 06: decomposition-aware cross-sectional rotation."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT, ROOT / "examples"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from examples.quant_trading.data import (  # noqa: E402
    fetch_yahoo_ohlcv_panel,
    load_bundled_real_ohlcv_panel,
    market_data_manifest,
    ohlcv_audit_report,
)
from examples.quant_trading.decomposition_features import build_feature_table, feature_coverage_report  # noqa: E402
from examples.quant_trading.features import walkforward_price_volume_features  # noqa: E402
from examples.quant_trading.strategy_baselines import buy_and_hold_weights  # noqa: E402
from examples.quant_trading.strategy_rotation import (  # noqa: E402
    classic_momentum_rotation_weights,
    compare_rotation_suites,
    detime_long_short_rotation_weights,
    detime_rotation_weights,
    make_classic_rotation_weight_grid,
    make_detime_rotation_weight_grid,
    rotation_diagnostic_table,
    volume_availability,
)
from examples.quant_trading.validation import turnover_report, write_run_audit, write_run_manifest  # noqa: E402
from examples.quant_trading.backtest import backtest_weights  # noqa: E402


BUNDLED_TICKERS = ["AUDUSD=X", "NZDUSD=X", "EURUSD=X", "GBPUSD=X"]
LIVE_SECTOR_ETFS = ["XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Column 06 cross-sectional rotation tutorial.")
    p.add_argument("--tickers", nargs="+", default=LIVE_SECTOR_ETFS)
    p.add_argument("--start", default="2018-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--interval", default="1d")
    p.add_argument("--cache-dir", default="examples/quant_trading/data/cache")
    p.add_argument("--report-dir", default="examples/quant_trading/reports")
    p.add_argument("--method", default="STL")
    p.add_argument("--period", default="63")
    p.add_argument("--train-window", type=int, default=252)
    p.add_argument("--step", type=int, default=63)
    p.add_argument("--top-n", type=int, default=3)
    p.add_argument("--rebalance", default="W-FRI")
    p.add_argument("--fee-bps", type=float, default=1.0)
    p.add_argument("--slippage-bps", type=float, default=2.0)
    p.add_argument("--use-bundled-sample", action="store_true", help="Use bundled real FX panel for offline execution.")
    return p.parse_args()


def _load_ohlcv(args: argparse.Namespace):
    if args.use_bundled_sample:
        panels = load_bundled_real_ohlcv_panel(BUNDLED_TICKERS, min_observations=120)
        # Keep the offline tutorial run bounded; live-data runs use the full downloaded range.
        panels = {field: table.tail(280).copy() for field, table in panels.items()}
        manifest = market_data_manifest(tickers=BUNDLED_TICKERS, start="2014-01-01", end="2018-01-02", interval="1d", source="Learn-Algorithmic-Trading bundled real Yahoo exports")
        return panels, manifest
    panels = fetch_yahoo_ohlcv_panel(args.tickers, start=args.start, end=args.end, interval=args.interval, cache_dir=args.cache_dir, allow_partial=True)
    manifest = market_data_manifest(tickers=args.tickers, start=args.start, end=args.end, interval=args.interval)
    return panels, manifest


def main() -> int:
    args = parse_args()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    print("column06: loading data", flush=True)
    ohlcv, manifest = _load_ohlcv(args)
    print("column06: data loaded", flush=True)
    prices = ohlcv["Close"]
    volumes = ohlcv.get("Volume")
    audit = ohlcv_audit_report(ohlcv)

    volumes_for_features = volumes if volume_availability(volumes) else None
    print("column06: building features", flush=True)
    features = walkforward_price_volume_features(
        prices,
        volumes_for_features,
        method=args.method,
        period=args.period if str(args.period).lower() == "auto" else int(args.period),
        train_window=args.train_window,
        step=args.step,
        z_window=min(63, max(21, args.train_window // 3)),
    )
    print("column06: features built", flush=True)
    feature_coverage_report(features).to_csv(report_dir / "column_06_feature_coverage.csv", index=False)
    build_feature_table(prices, features).tail(80).to_csv(report_dir / "column_06_feature_table_tail.csv")

    print("column06: running classical", flush=True)
    if args.use_bundled_sample:
        compact_top_n = min(args.top_n, 2, max(1, len(prices.columns) // 2))
        classical_weights = {
            "buy_hold_equal_weight": buy_and_hold_weights(prices),
            "classic_momentum_63_top": classic_momentum_rotation_weights(
                prices, lookback=63, top_n=compact_top_n, rebalance_freq=args.rebalance, vol_target=None
            ),
        }
    else:
        classical_weights = make_classic_rotation_weight_grid(prices, top_n=args.top_n, rebalance=args.rebalance)
    classical = {name: backtest_weights(prices, weights, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps) for name, weights in classical_weights.items()}
    print("column06: running detime", flush=True)
    if args.use_bundled_sample:
        compact_top_n = min(args.top_n, 2, max(1, len(prices.columns) // 2))
        detime_weights = {
            "detime_rotation_top_trend_cycle_residual_volume": detime_rotation_weights(
                prices, features, top_n=compact_top_n, rebalance_freq=args.rebalance, vol_target=None
            ),
            "detime_rotation_long_short": detime_long_short_rotation_weights(
                prices, features, top_n=compact_top_n, bottom_n=compact_top_n
            ),
        }
    else:
        detime_weights = make_detime_rotation_weight_grid(prices, features, top_n=args.top_n, rebalance=args.rebalance)
    print("column06: detime weights built", list(detime_weights.keys()), flush=True)
    detime = {}
    for name, weights in detime_weights.items():
        print(f"column06: backtesting {name}", flush=True)
        detime[name] = backtest_weights(prices, weights, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    print("column06: comparing", flush=True)
    comparison = compare_rotation_suites(classical, detime)
    comparison.to_csv(report_dir / "column_06_strategy_comparison.csv")

    print("column06: diagnostics", flush=True)
    diag = rotation_diagnostic_table(prices, features, tail=3)
    diag["input_volume_available"] = volume_availability(volumes)
    diag.to_csv(report_dir / "column_06_rotation_diagnostics.csv", index=False)
    diag.to_csv(report_dir / "column_06_factor_snapshot.csv", index=False)

    print("column06: turnover", flush=True)
    weights = {}
    weights.update(classical_weights)
    weights.update(detime_weights)
    turnover_report(weights).to_csv(report_dir / "column_06_turnover_report.csv")

    print("column06: writing audit", flush=True)
    write_run_audit(report_dir, data_manifest=manifest, audit=audit, strategy_stats=comparison, prefix="column_06")
    write_run_manifest(
        report_dir / "column_06_run_manifest.json",
        command="python examples/quant_trading/scripts/run_column_06_cross_sectional_rotation.py",
        dataset="market_ohlcv_rotation_universe",
        strategies=list(comparison.index),
        result_file=str(report_dir / "column_06_strategy_comparison.csv"),
    )
    print("Column 06 finished")
    print(comparison[["strategy_group", "cagr", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
