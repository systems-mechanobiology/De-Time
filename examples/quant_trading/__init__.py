"""Quant trading tutorial utilities for the De-Time documentation column.

The utilities are intentionally example-scoped. They are not part of the core
`detime` public package surface and should not add production trading claims.
"""

from .data import DEFAULT_UNIVERSES, MarketDataError, fetch_yahoo_prices, fetch_yahoo_ohlcv, data_audit_report
from .features import decompose_one_series, walkforward_decompose, build_feature_table
from .signals import (
    trend_pullback_signals,
    residual_mean_reversion_signals,
    turtle_donchian_signals,
    pair_trading_weights,
    cross_sectional_rotation_weights,
    residual_stress_filter,
)
from .backtest import backtest_weights, backtest_long_short_signals, summarize_returns

__all__ = [
    "DEFAULT_UNIVERSES",
    "MarketDataError",
    "fetch_yahoo_prices",
    "fetch_yahoo_ohlcv",
    "data_audit_report",
    "decompose_one_series",
    "walkforward_decompose",
    "build_feature_table",
    "trend_pullback_signals",
    "residual_mean_reversion_signals",
    "turtle_donchian_signals",
    "pair_trading_weights",
    "cross_sectional_rotation_weights",
    "residual_stress_filter",
    "backtest_weights",
    "backtest_long_short_signals",
    "summarize_returns",
]
