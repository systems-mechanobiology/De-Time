"""Quant trading tutorial utilities for the DeTime documentation column.

The utilities are example-scoped. They are not part of the core ``detime``
public package surface and should not be interpreted as production trading
advice.
"""

from .data import (
    DEFAULT_UNIVERSES,
    MarketDataError,
    data_audit_report,
    fetch_yahoo_ohlcv,
    fetch_yahoo_ohlcv_panel,
    fetch_yahoo_prices,
    load_bundled_real_ohlcv,
    load_bundled_real_ohlcv_panel,
    load_bundled_real_price_panel,
    load_or_download_ohlcv_for_tutorial,
    load_sample_goog_ohlcv,
    market_data_manifest,
    ohlcv_audit_report,
    ohlcv_panel_to_field,
    prices_to_returns,
    write_dataset_passport,
)
from .features import (
    build_feature_table,
    decompose_ohlcv,
    decompose_one_series,
    estimate_dominant_period,
    feature_coverage_report,
    walkforward_decompose,
    walkforward_decompose_ohlcv,
    walkforward_price_volume_features,
)
from .backtest import backtest_long_short_signals, backtest_weights, summarize_returns

from .strategy_pairs import (
    BUNDLED_REAL_PAIRS,
    DEFAULT_LIVE_PAIRS,
    build_pair_spread_bundle,
    classic_pair_zscore_weights,
    detime_spread_residual_weights,
    make_classic_pair_weight_grid,
    make_detime_pair_weight_grid,
    pair_diagnostic_table,
    run_pair_suite,
)
from .strategy_rotation import (
    classic_momentum_rotation_weights,
    detime_cross_sectional_score,
    detime_rotation_score,
    detime_rotation_weights,
    make_classic_rotation_weight_grid,
    make_detime_rotation_weight_grid,
    rotation_factor_snapshot,
    run_rotation_suites,
)

__all__ = [name for name in globals() if not name.startswith("_")]
