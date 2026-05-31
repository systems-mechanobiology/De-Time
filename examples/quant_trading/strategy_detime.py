from __future__ import annotations

"""Decomposition-aware strategy recipes for the quant tutorials.

Columns 01-02 use trend filters and decomposed MA/MACD. Columns 03-04
add residual mean reversion and breakout systems with volume confirmation.
"""

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_weights, signals_to_weights
from .classic_indicators import bollinger_bands, donchian_channels, dual_ma_signals, macd, rsi, sma
from .strategy_baselines import stats_table


def _align(frame: pd.DataFrame | None, prices: pd.DataFrame, *, fill: float | None = None) -> pd.DataFrame:
    if frame is None:
        if fill is None:
            raise KeyError("required feature frame is missing")
        return pd.DataFrame(float(fill), index=prices.index, columns=prices.columns)
    return frame.reindex(index=prices.index, columns=prices.columns).ffill()


def _feature(features: dict[str, pd.DataFrame], name: str, prices: pd.DataFrame, *, fill: float | None = None) -> pd.DataFrame:
    return _align(features.get(name), prices, fill=fill)


def _equal_weight_from_state(state: pd.DataFrame, *, max_gross: float = 1.0) -> pd.DataFrame:
    pos = state.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    gross = pos.abs().sum(axis=1).replace(0.0, np.nan)
    return pos.div(gross, axis=0).fillna(0.0) * float(max_gross)


def volume_confirmation_mask(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    min_volume_trend_slope: float = 0.0,
    min_volume_residual_z: float = -0.5,
) -> pd.DataFrame:
    if "volume_trend_slope" not in features and "volume_residual_z" not in features:
        return pd.DataFrame(True, index=prices.index, columns=prices.columns)
    vt = _feature(features, "volume_trend_slope", prices, fill=0.0)
    vz = _feature(features, "volume_residual_z", prices, fill=0.0)
    return ((vt >= float(min_volume_trend_slope)) | (vz >= float(min_volume_residual_z))).fillna(False)


def decomposition_risk_mask(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    max_abs_residual_z: float = 2.75,
    min_component_stability: float = 0.0,
) -> pd.DataFrame:
    rz = _feature(features, "residual_abs_z", prices, fill=0.0)
    stability = _feature(features, "component_stability", prices, fill=1.0)
    return ((rz < float(max_abs_residual_z)) & (stability > float(min_component_stability))).fillna(False)


def detime_trend_state(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    min_trend_slope: float = 0.0,
    min_trend_strength: float = -np.inf,
    require_cycle_turn_up: bool = False,
    use_volume_confirmation: bool = True,
    max_abs_residual_z: float = 2.75,
) -> pd.DataFrame:
    trend_up = _feature(features, "trend_slope", prices) > float(min_trend_slope)
    strength = _feature(features, "trend_strength", prices, fill=0.0) > float(min_trend_strength)
    state = trend_up & strength & decomposition_risk_mask(prices, features, max_abs_residual_z=max_abs_residual_z)
    if require_cycle_turn_up:
        state = state & (_feature(features, "cycle_slope", prices, fill=0.0) >= 0.0)
    if use_volume_confirmation:
        state = state & volume_confirmation_mask(prices, features)
    return state.fillna(False)


def detime_trend_weights(prices: pd.DataFrame, features: dict[str, pd.DataFrame], **kwargs) -> pd.DataFrame:
    return _equal_weight_from_state(detime_trend_state(prices, features, **kwargs))


def decomposed_dual_ma_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    fast: int = 20,
    slow: int = 100,
    require_cycle_turn_up: bool = False,
    use_volume_confirmation: bool = True,
    max_abs_residual_z: float = 2.75,
) -> pd.DataFrame:
    trend = _feature(features, "trend", prices)
    trend_cross = sma(trend, fast) > sma(trend, slow)
    trend_slope_ok = _feature(features, "trend_slope", prices, fill=0.0) >= 0.0
    state = trend_cross & trend_slope_ok & decomposition_risk_mask(prices, features, max_abs_residual_z=max_abs_residual_z)
    if require_cycle_turn_up:
        state = state & (_feature(features, "cycle_slope", prices, fill=0.0) >= 0.0)
    if use_volume_confirmation:
        state = state & volume_confirmation_mask(prices, features)
    return _equal_weight_from_state(state.fillna(False))


