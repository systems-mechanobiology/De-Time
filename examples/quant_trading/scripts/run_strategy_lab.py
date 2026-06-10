#!/usr/bin/env python
from __future__ import annotations

"""Run the concrete DeTime strategy lab on real OHLCV data.

The script intentionally produces trading artifacts, not just feature tables:
strategy signals, next-bar backtest metrics, order ledger, round-trip trades,
and buy/sell charts for the two core strategy families.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT / "examples") not in sys.path:
    sys.path.insert(0, str(ROOT / "examples"))

from quant_trading.data import fetch_yahoo_ohlcv, load_sample_goog_ohlcv, market_data_manifest, ohlcv_audit_report  # noqa: E402
from quant_trading.decomposition_features import feature_coverage_report, walkforward_price_volume_features  # noqa: E402
from quant_trading.strategy_baselines import (  # noqa: E402
    bollinger_mean_reversion_weights,
    buy_and_hold_weights,
    dual_moving_average_weights,
    macd_weights,
    rsi_mean_reversion_weights,
    turtle_breakout_weights,
)
from quant_trading.strategy_lab import (  # noqa: E402
    HybridRegimeConfig,
    OscillationReversionConfig,
    TrendFollowingConfig,
    backtest_signal_set,
    backtest_target_weights_next_bar,
    decomposition_hybrid_regime_signals,
    decomposition_oscillation_reversion_signals,
    decomposition_trend_following_signals,
    execution_price_panel,
    plot_signal_analysis,
    stats_table,
)


def _one_asset_panels(ohlcv: pd.DataFrame, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    close = ohlcv["Close"].rename(symbol).to_frame()
    open_ = ohlcv["Open"].rename(symbol).to_frame()
    high = ohlcv["High"].rename(symbol).to_frame()
    low = ohlcv["Low"].rename(symbol).to_frame()
    volume = ohlcv["Volume"].rename(symbol).to_frame()
    return close, open_, high, low, volume


def _load_data(args: argparse.Namespace) -> tuple[pd.DataFrame, str, str]:
    if args.csv:
        path = Path(args.csv)
        table = pd.read_csv(path, index_col=0, parse_dates=True)
        symbol = args.ticker or path.stem
        table.attrs["symbol"] = symbol
        table.attrs["source"] = f"user CSV: {path}"
        return table, symbol, table.attrs["source"]
    if args.use_bundled_sample:
        table = load_sample_goog_ohlcv(trim_start=args.start, trim_end=args.end)
        symbol = "GOOG"
        table.attrs["symbol"] = symbol
        return table, symbol, str(table.attrs.get("source", "bundled real GOOG sample"))
    symbol = args.ticker
    table = fetch_yahoo_ohlcv(
        symbol,
        start=args.start,
        end=args.end,
        interval=args.interval,
        auto_adjust=not args.no_auto_adjust,
        min_observations=args.min_observations,
        cache_dir=args.cache_dir,
    )
    table.attrs["symbol"] = symbol
    table.attrs["source"] = "Yahoo Finance via yfinance live download"
    return table, symbol, table.attrs["source"]


def _baseline_weights(close: pd.DataFrame, high: pd.DataFrame, low: pd.DataFrame, *, allow_short_reversion: bool) -> dict[str, pd.DataFrame]:
    return {
        "buy_hold": buy_and_hold_weights(close),
        "classic_sma_20_100": dual_moving_average_weights(close, fast=20, slow=100),
        "classic_macd_12_26_9": macd_weights(close, fast=12, slow=26, signal=9),
        "classic_turtle_55_20": turtle_breakout_weights(close, high=high, low=low, allow_short=False),
        "classic_bollinger_20_2": bollinger_mean_reversion_weights(close, window=20, entry_z=2.0, allow_short=allow_short_reversion),
        "classic_rsi_14": rsi_mean_reversion_weights(close, window=14, lower=30, upper=70, allow_short=allow_short_reversion),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", default="SPY", help="Ticker for live yfinance download, or label for --csv.")
    parser.add_argument("--csv", default=None, help="Optional user OHLCV CSV with Open/High/Low/Close/Volume columns.")
    parser.add_argument("--use-bundled-sample", action="store_true", help="Use archived real GOOG OHLCV sample for offline runs.")
    parser.add_argument("--start", default="2014-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--no-auto-adjust", action="store_true")
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--min-observations", type=int, default=180)
    parser.add_argument("--methods", nargs="+", default=["STL"], help="DeTime methods to run, e.g. STL SSA WAVELET STD.")
    parser.add_argument("--period", default="42", help="Integer period or 'auto'.")
    parser.add_argument("--train-window", type=int, default=180)
    parser.add_argument("--step", type=int, default=21)
    parser.add_argument("--z-window", type=int, default=63)
    parser.add_argument("--fee-bps", type=float, default=5.0)
    parser.add_argument("--slippage-bps", type=float, default=2.0)
    parser.add_argument("--periods-per-year", type=int, default=252)
    parser.add_argument("--allow-short-trend", action="store_true")
    parser.add_argument("--allow-short-reversion", action="store_true")
    parser.add_argument("--use-volume-filter", action="store_true", help="Apply volume filter to residual reversion entries.")
    parser.add_argument("--report-dir", default="examples/quant_trading/reports/strategy_lab")
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    charts_dir = report_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    ohlcv, symbol, source = _load_data(args)
    close, open_, high, low, volume = _one_asset_panels(ohlcv, symbol)
    execution_prices = execution_price_panel(ohlcv, field="Open", next_bar=True).rename(columns={ohlcv.attrs.get("symbol", "asset"): symbol})
    if list(execution_prices.columns) != [symbol]:
        execution_prices.columns = [symbol]

    ohlcv_audit_report(ohlcv, ticker=symbol).to_csv(report_dir / "strategy_lab_data_audit.csv", index=False)
    market_data_manifest(tickers=[symbol], start=args.start, end=args.end, interval=args.interval, source=source).to_csv(report_dir / "strategy_lab_market_data_manifest.csv", index=False)

    # Baselines use the same next-bar execution model as DeTime strategies.
    results = {}
    for name, weights in _baseline_weights(close, high, low, allow_short_reversion=args.allow_short_reversion).items():
        results[name] = backtest_target_weights_next_bar(
            close,
            weights,
            execution_prices=execution_prices,
            fee_bps=args.fee_bps,
            slippage_bps=args.slippage_bps,
            periods_per_year=args.periods_per_year,
            name=name,
        )

    feature_snapshots = []
    coverage_tables = []
    all_orders = []
    all_trades = []
    failed = []

    period_arg: int | str = args.period
    if isinstance(period_arg, str) and period_arg.lower() != "auto":
        period_arg = int(period_arg)

    for method in args.methods:
        method_name = method.upper()
        try:
            features = walkforward_price_volume_features(
                close,
                volume,
                method=method_name,
                period=period_arg,
                train_window=args.train_window,
                step=args.step,
                z_window=args.z_window,
            )
            coverage = feature_coverage_report(features)
            coverage.insert(0, "method", method_name)
            coverage_tables.append(coverage)
            trend_coverage = coverage.loc[coverage["feature"].eq("trend"), "coverage"]
            if trend_coverage.empty or float(trend_coverage.max()) < 0.10:
                raise RuntimeError(
                    f"{method_name} produced insufficient trend feature coverage. "
                    "Check optional dependencies and method parameters."
                )

            tail = pd.concat({k: v.tail(5) for k, v in features.items() if k in {"trend", "cycle", "residual_z", "trend_strength", "cycle_position", "volume_residual_z"}}, axis=1)
            tail = tail.stack(level=1, future_stack=True).reset_index().rename(columns={"level_1": "asset"})
            tail.insert(0, "method", method_name)
            feature_snapshots.append(tail)

            trend_cfg = TrendFollowingConfig(allow_short=args.allow_short_trend)
            rev_cfg = OscillationReversionConfig(allow_short=args.allow_short_reversion, use_volume_filter=args.use_volume_filter)
            hybrid_cfg = HybridRegimeConfig(trend=trend_cfg, reversion=rev_cfg)
            signal_sets = [
                decomposition_trend_following_signals(close, features, config=trend_cfg, name=f"detime_{method_name}_trend_following"),
                decomposition_oscillation_reversion_signals(close, features, config=rev_cfg, name=f"detime_{method_name}_oscillation_reversion"),
                decomposition_hybrid_regime_signals(close, features, config=hybrid_cfg, name=f"detime_{method_name}_hybrid_regime"),
            ]
            for signal_set in signal_sets:
                bt = backtest_signal_set(
                    close,
                    signal_set,
                    execution_prices=execution_prices,
                    fee_bps=args.fee_bps,
                    slippage_bps=args.slippage_bps,
                    periods_per_year=args.periods_per_year,
                )
                results[signal_set.name] = bt
                if not bt.orders.empty:
                    orders = bt.orders.copy()
                    orders.insert(0, "strategy", signal_set.name)
                    all_orders.append(orders)
                if not bt.trades.empty:
                    trades = bt.trades.copy()
                    trades.insert(0, "strategy", signal_set.name)
                    all_trades.append(trades)
                if not args.no_plots:
                    plot_signal_analysis(
                        ohlcv,
                        signal_set,
                        bt,
                        asset=symbol,
                        output_path=charts_dir / f"{signal_set.name}_{symbol}.png",
                        title=f"{signal_set.name} on {symbol}",
                    )
        except Exception as exc:  # fail visibly but keep other methods runnable
            failed.append({"method": method_name, "reason": repr(exc)})

    stats = stats_table(results)
    stats.to_csv(report_dir / "strategy_lab_strategy_stats.csv", index=False)
    if feature_snapshots:
        pd.concat(feature_snapshots, ignore_index=True).to_csv(report_dir / "strategy_lab_feature_snapshot.csv", index=False)
    if coverage_tables:
        pd.concat(coverage_tables, ignore_index=True).to_csv(report_dir / "strategy_lab_feature_coverage.csv", index=False)
    if all_orders:
        pd.concat(all_orders, ignore_index=True).to_csv(report_dir / "strategy_lab_orders.csv", index=False)
    else:
        pd.DataFrame(columns=["strategy", "asset", "signal_date", "fill_date", "action", "delta_weight", "fill_price"]).to_csv(report_dir / "strategy_lab_orders.csv", index=False)
    if all_trades:
        pd.concat(all_trades, ignore_index=True).to_csv(report_dir / "strategy_lab_trades.csv", index=False)
    else:
        pd.DataFrame(columns=["strategy", "asset", "side", "entry_signal_date", "exit_signal_date", "directional_return"]).to_csv(report_dir / "strategy_lab_trades.csv", index=False)
    pd.DataFrame(failed).to_csv(report_dir / "strategy_lab_failed_methods.csv", index=False)

    manifest = {
        "ticker": symbol,
        "source": source,
        "methods": [m.upper() for m in args.methods],
        "period": args.period,
        "train_window": args.train_window,
        "step": args.step,
        "fee_bps": args.fee_bps,
        "slippage_bps": args.slippage_bps,
        "periods_per_year": args.periods_per_year,
        "allow_short_trend": bool(args.allow_short_trend),
        "allow_short_reversion": bool(args.allow_short_reversion),
        "execution_model": "signals at bar t, fill at next open when available",
        "strategies_completed": list(results.keys()),
        "failed_methods": failed,
        "outputs": {
            "stats": str(report_dir / "strategy_lab_strategy_stats.csv"),
            "orders": str(report_dir / "strategy_lab_orders.csv"),
            "trades": str(report_dir / "strategy_lab_trades.csv"),
            "charts": str(charts_dir),
        },
    }
    (report_dir / "strategy_lab_run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    print(stats.to_string(index=False))
    if failed:
        print("\nFailed methods:")
        print(pd.DataFrame(failed).to_string(index=False))
    print(f"\nWrote strategy lab outputs to {report_dir}")


if __name__ == "__main__":
    main()
