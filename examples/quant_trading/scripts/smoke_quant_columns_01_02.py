from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
EXAMPLES = ROOT / "examples"
for path in (SRC, EXAMPLES):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pandas as pd  # noqa: E402

from quant_trading.data import load_sample_goog_ohlcv  # noqa: E402
from quant_trading.decomposition_features import feature_coverage_report, walkforward_price_volume_features  # noqa: E402
from quant_trading.strategy_baselines import make_classic_baseline_weight_grid  # noqa: E402
from quant_trading.strategy_detime import make_detime_trend_weight_grid  # noqa: E402
from quant_trading.validation import compare_weight_strategies  # noqa: E402


def main() -> int:
    ohlcv = load_sample_goog_ohlcv(trim_start="2014-01-01")
    prices = ohlcv[["Close"]].rename(columns={"Close": "GOOG"})
    volumes = ohlcv[["Volume"]].rename(columns={"Volume": "GOOG"})
    features = walkforward_price_volume_features(
        prices,
        volumes,
        method="STL",
        period=63,
        train_window=252,
        step=63,
        z_window=63,
    )
    coverage = feature_coverage_report(features)
    assert not coverage.empty
    assert coverage["coverage"].max() > 0
    strategies = {}
    strategies.update(make_classic_baseline_weight_grid(prices))
    strategies.update(make_detime_trend_weight_grid(prices, features))
    table, results = compare_weight_strategies(prices, strategies, fee_bps=1.0, slippage_bps=2.0)
    assert isinstance(table, pd.DataFrame)
    assert "sharpe" in table.columns
    assert results
    print("quant columns 01-02 smoke checks passed")
    print(table[["total_return", "sharpe", "max_drawdown", "average_turnover"]].round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
