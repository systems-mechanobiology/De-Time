from __future__ import annotations

"""Column 03: classical vs decomposition-aware mean-reversion recipes.

The functions in this module are deliberately small and auditable.  They keep
classic RSI/Bollinger/APO baselines visible, then rewrite the same trading idea
around DeTime residual, cycle, trend and volume components.
"""

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_weights, signals_to_weights
from .classic_indicators import (
    apo_reversion_signals,
    bollinger_reversion_signals,
    price_zscore_reversion_signals,
    rsi,
    rsi_reversion_signals,
)
from .strategy_baselines import stats_table
from .strategy_detime import _feature, decomposition_risk_mask, volume_confirmation_mask


def _stateful_weights(
    long_entries: pd.DataFrame,
    long_exits: pd.DataFrame,
    short_entries: pd.DataFrame | None = None,
    short_exits: pd.DataFrame | None = None,
    *,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    weights = signals_to_weights(long_entries, long_exits, short_entries=short_entries, short_exits=short_exits, equal_weight=True)
    return weights * float(max_gross)


def classic_rsi_reversion_weights(
    prices: pd.DataFrame,
    *,
    window: int = 14,
    lower: float = 30.0,
    upper: float = 70.0,
    exit_level: float = 50.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = rsi_reversion_signals(prices, window=window, lower=lower, upper=upper, exit_level=exit_level, allow_short=allow_short)
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def classic_bollinger_reversion_weights(
    prices: pd.DataFrame,
    *,
    window: int = 20,
    entry_z: float = 2.0,
    exit_z: float = 0.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = bollinger_reversion_signals(prices, window=window, entry_z=entry_z, exit_z=exit_z, allow_short=allow_short)
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def classic_price_zscore_reversion_weights(
    prices: pd.DataFrame,
    *,
    window: int = 63,
    entry_z: float = 1.5,
    exit_z: float = 0.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = price_zscore_reversion_signals(prices, window=window, entry_z=entry_z, exit_z=exit_z, allow_short=allow_short)
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def classic_apo_reversion_weights(
    prices: pd.DataFrame,
    *,
    fast: int = 10,
    slow: int = 40,
    z_window: int = 63,
    entry_z: float = 1.5,
    exit_z: float = 0.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = apo_reversion_signals(prices, fast=fast, slow=slow, z_window=z_window, entry_z=entry_z, exit_z=exit_z, allow_short=allow_short)
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def residual_reversion_entries_exits(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    entry_z: float = 1.5,
    exit_z: float = 0.15,
    min_trend_slope_for_longs: float = -np.inf,
    max_trend_slope_for_shorts: float = np.inf,
    require_cycle_turn: bool = True,
    min_cycle_slope_for_longs: float = -0.02,
    max_cycle_slope_for_shorts: float = 0.02,
    use_volume_confirmation: bool = True,
    allow_short: bool = True,
    max_abs_residual_z: float = 3.5,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    """Residual-z reversion signals with trend, cycle and volume context.

    The raw-price z-score baseline asks whether price is far from a rolling
    mean.  This version asks whether price is far from its current decomposed
    trend+cycle structure.
    """

    rz = _feature(features, "residual_z", prices, fill=0.0)
    trend_slope = _feature(features, "trend_slope", prices, fill=0.0)
    cycle_slope = _feature(features, "cycle_slope", prices, fill=0.0)
    stability = decomposition_risk_mask(prices, features, max_abs_residual_z=max_abs_residual_z)

    long_context = (trend_slope >= float(min_trend_slope_for_longs)) & stability
    short_context = (trend_slope <= float(max_trend_slope_for_shorts)) & stability
    if require_cycle_turn:
        long_context &= cycle_slope >= float(min_cycle_slope_for_longs)
        short_context &= cycle_slope <= float(max_cycle_slope_for_shorts)
    if use_volume_confirmation:
        vol_ok = volume_confirmation_mask(prices, features, min_volume_trend_slope=-0.005, min_volume_residual_z=-0.85)
        long_context &= vol_ok
        short_context &= vol_ok

    long_entries = (rz < -float(entry_z)) & long_context
    long_exits = (rz > -float(exit_z)) | (~long_context)
    if not allow_short:
        return long_entries.fillna(False), long_exits.fillna(False), None, None
    short_entries = (rz > float(entry_z)) & short_context
    short_exits = (rz < float(exit_z)) | (~short_context)
    return long_entries.fillna(False), long_exits.fillna(False), short_entries.fillna(False), short_exits.fillna(False)


def detime_residual_reversion_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    entry_z: float = 1.5,
    exit_z: float = 0.15,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = residual_reversion_entries_exits(prices, features, entry_z=entry_z, exit_z=exit_z, allow_short=allow_short)
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def detime_trend_pullback_reversion_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    entry_z: float = 1.0,
    exit_z: float = 0.10,
    min_trend_slope: float = -0.001,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, _, _ = residual_reversion_entries_exits(
        prices,
        features,
        entry_z=entry_z,
        exit_z=exit_z,
        min_trend_slope_for_longs=min_trend_slope,
        min_cycle_slope_for_longs=-0.02,
        require_cycle_turn=True,
        use_volume_confirmation=True,
        allow_short=False,
        max_abs_residual_z=3.0,
    )
    return _stateful_weights(le, lx, None, None, max_gross=max_gross)


def detime_residual_bands_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    entry_z: float = 2.0,
    exit_z: float = 0.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Cycle-aware residual band strategy, analogous to Bollinger reversion."""

    le, lx, se, sx = residual_reversion_entries_exits(
        prices,
        features,
        entry_z=entry_z,
        exit_z=exit_z,
        require_cycle_turn=True,
        min_cycle_slope_for_longs=-0.02,
        max_cycle_slope_for_shorts=0.02,
        use_volume_confirmation=True,
        allow_short=allow_short,
        max_abs_residual_z=4.0,
    )
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def detime_residual_rsi_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    window: int = 14,
    lower: float = 35.0,
    upper: float = 65.0,
    exit_level: float = 50.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """RSI applied to residual pressure rather than raw price."""

    residual = _feature(features, "residual", prices, fill=0.0)
    residual_rsi = rsi(residual, window=window)
    rz = _feature(features, "residual_z", prices, fill=0.0)
    cycle_slope = _feature(features, "cycle_slope", prices, fill=0.0)
    stable = decomposition_risk_mask(prices, features, max_abs_residual_z=3.5)
    vol_ok = volume_confirmation_mask(prices, features, min_volume_trend_slope=-0.005, min_volume_residual_z=-0.85)

    long_entries = (residual_rsi < float(lower)) & (rz < -0.5) & (cycle_slope >= -0.02) & stable & vol_ok
    long_exits = (residual_rsi > float(exit_level)) | (rz > 0.0) | (~stable)
    if not allow_short:
        return _stateful_weights(long_entries.fillna(False), long_exits.fillna(False), None, None, max_gross=max_gross)
    short_entries = (residual_rsi > float(upper)) & (rz > 0.5) & (cycle_slope <= 0.02) & stable & vol_ok
    short_exits = (residual_rsi < float(exit_level)) | (rz < 0.0) | (~stable)
    return _stateful_weights(long_entries.fillna(False), long_exits.fillna(False), short_entries.fillna(False), short_exits.fillna(False), max_gross=max_gross)


def make_classic_mean_reversion_weight_grid(prices: pd.DataFrame, *, allow_short: bool = True) -> dict[str, pd.DataFrame]:
    return {
        "classic_rsi_14_reversion": classic_rsi_reversion_weights(prices, window=14, allow_short=allow_short),
        "classic_bollinger_20_2z": classic_bollinger_reversion_weights(prices, window=20, entry_z=2.0, allow_short=allow_short),
        "classic_price_zscore_63_1p5z": classic_price_zscore_reversion_weights(prices, window=63, entry_z=1.5, allow_short=allow_short),
        "classic_apo_10_40_reversion": classic_apo_reversion_weights(prices, fast=10, slow=40, allow_short=allow_short),
    }


def make_detime_mean_reversion_weight_grid(prices: pd.DataFrame, features: dict[str, pd.DataFrame], *, allow_short: bool = True) -> dict[str, pd.DataFrame]:
    return {
        "detime_residual_z_1p0_cycle_volume": detime_residual_reversion_weights(prices, features, entry_z=1.0, allow_short=allow_short),
        "detime_residual_band_1p25z": detime_residual_bands_weights(prices, features, entry_z=1.25, allow_short=allow_short),
        "detime_residual_rsi_14": detime_residual_rsi_weights(prices, features, window=14, allow_short=allow_short),
        "detime_trend_pullback_residual": detime_trend_pullback_reversion_weights(prices, features, entry_z=1.0),
    }


def run_classical_mean_reversion_baselines(
    prices: pd.DataFrame,
    *,
    allow_short: bool = True,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    return {
        name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps)
        for name, weights in make_classic_mean_reversion_weight_grid(prices, allow_short=allow_short).items()
    }


def run_detime_mean_reversion_baselines(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    allow_short: bool = True,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    return {
        name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps)
        for name, weights in make_detime_mean_reversion_weight_grid(prices, features, allow_short=allow_short).items()
    }


def compare_mean_reversion_suites(classical: dict[str, BacktestResult], detime: dict[str, BacktestResult]) -> pd.DataFrame:
    left = stats_table(classical).assign(strategy_group="classical_mean_reversion")
    right = stats_table(detime).assign(strategy_group="detime_residual_mean_reversion")
    table = pd.concat([left, right], axis=0)
    order = ["strategy_group", "cagr", "sharpe", "max_drawdown", "calmar", "average_turnover", "average_gross_exposure", "total_return", "volatility", "hit_rate"]
    return table[[c for c in order if c in table.columns]].sort_values("sharpe", ascending=False)


mean_reversion_baseline_suite = make_classic_mean_reversion_weight_grid
detime_mean_reversion_suite = make_detime_mean_reversion_weight_grid
