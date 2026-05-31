from __future__ import annotations

"""Fast offline smoke test for Columns 05-06 using bundled real FX data.

This verifies imports, real-data loading, spread decomposition, rotation
features and backtest plumbing. It is not benchmark evidence.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for candidate in (ROOT / "src", ROOT / "examples"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import pandas as pd  # noqa: E402

from quant_trading.data import load_bundled_real_ohlcv_panel  # noqa: E402
from quant_trading.features import walkforward_price_volume_features  # noqa: E402
from quant_trading.strategy_pairs import (  # noqa: E402
    make_classic_pair_weight_grid,
    make_detime_pair_weight_grid,
    walkforward_pair_spread_features,
)
from quant_trading.strategy_rotation import (  # noqa: E402
    make_classic_rotation_weight_grid,
    make_detime_rotation_weight_grid,
    volume_availability,
)
from quant_trading.validation import compare_weight_strategies  # noqa: E402


def main() -> int:
    report_dir = ROOT / "examples" / "quant_trading" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    tickers = ["AUDUSD=X", "NZDUSD=X", "EURUSD=X", "GBPUSD=X"]
    pairs = [("AUDUSD=X", "NZDUSD=X")]
    ohlcv = load_bundled_real_ohlcv_panel(tickers, min_observations=120)
    ohlcv = {field: table.tail(360).copy() for field, table in ohlcv.items()}
    prices = ohlcv["Close"]

    spread_features, spread_panel, beta_panel, pair_specs = walkforward_pair_spread_features(
        prices,
        pairs,
        hedge_window=60,
        method="STL",
        period=42,
        train_window=126,
        step=252,
        z_window=42,
    )
    pair_strategies: dict[str, pd.DataFrame] = {}
    pair_strategies.update(make_classic_pair_weight_grid(prices, pair_specs, lookback=60))
    pair_strategies.update(make_detime_pair_weight_grid(prices, pair_specs, spread_features, spread_panel=spread_panel, beta_panel=beta_panel))
    pair_table, pair_results = compare_weight_strategies(prices, pair_strategies, fee_bps=1.0, slippage_bps=2.0)

    volumes = ohlcv.get("Volume")
    volumes_for_features = volumes if volume_availability(volumes) else None
    features = walkforward_price_volume_features(
        prices,
        volumes_for_features,
        method="STL",
        period=42,
        train_window=126,
        step=252,
        z_window=42,
    )
    rotation_strategies: dict[str, pd.DataFrame] = {}
    rotation_strategies.update(make_classic_rotation_weight_grid(prices, top_n=2, rebalance="W-FRI"))
    rotation_strategies.update(make_detime_rotation_weight_grid(prices, features, top_n=2, rebalance="W-FRI"))
    rotation_table, rotation_results = compare_weight_strategies(prices, rotation_strategies, fee_bps=1.0, slippage_bps=2.0)

    assert isinstance(pair_table, pd.DataFrame) and "sharpe" in pair_table.columns and len(pair_table) >= 6
    assert isinstance(rotation_table, pd.DataFrame) and "sharpe" in rotation_table.columns and len(rotation_table) >= 6
    assert pair_results and rotation_results
    pair_table.to_csv(report_dir / "column_05_smoke_strategy_stats.csv")
    rotation_table.to_csv(report_dir / "column_06_smoke_strategy_stats.csv")
    print("quant columns 05-06 smoke checks passed")
    print(pair_table[["total_return", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    print(rotation_table[["total_return", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
