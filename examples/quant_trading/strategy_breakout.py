from __future__ import annotations

"""Column 04: Donchian/Turtle breakout recipes with DeTime confirmation."""

from typing import Mapping

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_weights, signals_to_weights
from .classic_indicators import atr, donchian_breakout_signals, donchian_channels
from .data import ohlcv_panel_to_field
from .strategy_baselines import stats_table
from .strategy_detime import _feature, decomposition_risk_mask, volume_confirmation_mask

OHLCVLike = Mapping[str, pd.DataFrame] | pd.DataFrame


def _field(ohlcv: OHLCVLike, name: str) -> pd.DataFrame:
    if isinstance(ohlcv, Mapping):
        return ohlcv_panel_to_field(ohlcv, name)
    if name not in ohlcv.columns:
        raise KeyError(f"OHLCV table is missing {name!r}")
    asset = str(ohlcv.attrs.get("symbol", "asset"))
    return ohlcv[[name]].rename(columns={name: asset}).sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()


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


def classic_donchian_breakout_weights(
    ohlcv: OHLCVLike,
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    close, high, low = _field(ohlcv, "Close"), _field(ohlcv, "High"), _field(ohlcv, "Low")
    le, lx, se, sx = donchian_breakout_signals(close, high, low, entry_window=entry_window, exit_window=exit_window, allow_short=allow_short)
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def classic_turtle_breakout_weights(
    ohlcv: OHLCVLike,
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    atr_window: int = 20,
    max_atr_pct: float = 0.20,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Classic Donchian/Turtle-style breakout with a simple ATR sanity cap."""

    close, high, low = _field(ohlcv, "Close"), _field(ohlcv, "High"), _field(ohlcv, "Low")
    le, lx, se, sx = donchian_breakout_signals(close, high, low, entry_window=entry_window, exit_window=exit_window, allow_short=allow_short)
    atr_pct = atr(high, low, close, window=atr_window) / (close.abs() + 1e-12)
    vol_ok = (atr_pct < float(max_atr_pct)).fillna(False)
    le = le & vol_ok
    if se is not None:
        se = se & vol_ok
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def classic_volatility_breakout_weights(
    ohlcv: OHLCVLike,
    *,
    lookback: int = 20,
    atr_window: int = 20,
    atr_multiple: float = 1.0,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Close above prior close plus ATR threshold; a non-channel breakout baseline."""

    close, high, low = _field(ohlcv, "Close"), _field(ohlcv, "High"), _field(ohlcv, "Low")
    a = atr(high, low, close, window=atr_window)
    ref = close.shift(int(lookback))
    long_entries = (close > ref + float(atr_multiple) * a).fillna(False)
    long_exits = (close < ref).fillna(False)
    if not allow_short:
        return _stateful_weights(long_entries, long_exits, None, None, max_gross=max_gross)
    short_entries = (close < ref - float(atr_multiple) * a).fillna(False)
    short_exits = (close > ref).fillna(False)
    return _stateful_weights(long_entries, long_exits, short_entries, short_exits, max_gross=max_gross)


def detime_breakout_entries_exits(
    ohlcv: OHLCVLike,
    features: dict[str, pd.DataFrame],
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    min_trend_slope: float = -0.001,
    min_trend_strength: float = -np.inf,
    min_volume_residual_z: float = -0.85,
    require_cycle_confirmation: bool = True,
    min_cycle_slope: float = -0.02,
    max_residual_overextension: float = 2.25,
    allow_short: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    """Donchian breakout gated by trend, cycle, residual and volume state."""

    close, high, low = _field(ohlcv, "Close"), _field(ohlcv, "High"), _field(ohlcv, "Low")
    le, lx, se, sx = donchian_breakout_signals(close, high, low, entry_window=entry_window, exit_window=exit_window, allow_short=allow_short)

    trend_slope = _feature(features, "trend_slope", close, fill=0.0)
    trend_strength = _feature(features, "trend_strength", close, fill=0.0)
    cycle_slope = _feature(features, "cycle_slope", close, fill=0.0)
    residual_z = _feature(features, "residual_z", close, fill=0.0)
    stable = decomposition_risk_mask(close, features, max_abs_residual_z=max_residual_overextension)
    volume_ok = volume_confirmation_mask(close, features, min_volume_trend_slope=-0.005, min_volume_residual_z=min_volume_residual_z)

    long_context = (trend_slope > float(min_trend_slope)) & (trend_strength > float(min_trend_strength)) & stable & volume_ok
    if require_cycle_confirmation:
        long_context &= cycle_slope >= float(min_cycle_slope)
    long_entries = le & long_context & (residual_z < float(max_residual_overextension))
    long_exits = lx | (trend_slope < 0.0) | ((cycle_slope < 0.0) & (residual_z > 0.75)) | (~stable)

    if not allow_short:
        return long_entries.fillna(False), long_exits.fillna(False), None, None

    short_context = (trend_slope < -float(min_trend_slope)) & (trend_strength < -float(min_trend_strength)) & stable & volume_ok
    if require_cycle_confirmation:
        short_context &= cycle_slope <= -float(min_cycle_slope)
    assert se is not None and sx is not None
    short_entries = se & short_context & (residual_z > -float(max_residual_overextension))
    short_exits = sx | (trend_slope > 0.0) | ((cycle_slope > 0.0) & (residual_z < -0.75)) | (~stable)
    return long_entries.fillna(False), long_exits.fillna(False), short_entries.fillna(False), short_exits.fillna(False)


def detime_donchian_breakout_weights(
    ohlcv: OHLCVLike,
    features: dict[str, pd.DataFrame],
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = detime_breakout_entries_exits(
        ohlcv,
        features,
        entry_window=entry_window,
        exit_window=exit_window,
        min_trend_slope=-0.001,
        min_volume_residual_z=-0.85,
        require_cycle_confirmation=True,
        min_cycle_slope=-0.02,
        allow_short=allow_short,
    )
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def detime_turtle_volume_breakout_weights(
    ohlcv: OHLCVLike,
    features: dict[str, pd.DataFrame],
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = detime_breakout_entries_exits(
        ohlcv,
        features,
        entry_window=entry_window,
        exit_window=exit_window,
        min_trend_slope=-0.001,
        min_trend_strength=0.0,
        min_volume_residual_z=-0.75,
        require_cycle_confirmation=True,
        min_cycle_slope=-0.02,
        max_residual_overextension=3.25,
        allow_short=allow_short,
    )
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def detime_breakout_without_cycle_weights(
    ohlcv: OHLCVLike,
    features: dict[str, pd.DataFrame],
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Ablation: trend+volume breakout without cycle-turn confirmation."""

    le, lx, se, sx = detime_breakout_entries_exits(
        ohlcv,
        features,
        entry_window=entry_window,
        exit_window=exit_window,
        min_trend_slope=-0.001,
        min_volume_residual_z=-0.85,
        require_cycle_confirmation=False,
        allow_short=allow_short,
    )
    return _stateful_weights(le, lx, se, sx, max_gross=max_gross)


def breakout_diagnostic_table(ohlcv: OHLCVLike, features: dict[str, pd.DataFrame], *, entry_window: int = 55, exit_window: int = 20) -> pd.DataFrame:
    """Return the latest channel and DeTime breakout context for notebook display."""

    close, high, low = _field(ohlcv, "Close"), _field(ohlcv, "High"), _field(ohlcv, "Low")
    ch = donchian_channels(high, low, entry_window=entry_window, exit_window=exit_window)
    latest = []
    for asset in close.columns:
        last = close.index[-1]
        latest.append(
            {
                "asset": asset,
                "date": last,
                "close": float(close.loc[last, asset]),
                "donchian_upper_entry": float(ch.upper_entry.loc[last, asset]) if pd.notna(ch.upper_entry.loc[last, asset]) else np.nan,
                "donchian_lower_exit": float(ch.lower_exit.loc[last, asset]) if pd.notna(ch.lower_exit.loc[last, asset]) else np.nan,
                "trend_slope": float(_feature(features, "trend_slope", close, fill=0.0).loc[last, asset]),
                "cycle_slope": float(_feature(features, "cycle_slope", close, fill=0.0).loc[last, asset]),
                "residual_z": float(_feature(features, "residual_z", close, fill=0.0).loc[last, asset]),
                "volume_residual_z": float(_feature(features, "volume_residual_z", close, fill=0.0).loc[last, asset]),
            }
        )
    return pd.DataFrame(latest)


def make_classic_breakout_weight_grid(ohlcv: OHLCVLike, *, allow_short: bool = False) -> dict[str, pd.DataFrame]:
    return {
        "classic_donchian_55_20": classic_donchian_breakout_weights(ohlcv, entry_window=55, exit_window=20, allow_short=allow_short),
        "classic_donchian_20_10": classic_donchian_breakout_weights(ohlcv, entry_window=20, exit_window=10, allow_short=allow_short),
        "classic_turtle_55_20_atr_cap": classic_turtle_breakout_weights(ohlcv, entry_window=55, exit_window=20, allow_short=allow_short),
        "classic_volatility_breakout_20": classic_volatility_breakout_weights(ohlcv, lookback=20, allow_short=allow_short),
    }


def make_detime_breakout_weight_grid(ohlcv: OHLCVLike, features: dict[str, pd.DataFrame], *, allow_short: bool = False) -> dict[str, pd.DataFrame]:
    return {
        "detime_donchian_55_20_trend_cycle_volume": detime_donchian_breakout_weights(ohlcv, features, entry_window=55, exit_window=20, allow_short=allow_short),
        "detime_donchian_20_10_trend_cycle_volume": detime_donchian_breakout_weights(ohlcv, features, entry_window=20, exit_window=10, allow_short=allow_short),
        "detime_turtle_55_20_volume_shock": detime_turtle_volume_breakout_weights(ohlcv, features, entry_window=55, exit_window=20, allow_short=allow_short),
        "detime_breakout_trend_volume_no_cycle_ablation": detime_breakout_without_cycle_weights(ohlcv, features, entry_window=55, exit_window=20, allow_short=allow_short),
    }


def run_classical_breakout_baselines(
    ohlcv: OHLCVLike,
    *,
    allow_short: bool = False,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    close = _field(ohlcv, "Close")
    return {
        name: backtest_weights(close, weights, fee_bps=fee_bps, slippage_bps=slippage_bps)
        for name, weights in make_classic_breakout_weight_grid(ohlcv, allow_short=allow_short).items()
    }


def run_detime_breakout_baselines(
    ohlcv: OHLCVLike,
    features: dict[str, pd.DataFrame],
    *,
    allow_short: bool = False,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    close = _field(ohlcv, "Close")
    return {
        name: backtest_weights(close, weights, fee_bps=fee_bps, slippage_bps=slippage_bps)
        for name, weights in make_detime_breakout_weight_grid(ohlcv, features, allow_short=allow_short).items()
    }


def compare_breakout_suites(classical: dict[str, BacktestResult], detime: dict[str, BacktestResult]) -> pd.DataFrame:
    left = stats_table(classical).assign(strategy_group="classical_breakout")
    right = stats_table(detime).assign(strategy_group="detime_breakout")
    table = pd.concat([left, right], axis=0)
    order = ["strategy_group", "cagr", "sharpe", "max_drawdown", "calmar", "average_turnover", "average_gross_exposure", "total_return", "volatility", "hit_rate"]
    return table[[c for c in order if c in table.columns]].sort_values("sharpe", ascending=False)


breakout_baseline_suite = make_classic_breakout_weight_grid
detime_breakout_suite = make_detime_breakout_weight_grid
