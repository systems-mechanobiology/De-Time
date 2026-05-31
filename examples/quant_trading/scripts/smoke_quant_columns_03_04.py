from __future__ import annotations

"""Fast offline smoke test for Columns 03-04 using bundled real GOOG data."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "src", ROOT / "examples"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pandas as pd  # noqa: E402

from quant_trading.data import load_sample_goog_ohlcv  # noqa: E402
from quant_trading.decomposition_features import walkforward_price_volume_features  # noqa: E402
from quant_trading.strategy_breakout import make_classic_breakout_weight_grid, make_detime_breakout_weight_grid  # noqa: E402
from quant_trading.strategy_mean_reversion import make_classic_mean_reversion_weight_grid, make_detime_mean_reversion_weight_grid  # noqa: E402
from quant_trading.validation import compare_weight_strategies  # noqa: E402


def main() -> int:
    sample = load_sample_goog_ohlcv(trim_start="2016-01-01")
    ticker = str(sample.attrs.get("symbol", "GOOG"))
    prices = sample[["Close"]].rename(columns={"Close": ticker})
    volumes = sample[["Volume"]].rename(columns={"Volume": ticker})
    ohlcv = {field: sample[[field]].rename(columns={field: ticker}) for field in ["Open", "High", "Low", "Close", "Volume"]}

    features = walkforward_price_volume_features(
        prices,
        volumes,
        method="STL",
        period=42,
        train_window=126,
        step=126,
        z_window=42,
    )

    strategies: dict[str, pd.DataFrame] = {}
    strategies.update(make_classic_mean_reversion_weight_grid(prices, allow_short=False))
    strategies.update(make_detime_mean_reversion_weight_grid(prices, features, allow_short=False))
    strategies.update(make_classic_breakout_weight_grid(ohlcv, allow_short=False))
    strategies.update(make_detime_breakout_weight_grid(ohlcv, features, allow_short=False))

    table, results = compare_weight_strategies(prices, strategies, fee_bps=1.0, slippage_bps=2.0)
    assert isinstance(table, pd.DataFrame)
    assert "sharpe" in table.columns
    assert len(table) >= 10
    assert results
    report_dir = ROOT / "examples/quant_trading/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(report_dir / "column_03_04_smoke_strategy_stats.csv")
    print("quant columns 03-04 smoke checks passed")
    print(table[["total_return", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
