#!/usr/bin/env python
from __future__ import annotations

"""Run the extended De-Time strategy tutorials.

This script produces two executable tutorial blocks:

1. Method-specific single-asset strategy variants.  The same trading ideas are
   run under different decomposition methods and windows, so the reader can see
   that STL/SSA/STD/Wavelet create different trend, cycle, and residual signals.
2. Component-level pair trading.  The pair logic decomposes both assets, checks
   trend/cycle similarity and cointegration diagnostics, then trades residual
   gaps or fair-value spread deviations.

All outputs are in English and all strategies are backtested with a transparent
next-bar execution model.
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

from quant_trading.data import (  # noqa: E402
    FX_EXAMPLES,
    fetch_yahoo_ohlcv,
    fetch_yahoo_ohlcv_panel,
    load_bundled_real_ohlcv_panel,
    load_sample_goog_ohlcv,
    market_data_manifest,
    ohlcv_audit_report,
    ohlcv_panel_to_field,
)
from quant_trading.strategy_component_pairs import (  # noqa: E402
    ComponentPairConfig,
    collect_pair_orders_and_trades,
    run_component_pair_suite,
)
from quant_trading.strategy_lab import execution_price_panel  # noqa: E402
from quant_trading.strategy_method_variants import (  # noqa: E402
    DecompositionVariantSpec,
    collect_orders_and_trades,
    default_variant_specs,
    run_method_variant_grid,
)


BUNDLED_DEFAULT_PAIRS = [
    ("AUDUSD=X", "NZDUSD=X"),
    ("EURUSD=X", "GBPUSD=X"),
    ("CADUSD=X", "CHFUSD=X"),
]

LIVE_DEFAULT_PAIRS = [
    ("KO", "PEP"),
    ("XOM", "CVX"),
    ("MA", "V"),
    ("SPY", "QQQ"),
]


def _parse_pairs(raw: list[str] | None) -> list[tuple[str, str]]:
    if not raw:
        return []
    pairs: list[tuple[str, str]] = []
    for item in raw:
        token = str(item).replace("/", ":")
        if ":" not in token:
            raise ValueError(f"Pair must be formatted LEFT:RIGHT, got {item!r}")
        left, right = token.split(":", 1)
        pairs.append((left.strip(), right.strip()))
    return pairs


def _single_asset_panels(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, str]:
    if args.use_bundled_sample:
        ohlcv = load_sample_goog_ohlcv(trim_start=args.start, trim_end=args.end)
        symbol = "GOOG"
        source = str(ohlcv.attrs.get("source", "bundled real GOOG sample"))
    else:
        symbol = args.ticker
        ohlcv = fetch_yahoo_ohlcv(
            symbol,
            start=args.start,
            end=args.end,
            interval=args.interval,
            auto_adjust=not args.no_auto_adjust,
            min_observations=args.min_observations,
            cache_dir=args.cache_dir,
        )
        source = "Yahoo Finance via yfinance live download"
        ohlcv.attrs["symbol"] = symbol
        ohlcv.attrs["source"] = source
    close = ohlcv["Close"].rename(symbol).to_frame()
    volume = ohlcv["Volume"].rename(symbol).to_frame()
    execution_prices = execution_price_panel(ohlcv, field="Open", next_bar=True)
    execution_prices.columns = [symbol]
    return close, volume, execution_prices, symbol, source


def _pair_panels(args: argparse.Namespace, pairs: list[tuple[str, str]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    assets = sorted({x for pair in pairs for x in pair})
    if args.use_bundled_sample:
        available = [ticker for ticker in assets if ticker in FX_EXAMPLES]
        if len(available) < 2:
            pairs[:] = BUNDLED_DEFAULT_PAIRS
            assets = sorted({x for pair in pairs for x in pair})
        panel = load_bundled_real_ohlcv_panel(assets, min_observations=args.min_observations)
        source = "Learn-Algorithmic-Trading bundled real FX Yahoo Finance exports"
    else:
        panel = fetch_yahoo_ohlcv_panel(
            assets,
            start=args.start,
            end=args.end,
            interval=args.interval,
            auto_adjust=not args.no_auto_adjust,
            min_observations=args.min_observations,
            cache_dir=args.cache_dir,
            allow_partial=True,
        )
        source = "Yahoo Finance via yfinance live download"
    close = ohlcv_panel_to_field(panel, "Close")
    volume = ohlcv_panel_to_field(panel, "Volume") if "Volume" in panel else pd.DataFrame(index=close.index, columns=close.columns)
    open_ = ohlcv_panel_to_field(panel, "Open") if "Open" in panel else close.shift(-1)
    execution_prices = open_.shift(-1).reindex(index=close.index, columns=close.columns).ffill()
    return close, volume, execution_prices, source


def _specs_from_args(args: argparse.Namespace) -> list[DecompositionVariantSpec]:
    if args.variant_grid == "default":
        return default_variant_specs(include_wavelet=args.include_wavelet)
    specs: list[DecompositionVariantSpec] = []
    for method in args.methods:
        for period in args.periods:
            specs.append(
                DecompositionVariantSpec(
                    method=method.upper(),
                    period=int(period) if str(period).isdigit() else str(period),
                    train_window=args.train_window,
                    step=args.step,
                    z_window=args.z_window,
                    role="custom_grid",
                )
            )
    return specs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--use-bundled-sample", action="store_true", help="Use bundled real GOOG + FX data for offline execution.")
    parser.add_argument("--ticker", default="SPY", help="Single-asset ticker for live data runs.")
    parser.add_argument("--start", default="2014-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--no-auto-adjust", action="store_true")
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--min-observations", type=int, default=180)
    parser.add_argument("--variant-grid", choices=["default", "custom"], default="default")
    parser.add_argument("--methods", nargs="+", default=["STL", "SSA", "STD"], help="Used when --variant-grid custom.")
    parser.add_argument("--periods", nargs="+", default=["21", "42", "63"], help="Used when --variant-grid custom.")
    parser.add_argument("--train-window", type=int, default=180)
    parser.add_argument("--step", type=int, default=21)
    parser.add_argument("--z-window", type=int, default=63)
    parser.add_argument("--include-wavelet", action="store_true", help="Include WAVELET in default grid. PyWavelets must be installed.")
    parser.add_argument("--pairs", nargs="*", default=None, help="Pairs formatted LEFT:RIGHT. Defaults to FX pairs offline or equity/ETF pairs live.")
    parser.add_argument("--pair-method", default="STL")
    parser.add_argument("--pair-period", default="42")
    parser.add_argument("--pair-train-window", type=int, default=180)
    parser.add_argument("--require-cointegration", action="store_true")
    parser.add_argument("--fee-bps", type=float, default=5.0)
    parser.add_argument("--slippage-bps", type=float, default=2.0)
    parser.add_argument("--periods-per-year", type=int, default=252)
    parser.add_argument("--report-dir", default="examples/quant_trading/reports/strategy_expansion")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    close, volume, execution_prices, symbol, single_source = _single_asset_panels(args)
    ohlcv_audit_report({"Close": close, "Volume": volume}).to_csv(report_dir / "method_variants_data_audit.csv", index=False)
    market_data_manifest(tickers=[symbol], start=args.start, end=args.end, interval=args.interval, source=single_source).to_csv(report_dir / "method_variants_market_data_manifest.csv", index=False)

    specs = _specs_from_args(args)
    method_stats, method_results, spec_table, coverage, failed = run_method_variant_grid(
        close,
        volume,
        specs=specs,
        execution_prices=execution_prices,
        fee_bps=args.fee_bps,
        slippage_bps=args.slippage_bps,
        periods_per_year=args.periods_per_year,
        allow_short_trend=False,
        allow_short_reversion=True,
    )
    method_stats.to_csv(report_dir / "method_variant_strategy_stats.csv", index=False)
    spec_table.to_csv(report_dir / "method_variant_spec_grid.csv", index=False)
    coverage.to_csv(report_dir / "method_variant_feature_coverage.csv", index=False)
    ((failed if not failed.empty else pd.DataFrame(columns=["variant", "method", "period", "train_window", "reason"]))).to_csv(report_dir / "method_variant_failed_methods.csv", index=False)
    method_orders, method_trades = collect_orders_and_trades(method_results)
    method_orders.to_csv(report_dir / "method_variant_orders.csv", index=False)
    method_trades.to_csv(report_dir / "method_variant_trades.csv", index=False)

    pairs = _parse_pairs(args.pairs) or (BUNDLED_DEFAULT_PAIRS if args.use_bundled_sample else LIVE_DEFAULT_PAIRS)
    pair_close, pair_volume, pair_execution_prices, pair_source = _pair_panels(args, pairs)
    ohlcv_audit_report({"Close": pair_close, "Volume": pair_volume}).to_csv(report_dir / "component_pair_data_audit.csv", index=False)
    market_data_manifest(tickers=sorted({x for pair in pairs for x in pair}), start=args.start, end=args.end, interval=args.interval, source=pair_source).to_csv(report_dir / "component_pair_market_data_manifest.csv", index=False)

    pair_cfg = ComponentPairConfig(
        method=args.pair_method.upper(),
        period=int(args.pair_period) if str(args.pair_period).isdigit() else args.pair_period,
        train_window=args.pair_train_window,
        step=args.step,
        z_window=args.z_window,
        require_cointegration=bool(args.require_cointegration),
    )
    pair_stats, pair_results, pair_diagnostics, pair_feature_snapshot = run_component_pair_suite(
        pair_close,
        pairs,
        volumes=pair_volume,
        config=pair_cfg,
        execution_prices=pair_execution_prices,
        fee_bps=args.fee_bps,
        slippage_bps=args.slippage_bps,
        periods_per_year=args.periods_per_year,
    )
    pair_stats.to_csv(report_dir / "component_pair_strategy_stats.csv", index=False)
    pair_diagnostics.to_csv(report_dir / "component_pair_diagnostics.csv", index=False)
    pair_feature_snapshot.to_csv(report_dir / "component_pair_feature_snapshot.csv")
    pair_orders, pair_trades = collect_pair_orders_and_trades(pair_results)
    pair_orders.to_csv(report_dir / "component_pair_orders.csv", index=False)
    pair_trades.to_csv(report_dir / "component_pair_trades.csv", index=False)

    manifest = {
        "single_asset": symbol,
        "single_source": single_source,
        "method_variant_specs": [spec.to_record() for spec in specs],
        "method_variant_completed_strategies": list(method_results.keys()),
        "method_variant_failed": failed.to_dict(orient="records") if not failed.empty else [],
        "pairs": [f"{a}:{b}" for a, b in pairs],
        "pair_source": pair_source,
        "pair_config": pair_cfg.to_record(),
        "pair_completed_strategies": list(pair_results.keys()),
        "fee_bps": args.fee_bps,
        "slippage_bps": args.slippage_bps,
        "execution_model": "signals at bar t, fill at next open when available",
        "outputs": {
            "method_variant_stats": str(report_dir / "method_variant_strategy_stats.csv"),
            "component_pair_stats": str(report_dir / "component_pair_strategy_stats.csv"),
            "component_pair_diagnostics": str(report_dir / "component_pair_diagnostics.csv"),
        },
    }
    (report_dir / "strategy_expansion_run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    print("\nMethod-specific strategy variants")
    print(method_stats.head(20).to_string(index=False) if not method_stats.empty else "No method variant strategies completed.")
    if not failed.empty:
        print("\nFailed method variants")
        print(failed.to_string(index=False))
    print("\nComponent-level pair strategies")
    print(pair_stats.head(20).to_string(index=False) if not pair_stats.empty else "No pair strategies completed.")
    print(f"\nWrote strategy expansion outputs to {report_dir}")


if __name__ == "__main__":
    main()