def decomposed_macd_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    use_volume_confirmation: bool = True,
    max_abs_residual_z: float = 2.75,
    max_cycle_z: float = 1.5,
) -> pd.DataFrame:
    trend = _feature(features, "trend", prices)
    parts = macd(trend, fast=fast, slow=slow, signal=signal)
    state = (parts["macd"] > parts["signal"]) & (parts["histogram"] > 0)
    state = state & (_feature(features, "cycle_z", prices, fill=0.0) < float(max_cycle_z))
    state = state & decomposition_risk_mask(prices, features, max_abs_residual_z=max_abs_residual_z)
    if use_volume_confirmation:
        state = state & volume_confirmation_mask(prices, features)
    return _equal_weight_from_state(state.fillna(False))


def trend_pullback_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    entry_residual_z: float = -1.0,
    exit_residual_z: float = 0.25,
    min_trend_slope: float = 0.0,
    use_volume_confirmation: bool = True,
) -> pd.DataFrame:
    trend_ok = _feature(features, "trend_slope", prices) > float(min_trend_slope)
    rz = _feature(features, "residual_z", prices)
    entries = trend_ok & (rz < float(entry_residual_z))
    exits = (~trend_ok) | (rz > float(exit_residual_z))
    if use_volume_confirmation:
        entries = entries & volume_confirmation_mask(prices, features)
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=True)


