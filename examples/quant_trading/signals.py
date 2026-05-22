from __future__ import annotations

"""Trading signal recipes built from De-Time decomposition features."""

import numpy as np
import pandas as pd


def _align(frame: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    return frame.reindex(index=prices.index, columns=prices.columns).ffill()


def trend_pullback_signals(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    residual_entry_z: float = -1.0,
    residual_exit_z: float = 0.25,
    min_trend_slope: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Long when trend is rising and residual is temporarily cheap."""

    trend_up = _align(features["trend_slope"], prices) > float(min_trend_slope)
    rz = _align(features["residual_z"], prices)
    entries = trend_up & (rz < float(residual_entry_z))
    exits = (~trend_up) | (rz > float(residual_exit_z))
    return entries.fillna(False), exits.fillna(False)


def residual_mean_reversion_signals(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    long_z: float = -1.5,
    short_z: float = 1.5,
    exit_z: float = 0.25,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Long and short signals from residual z-score mean reversion."""

    rz = _align(features["residual_z"], prices)
    long_entries = rz < float(long_z)
    long_exits = rz > -abs(float(exit_z))
    short_entries = rz > float(short_z)
    short_exits = rz < abs(float(exit_z))
    return long_entries.fillna(False), long_exits.fillna(False), short_entries.fillna(False), short_exits.fillna(False)


def turtle_donchian_signals(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame] | None = None,
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    use_trend_filter: bool = True,
    min_trend_slope: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Donchian/Turtle breakout with an optional De-Time trend filter."""

    clean = prices.sort_index().ffill().bfill()
    high = clean.rolling(int(entry_window), min_periods=max(5, int(entry_window) // 2)).max().shift(1)
    low_exit = clean.rolling(int(exit_window), min_periods=max(5, int(exit_window) // 2)).min().shift(1)
    entries = clean > high
    exits = clean < low_exit
    if use_trend_filter:
        if features is None or "trend_slope" not in features:
            raise ValueError("features['trend_slope'] is required when use_trend_filter=True.")
        entries = entries & (_align(features["trend_slope"], clean) > float(min_trend_slope))
    return entries.fillna(False), exits.fillna(False)


def residual_stress_filter(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    max_abs_residual_z: float = 3.0,
    require_positive_trend: bool = False,
) -> pd.DataFrame:
    """Boolean risk filter: trade only when residual stress is not extreme."""

    ok = _align(features["residual_abs_z"], prices) < float(max_abs_residual_z)
    if require_positive_trend:
        ok = ok & (_align(features["trend_slope"], prices) > 0)
    return ok.fillna(False)


def pair_trading_weights(
    x: pd.Series,
    y: pd.Series,
    *,
    lookback: int = 120,
    entry_z: float = 1.5,
    exit_z: float = 0.25,
    beta: float | None = None,
    spread_residual_z: pd.Series | None = None,
) -> pd.DataFrame:
    """Create pair-trading target weights from hedge-adjusted spread behavior.

    Positive spread z-score means `x` is rich relative to `y`: short `x`, long `y`.
    Negative spread z-score means `x` is cheap relative to `y`: long `x`, short `y`.
    """

    df = pd.concat({x.name or "x": x, y.name or "y": y}, axis=1).dropna().astype(float)
    left, right = df.columns
    if beta is None:
        rx = df[left].pct_change()
        ry = df[right].pct_change()
        cov = rx.rolling(lookback, min_periods=lookback // 2).cov(ry)
        var = ry.rolling(lookback, min_periods=lookback // 2).var()
        beta_s = (cov / (var + 1e-12)).clip(0.1, 5.0).fillna(1.0)
    else:
        beta_s = pd.Series(float(beta), index=df.index)

    spread = np.log(df[left]) - beta_s * np.log(df[right])
    z = (spread - spread.rolling(lookback, min_periods=lookback // 2).mean()) / (
        spread.rolling(lookback, min_periods=lookback // 2).std(ddof=0) + 1e-12
    )
    if spread_residual_z is not None:
        z = spread_residual_z.reindex(z.index).ffill().combine_first(z)

    raw_state = pd.Series(np.nan, index=df.index)
    raw_state[z > float(entry_z)] = -1.0
    raw_state[z < -float(entry_z)] = 1.0
    raw_state[z.abs() < float(exit_z)] = 0.0
    state = raw_state.ffill().fillna(0.0)

    weights = pd.DataFrame(index=df.index, columns=[left, right], dtype=float)
    weights[left] = 0.5 * state
    weights[right] = -0.5 * beta_s.reindex(df.index).fillna(1.0) * state
    gross = weights.abs().sum(axis=1).replace(0.0, np.nan)
    return weights.div(gross, axis=0).fillna(0.0)


def cross_sectional_rotation_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    top_n: int = 3,
    bottom_n: int = 0,
    long_short: bool = False,
    vol_target: float | None = 0.15,
    max_weight: float = 0.35,
) -> pd.DataFrame:
    """Turn De-Time features into daily top-N target weights."""

    ret = prices.pct_change()
    realized_vol = ret.rolling(20, min_periods=10).std(ddof=0) * np.sqrt(252)
    trend = _align(features["trend_slope"], prices)
    rz = _align(features["residual_z"], prices)
    season_slope = _align(features["season_slope"], prices)
    noise = _align(features.get("reconstruction_error", pd.DataFrame(0.0, index=prices.index, columns=prices.columns)), prices)

    score = (
        trend.rank(axis=1, pct=True)
        + (-rz).rank(axis=1, pct=True)
        + season_slope.rank(axis=1, pct=True)
        - 0.25 * noise.rank(axis=1, pct=True)
    )
    weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for dt, row in score.iterrows():
        valid = row.dropna()
        if valid.empty:
            continue
        longs = valid.nlargest(min(int(top_n), len(valid))).index
        weights.loc[dt, longs] = 1.0 / max(len(longs), 1)
        if long_short and int(bottom_n) > 0 and len(valid) > len(longs):
            shorts = valid.nsmallest(min(int(bottom_n), len(valid) - len(longs))).index
            weights.loc[dt, shorts] = -1.0 / max(len(shorts), 1)

    weights = weights.clip(-float(max_weight), float(max_weight))
    gross = weights.abs().sum(axis=1).replace(0.0, np.nan)
    weights = weights.div(gross, axis=0).fillna(0.0)

    if vol_target is not None:
        strategy_returns = (weights.shift(1).fillna(0.0) * ret).sum(axis=1)
        strategy_vol = strategy_returns.rolling(60, min_periods=20).std(ddof=0) * np.sqrt(252)
        leverage = (float(vol_target) / (strategy_vol + 1e-12)).clip(0.0, 2.0).fillna(1.0)
        weights = weights.mul(leverage, axis=0)
    return weights.fillna(0.0)