def make_detime_trend_weight_grid(prices: pd.DataFrame, features: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {
        "detime_trend_slope": detime_trend_weights(prices, features, min_trend_slope=0.0),
        "detime_trend_cycle_volume": detime_trend_weights(prices, features, min_trend_slope=0.0, require_cycle_turn_up=True, use_volume_confirmation=True),
        "detime_sma_20_100_trend_volume": decomposed_dual_ma_weights(prices, features, fast=20, slow=100),
        "detime_macd_12_26_9": decomposed_macd_weights(prices, features, fast=12, slow=26, signal=9),
        "detime_trend_pullback": trend_pullback_weights(prices, features),
    }


detime_strategy_weight_suite = make_detime_trend_weight_grid


def run_detime_trend_baselines(prices: pd.DataFrame, features: dict[str, pd.DataFrame], *, fee_bps: float = 5.0, slippage_bps: float = 2.0) -> dict[str, BacktestResult]:
    return {name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, weights in make_detime_trend_weight_grid(prices, features).items()}


def compare_classical_and_detime(classical: dict[str, BacktestResult], detime: dict[str, BacktestResult]) -> pd.DataFrame:
    left = stats_table(classical).assign(strategy_group="classical")
    right = stats_table(detime).assign(strategy_group="detime")
    table = pd.concat([left, right], axis=0)
    order = ["strategy_group", "cagr", "sharpe", "max_drawdown", "calmar", "average_turnover", "total_return", "volatility", "hit_rate"]
    return table[[c for c in order if c in table.columns]].sort_values("sharpe", ascending=False)


detime_trend_following_weights = detime_trend_weights
detime_trend_macd_weights = decomposed_macd_weights
detime_multi_ma_weights = decomposed_dual_ma_weights
detime_pullback_weights = trend_pullback_weights


# ---------------------------------------------------------------------------
# Column 03: residual mean reversion, RSI and Bollinger rewrites
# ---------------------------------------------------------------------------


def _cycle_timing_mask(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    side: str,
    require_cycle: bool = True,
) -> pd.DataFrame:
    if not require_cycle:
        return pd.DataFrame(True, index=prices.index, columns=prices.columns)
    slope = _feature(features, "cycle_slope", prices, fill=0.0)
    if side == "long":
        return (slope >= 0.0).fillna(False)
    if side == "short":
        return (slope <= 0.0).fillna(False)
    raise ValueError("side must be 'long' or 'short'")


def residual_mean_reversion_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    entry_z: float = 1.5,
    exit_z: float = 0.0,
    min_trend_slope: float = 0.0,
    require_cycle_turn: bool = True,
    use_volume_confirmation: bool = True,
    allow_short: bool = False,
    panic_abs_z: float = 3.25,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Mean reversion on residual deviation rather than raw price deviation.

    Long trades buy a negative residual only when the broader trend is not
    broken and the cycle is no longer pointing down. Optional short trades are
    symmetric, but the notebooks keep the default long-only version because
    borrowing and short-sale constraints are data-vendor dependent.
    """

    rz = _feature(features, "residual_z", prices, fill=0.0)
    trend = _feature(features, "trend_slope", prices, fill=0.0)
    stable = decomposition_risk_mask(prices, features, max_abs_residual_z=panic_abs_z)
    long_entries = (rz < -abs(float(entry_z))) & (trend >= float(min_trend_slope)) & stable
    long_entries = long_entries & _cycle_timing_mask(prices, features, side="long", require_cycle=require_cycle_turn)
    long_exits = (rz > float(exit_z)) | (trend < float(min_trend_slope)) | (~stable)
    if use_volume_confirmation:
        long_entries = long_entries & volume_confirmation_mask(prices, features, min_volume_residual_z=-1.0)
    if allow_short:
        short_entries = (rz > abs(float(entry_z))) & (trend <= -float(min_trend_slope)) & stable
        short_entries = short_entries & _cycle_timing_mask(prices, features, side="short", require_cycle=require_cycle_turn)
        short_exits = (rz < -float(exit_z)) | (trend > -float(min_trend_slope)) | (~stable)
    else:
        short_entries = short_exits = None
    return signals_to_weights(
        long_entries.fillna(False),
        long_exits.fillna(False),
        short_entries=None if short_entries is None else short_entries.fillna(False),
        short_exits=None if short_exits is None else short_exits.fillna(False),
        equal_weight=True,
    ) * float(max_gross)


def residual_rsi_mean_reversion_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    window: int = 14,
    lower: float = 35.0,
    exit_level: float = 52.0,
    min_trend_slope: float = 0.0,
    use_volume_confirmation: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """RSI applied to residual state, not to raw price."""

    residual = _feature(features, "residual", prices, fill=0.0)
    residual_rsi = rsi(residual, window=window)
    rz = _feature(features, "residual_z", prices, fill=0.0)
    trend_ok = _feature(features, "trend_slope", prices, fill=0.0) >= float(min_trend_slope)
    entries = (residual_rsi < float(lower)) & (rz < -0.5) & trend_ok & _cycle_timing_mask(prices, features, side="long")
    exits = (residual_rsi > float(exit_level)) | (rz > 0.0) | (~trend_ok)
    if use_volume_confirmation:
        entries = entries & volume_confirmation_mask(prices, features, min_volume_residual_z=-1.0)
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=True) * float(max_gross)


def residual_bollinger_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    window: int = 20,
    num_std: float = 2.0,
    min_trend_slope: float = 0.0,
    use_volume_confirmation: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Bollinger logic on the residual channel after trend and cycle removal."""

    residual = _feature(features, "residual", prices, fill=0.0)
    bands = bollinger_bands(residual, window=window, num_std=num_std)
    trend_ok = _feature(features, "trend_slope", prices, fill=0.0) >= float(min_trend_slope)
    entries = (residual < bands.lower) & trend_ok & _cycle_timing_mask(prices, features, side="long")
    exits = (residual >= bands.middle) | (~trend_ok)
    if use_volume_confirmation:
        entries = entries & volume_confirmation_mask(prices, features, min_volume_residual_z=-1.0)
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=True) * float(max_gross)


def cycle_adjusted_residual_band_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    entry_z: float = 1.25,
    max_cycle_position: float = 1.0,
    min_trend_slope: float = 0.0,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Residual band strategy that avoids buying when the cycle is already high."""

    rz = _feature(features, "residual_z", prices, fill=0.0)
    cycle_pos = _feature(features, "cycle_position", prices, fill=0.0)
    trend_ok = _feature(features, "trend_slope", prices, fill=0.0) >= float(min_trend_slope)
    entries = (rz < -abs(float(entry_z))) & (cycle_pos < float(max_cycle_position)) & trend_ok
    entries = entries & _cycle_timing_mask(prices, features, side="long")
    exits = (rz > 0.0) | (cycle_pos > float(max_cycle_position)) | (~trend_ok)
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=True) * float(max_gross)


def make_detime_mean_reversion_weight_grid(prices: pd.DataFrame, features: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {
        "detime_residual_z_cycle": residual_mean_reversion_weights(prices, features, entry_z=1.5, require_cycle_turn=True),
        "detime_residual_rsi": residual_rsi_mean_reversion_weights(prices, features, window=14),
        "detime_residual_bollinger": residual_bollinger_weights(prices, features, window=20, num_std=2.0),
        "detime_cycle_adjusted_band": cycle_adjusted_residual_band_weights(prices, features, entry_z=1.25),
    }


def run_detime_mean_reversion_baselines(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    return {name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, weights in make_detime_mean_reversion_weight_grid(prices, features).items()}


# ---------------------------------------------------------------------------
# Column 04: Donchian / Turtle breakout with decomposition and volume gates
# ---------------------------------------------------------------------------


def detime_donchian_breakout_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
    entry_window: int = 55,
    exit_window: int = 20,
    min_trend_slope: float = 0.0,
    min_trend_strength: float = -np.inf,
    min_cycle_slope: float = -np.inf,
    min_volume_trend_slope: float = 0.0,
    volume_shock_z: float = 0.75,
    max_overextension_z: float = 2.25,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Donchian breakout confirmed by De-Time trend, cycle and volume state."""

    h = high.reindex_like(prices).ffill().bfill() if high is not None else prices
    l = low.reindex_like(prices).ffill().bfill() if low is not None else prices
    entry_channel = donchian_channels(h, l, window=entry_window, shift=1)
    exit_channel = donchian_channels(h, l, window=exit_window, shift=1)
    price_breakout = prices > entry_channel.upper

    trend_ok = _feature(features, "trend_slope", prices, fill=0.0) > float(min_trend_slope)
    strength_ok = _feature(features, "trend_strength", prices, fill=0.0) > float(min_trend_strength)
    cycle_ok = _feature(features, "cycle_slope", prices, fill=0.0) >= float(min_cycle_slope)
    residual_ok = _feature(features, "residual_abs_z", prices, fill=0.0) < float(max_overextension_z)
    volume_ok = volume_confirmation_mask(
        prices,
        features,
        min_volume_trend_slope=float(min_volume_trend_slope),
        min_volume_residual_z=float(volume_shock_z),
    )
    entries = price_breakout & trend_ok & strength_ok & cycle_ok & residual_ok & volume_ok
    exits = (
        (prices < exit_channel.lower)
        | (_feature(features, "trend_slope", prices, fill=0.0) < 0.0)
        | ((_feature(features, "cycle_slope", prices, fill=0.0) < 0.0) & (_feature(features, "residual_z", prices, fill=0.0) > 1.0))
    )
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=True) * float(max_gross)


def detime_turtle_breakout_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Turtle 55/20 breakout rewritten as trend + volume-confirmed breakout."""

    return detime_donchian_breakout_weights(
        prices,
        features,
        high=high,
        low=low,
        entry_window=55,
        exit_window=20,
        min_trend_slope=0.0,
        min_trend_strength=-0.25,
        min_cycle_slope=-0.01,
        volume_shock_z=0.5,
        max_overextension_z=2.5,
        max_gross=max_gross,
    )


def make_detime_breakout_weight_grid(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    return {
        "detime_donchian_20_10_volume": detime_donchian_breakout_weights(
            prices,
            features,
            high=high,
            low=low,
            entry_window=20,
            exit_window=10,
            min_trend_strength=-0.5,
            volume_shock_z=0.5,
            max_overextension_z=2.5,
        ),
        "detime_donchian_55_20_volume": detime_donchian_breakout_weights(
            prices,
            features,
            high=high,
            low=low,
            entry_window=55,
            exit_window=20,
            min_trend_strength=-0.25,
            volume_shock_z=0.5,
            max_overextension_z=2.5,
        ),
        "detime_turtle_55_20": detime_turtle_breakout_weights(prices, features, high=high, low=low),
    }


def run_detime_breakout_baselines(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    weights = make_detime_breakout_weight_grid(prices, features, high=high, low=low)
    return {name: backtest_weights(prices, w, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, w in weights.items()}


# Public aliases used in notebooks.
detime_residual_mean_reversion_weights = residual_mean_reversion_weights
detime_residual_rsi_weights = residual_rsi_mean_reversion_weights
detime_residual_bollinger_weights = residual_bollinger_weights
detime_breakout_weights = detime_donchian_breakout_weights
