from __future__ import annotations

"""Concrete decomposition-based trading strategies and backtesting helpers.

This module is intentionally narrower than the earlier tutorial strategy map.  It
implements two complete strategy families that users can inspect end-to-end:

1. Trend following: trade when the decomposed trend is strong enough to define a
   regime.  Trend direction creates the signal; cycle/residual/volume components
   manage entry timing, overextension, and participation.
2. Oscillation reversion: trade only when the decomposed trend is weak.  The
   residual channel becomes the traded object: negative residual means price is
   below its current trend+cycle structure; positive residual means price is
   above that structure.

Both families output signals, target weights, order ledgers, round-trip trades,
performance summaries, and optional buy/sell charts.  The backtest is a
transparent next-bar research backtester: signals observed on bar t are filled
using the next available open if an Open column is supplied, otherwise the next
close is used as a proxy.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

from .backtest import max_drawdown, summarize_returns


FrameDict = dict[str, pd.DataFrame]


@dataclass(frozen=True)
class TrendFollowingConfig:
    """Controls for the decomposed trend-following strategy."""

    entry_trend_strength: float = 0.15
    exit_trend_strength: float = 0.02
    min_trend_slope: float = 0.0
    max_entry_cycle_position: float = 1.25
    max_entry_residual_abs_z: float = 2.50
    exit_residual_abs_z: float = 3.25
    use_volume_confirmation: bool = True
    min_volume_trend_slope: float = 0.0
    min_volume_residual_z: float = -0.75
    allow_short: bool = False
    max_gross: float = 1.0
    strength_cap: float = 1.25
    min_position_fraction: float = 0.25


@dataclass(frozen=True)
class OscillationReversionConfig:
    """Controls for the decomposed residual mean-reversion strategy."""

    entry_residual_z: float = 1.75
    exit_residual_z: float = 0.15
    max_abs_trend_strength: float = 0.35
    max_abs_trend_slope: float | None = None
    require_cycle_turn: bool = True
    use_volume_filter: bool = False
    min_volume_residual_z: float = -2.50
    allow_short: bool = False
    max_gross: float = 1.0
    residual_z_cap: float = 3.50
    min_position_fraction: float = 0.25


@dataclass(frozen=True)
class HybridRegimeConfig:
    """Controls for switching between trend following and reversion."""

    trend: TrendFollowingConfig = TrendFollowingConfig()
    reversion: OscillationReversionConfig = OscillationReversionConfig()
    trend_regime_strength: float = 0.35
    flat_regime_strength: float = 0.35


@dataclass
class SignalSet:
    """Signal and target-position bundle for a strategy."""

    name: str
    long_entries: pd.DataFrame
    long_exits: pd.DataFrame
    short_entries: pd.DataFrame | None
    short_exits: pd.DataFrame | None
    target_weights: pd.DataFrame
    diagnostics: dict[str, pd.DataFrame]


@dataclass
class DetailedBacktestResult:
    """Backtest output with portfolio series, orders, and round-trip trades."""

    name: str
    returns: pd.Series
    equity: pd.Series
    weights: pd.DataFrame
    asset_forward_returns: pd.DataFrame
    costs: pd.Series
    turnover: pd.Series
    orders: pd.DataFrame
    trades: pd.DataFrame
    stats: dict[str, float]

    def stats_frame(self) -> pd.DataFrame:
        return pd.DataFrame([self.stats], index=[self.name])


# ---------------------------------------------------------------------------
# Alignment helpers
# ---------------------------------------------------------------------------


def _as_frame(x: pd.Series | pd.DataFrame, *, columns: pd.Index | list[str] | None = None) -> pd.DataFrame:
    if isinstance(x, pd.Series):
        name = x.name or (columns[0] if columns is not None and len(columns) == 1 else "asset")
        return x.to_frame(name)
    return x.copy()


def _align_feature(features: Mapping[str, pd.DataFrame], name: str, prices: pd.DataFrame, *, fill: float = 0.0) -> pd.DataFrame:
    frame = features.get(name)
    if frame is None:
        return pd.DataFrame(float(fill), index=prices.index, columns=prices.columns)
    return frame.reindex(index=prices.index, columns=prices.columns).replace([np.inf, -np.inf], np.nan).ffill().fillna(float(fill))


def _bool_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.replace([np.inf, -np.inf], np.nan).fillna(False).astype(bool)


def _volume_ok(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, min_volume_trend_slope: float, min_volume_residual_z: float) -> pd.DataFrame:
    if "volume_trend_slope" not in features and "volume_residual_z" not in features:
        return pd.DataFrame(True, index=prices.index, columns=prices.columns)
    vt = _align_feature(features, "volume_trend_slope", prices, fill=0.0)
    vr = _align_feature(features, "volume_residual_z", prices, fill=0.0)
    return _bool_frame((vt >= float(min_volume_trend_slope)) | (vr >= float(min_volume_residual_z)))


def _normalize_gross(raw_position: pd.DataFrame, *, max_gross: float) -> pd.DataFrame:
    pos = raw_position.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    gross = pos.abs().sum(axis=1)
    scale = pd.Series(1.0, index=pos.index)
    too_large = gross > float(max_gross)
    scale.loc[too_large] = float(max_gross) / gross.loc[too_large]
    return pos.mul(scale, axis=0).fillna(0.0)


def _position_size_from_score(score: pd.DataFrame, *, cap: float, min_fraction: float, max_gross: float) -> pd.DataFrame:
    cap = max(float(cap), 1e-12)
    size = (score.abs().clip(lower=0.0, upper=cap) / cap).fillna(0.0)
    size = float(min_fraction) + (1.0 - float(min_fraction)) * size
    return (size * float(max_gross)).clip(lower=0.0, upper=float(max_gross))


def positions_from_signals(
    long_entries: pd.DataFrame,
    long_exits: pd.DataFrame,
    *,
    short_entries: pd.DataFrame | None = None,
    short_exits: pd.DataFrame | None = None,
    size: pd.DataFrame | None = None,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Convert entry/exit events to target weights.

    Entries are stateful: a new long signal is ignored while already long, and a
    new short signal is ignored while already short.  A reversal first closes the
    existing side and then opens the opposite side on the same signal date.
    """

    idx = long_entries.index
    cols = long_entries.columns
    le = _bool_frame(long_entries.reindex(index=idx, columns=cols))
    lx = _bool_frame(long_exits.reindex(index=idx, columns=cols))
    se = _bool_frame(short_entries.reindex(index=idx, columns=cols)) if short_entries is not None else pd.DataFrame(False, index=idx, columns=cols)
    sx = _bool_frame(short_exits.reindex(index=idx, columns=cols)) if short_exits is not None else pd.DataFrame(False, index=idx, columns=cols)
    if size is None:
        sz = pd.DataFrame(1.0, index=idx, columns=cols)
    else:
        sz = size.reindex(index=idx, columns=cols).replace([np.inf, -np.inf], np.nan).ffill().fillna(0.0).clip(lower=0.0)

    out = pd.DataFrame(0.0, index=idx, columns=cols)
    for col in cols:
        state = 0
        values: list[float] = []
        for dt in idx:
            long_exit_now = bool(lx.loc[dt, col])
            short_exit_now = bool(sx.loc[dt, col])
            long_entry_now = bool(le.loc[dt, col])
            short_entry_now = bool(se.loc[dt, col])

            if state > 0 and (long_exit_now or short_entry_now):
                state = 0
            elif state < 0 and (short_exit_now or long_entry_now):
                state = 0

            if state == 0:
                if long_entry_now:
                    state = 1
                elif short_entry_now:
                    state = -1

            values.append(float(state) * float(sz.loc[dt, col]))
        out[col] = values
    return _normalize_gross(out, max_gross=max_gross)


# ---------------------------------------------------------------------------
# Strategy family 1: trend following
# ---------------------------------------------------------------------------


def decomposition_trend_following_signals(
    prices: pd.DataFrame,
    features: Mapping[str, pd.DataFrame],
    *,
    config: TrendFollowingConfig | None = None,
    name: str = "detime_trend_following",
) -> SignalSet:
    """Trend-following strategy driven by the decomposed trend component.

    Logic:
    - enter long when the trend slope and normalized trend strength are positive;
    - optionally enter short when they are negative;
    - avoid buying when the cycle is already too high or the residual is already
      too stretched;
    - require volume participation if volume decomposition exists;
    - size the position by trend strength.
    """

    cfg = config or TrendFollowingConfig()
    px = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    trend_slope = _align_feature(features, "trend_slope", px, fill=0.0)
    trend_strength = _align_feature(features, "trend_strength", px, fill=0.0)
    cycle_position = _align_feature(features, "cycle_position", px, fill=0.0)
    residual_abs_z = _align_feature(features, "residual_abs_z", px, fill=0.0)

    volume_ok = _volume_ok(
        px,
        features,
        min_volume_trend_slope=cfg.min_volume_trend_slope,
        min_volume_residual_z=cfg.min_volume_residual_z,
    ) if cfg.use_volume_confirmation else pd.DataFrame(True, index=px.index, columns=px.columns)

    long_entries = (
        (trend_slope > float(cfg.min_trend_slope))
        & (trend_strength > float(cfg.entry_trend_strength))
        & (cycle_position < float(cfg.max_entry_cycle_position))
        & (residual_abs_z < float(cfg.max_entry_residual_abs_z))
        & volume_ok
    )
    long_exits = (
        (trend_slope < -abs(float(cfg.min_trend_slope)))
        | (trend_strength < float(cfg.exit_trend_strength))
        | (residual_abs_z > float(cfg.exit_residual_abs_z))
    )

    if cfg.allow_short:
        short_entries = (
            (trend_slope < -abs(float(cfg.min_trend_slope)))
            & (trend_strength < -abs(float(cfg.entry_trend_strength)))
            & (cycle_position > -float(cfg.max_entry_cycle_position))
            & (residual_abs_z < float(cfg.max_entry_residual_abs_z))
            & volume_ok
        )
        short_exits = (
            (trend_slope > abs(float(cfg.min_trend_slope)))
            | (trend_strength > -float(cfg.exit_trend_strength))
            | (residual_abs_z > float(cfg.exit_residual_abs_z))
        )
    else:
        short_entries = short_exits = None

    size = _position_size_from_score(
        trend_strength,
        cap=cfg.strength_cap,
        min_fraction=cfg.min_position_fraction,
        max_gross=cfg.max_gross,
    )
    weights = positions_from_signals(
        _bool_frame(long_entries),
        _bool_frame(long_exits),
        short_entries=None if short_entries is None else _bool_frame(short_entries),
        short_exits=None if short_exits is None else _bool_frame(short_exits),
        size=size,
        max_gross=cfg.max_gross,
    )
    diagnostics = {
        "trend_slope": trend_slope,
        "trend_strength": trend_strength,
        "cycle_position": cycle_position,
        "residual_abs_z": residual_abs_z,
        "volume_ok": volume_ok.astype(float),
        "position_size": size,
    }
    return SignalSet(name=name, long_entries=_bool_frame(long_entries), long_exits=_bool_frame(long_exits), short_entries=short_entries, short_exits=short_exits, target_weights=weights, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# Strategy family 2: oscillation / residual reversion
# ---------------------------------------------------------------------------


def decomposition_oscillation_reversion_signals(
    prices: pd.DataFrame,
    features: Mapping[str, pd.DataFrame],
    *,
    config: OscillationReversionConfig | None = None,
    name: str = "detime_oscillation_reversion",
) -> SignalSet:
    """Residual mean-reversion strategy for weak-trend regimes.

    Logic:
    - first demand a weak-trend/sideways regime;
    - use residual_z as the traded deviation from trend+cycle fair value;
    - buy when residual_z is strongly negative;
    - sell or short when residual_z is strongly positive;
    - optionally require the cycle to turn in the trade direction.
    """

    cfg = config or OscillationReversionConfig()
    px = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    trend_slope = _align_feature(features, "trend_slope", px, fill=0.0)
    trend_strength = _align_feature(features, "trend_strength", px, fill=0.0)
    cycle_slope = _align_feature(features, "cycle_slope", px, fill=0.0)
    residual_z = _align_feature(features, "residual_z", px, fill=0.0)
    residual_vol = _align_feature(features, "residual_vol", px, fill=np.nan)
    trend = _align_feature(features, "trend", px, fill=np.nan)
    cycle = _align_feature(features, "cycle", px, fill=0.0)

    weak_trend = trend_strength.abs() <= float(cfg.max_abs_trend_strength)
    if cfg.max_abs_trend_slope is not None:
        weak_trend = weak_trend & (trend_slope.abs() <= float(cfg.max_abs_trend_slope))

    cycle_long_ok = cycle_slope >= 0.0 if cfg.require_cycle_turn else pd.DataFrame(True, index=px.index, columns=px.columns)
    cycle_short_ok = cycle_slope <= 0.0 if cfg.require_cycle_turn else pd.DataFrame(True, index=px.index, columns=px.columns)
    volume_ok = _volume_ok(px, features, min_volume_trend_slope=-np.inf, min_volume_residual_z=cfg.min_volume_residual_z) if cfg.use_volume_filter else pd.DataFrame(True, index=px.index, columns=px.columns)

    entry_z = abs(float(cfg.entry_residual_z))
    exit_z = abs(float(cfg.exit_residual_z))
    long_entries = (residual_z <= -entry_z) & weak_trend & cycle_long_ok & volume_ok
    long_exits = (residual_z >= -exit_z) | (~weak_trend)

    if cfg.allow_short:
        short_entries = (residual_z >= entry_z) & weak_trend & cycle_short_ok & volume_ok
        short_exits = (residual_z <= exit_z) | (~weak_trend)
    else:
        short_entries = short_exits = None

    size = _position_size_from_score(
        residual_z,
        cap=cfg.residual_z_cap,
        min_fraction=cfg.min_position_fraction,
        max_gross=cfg.max_gross,
    )
    weights = positions_from_signals(
        _bool_frame(long_entries),
        _bool_frame(long_exits),
        short_entries=None if short_entries is None else _bool_frame(short_entries),
        short_exits=None if short_exits is None else _bool_frame(short_exits),
        size=size,
        max_gross=cfg.max_gross,
    )

    fair_log = trend + cycle
    fair_value = np.exp(fair_log).where(np.isfinite(fair_log))
    band_width = residual_vol.fillna(residual_z.rolling(63, min_periods=10).std(ddof=0)).abs()
    upper_band = np.exp(fair_log + entry_z * band_width).where(np.isfinite(fair_log))
    lower_band = np.exp(fair_log - entry_z * band_width).where(np.isfinite(fair_log))

    diagnostics = {
        "trend_slope": trend_slope,
        "trend_strength": trend_strength,
        "weak_trend_regime": weak_trend.astype(float),
        "cycle_slope": cycle_slope,
        "residual_z": residual_z,
        "fair_value": fair_value,
        "upper_residual_band": upper_band,
        "lower_residual_band": lower_band,
        "position_size": size,
    }
    return SignalSet(name=name, long_entries=_bool_frame(long_entries), long_exits=_bool_frame(long_exits), short_entries=short_entries, short_exits=short_exits, target_weights=weights, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# Optional combined regime strategy
# ---------------------------------------------------------------------------


def decomposition_hybrid_regime_signals(
    prices: pd.DataFrame,
    features: Mapping[str, pd.DataFrame],
    *,
    config: HybridRegimeConfig | None = None,
    name: str = "detime_hybrid_regime",
) -> SignalSet:
    """Switch between trend-following and residual-reversion regimes."""

    cfg = config or HybridRegimeConfig()
    trend_sig = decomposition_trend_following_signals(prices, features, config=cfg.trend, name=f"{name}_trend_leg")
    rev_sig = decomposition_oscillation_reversion_signals(prices, features, config=cfg.reversion, name=f"{name}_reversion_leg")
    px = prices.sort_index().ffill().bfill()
    trend_strength = _align_feature(features, "trend_strength", px, fill=0.0)
    trend_regime = trend_strength.abs() >= float(cfg.trend_regime_strength)
    flat_regime = trend_strength.abs() <= float(cfg.flat_regime_strength)

    weights = trend_sig.target_weights.where(trend_regime, 0.0) + rev_sig.target_weights.where(flat_regime, 0.0)
    weights = _normalize_gross(weights, max_gross=max(cfg.trend.max_gross, cfg.reversion.max_gross))
    long_entries = _bool_frame((weights > 0.0) & (weights.shift(1).fillna(0.0) <= 0.0))
    long_exits = _bool_frame((weights <= 0.0) & (weights.shift(1).fillna(0.0) > 0.0))
    short_entries = _bool_frame((weights < 0.0) & (weights.shift(1).fillna(0.0) >= 0.0)) if (weights < 0.0).any().any() else None
    short_exits = _bool_frame((weights >= 0.0) & (weights.shift(1).fillna(0.0) < 0.0)) if short_entries is not None else None
    diagnostics = {
        "trend_regime": trend_regime.astype(float),
        "flat_regime": flat_regime.astype(float),
        "trend_leg_weight": trend_sig.target_weights,
        "reversion_leg_weight": rev_sig.target_weights,
    }
    diagnostics.update({f"trend_{k}": v for k, v in trend_sig.diagnostics.items() if k in {"trend_strength", "cycle_position", "residual_abs_z"}})
    diagnostics.update({f"reversion_{k}": v for k, v in rev_sig.diagnostics.items() if k in {"residual_z", "fair_value", "upper_residual_band", "lower_residual_band"}})
    return SignalSet(name=name, long_entries=long_entries, long_exits=long_exits, short_entries=short_entries, short_exits=short_exits, target_weights=weights, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# Next-bar backtest and trade diagnostics
# ---------------------------------------------------------------------------


def execution_price_panel(
    ohlcv_or_prices: pd.DataFrame | Mapping[str, pd.DataFrame],
    *,
    field: str = "Open",
    next_bar: bool = True,
) -> pd.DataFrame:
    """Return execution prices aligned to signal dates.

    If a single OHLCV table is passed, the output has one asset column named by
    ``frame.attrs['symbol']`` when available.  If a field panel dictionary is
    passed, the requested field is extracted directly.  If the requested field is
    missing, Close is used as a proxy.
    """

    if isinstance(ohlcv_or_prices, Mapping):
        source = ohlcv_or_prices.get(field) or ohlcv_or_prices.get("Close")
        if source is None:
            raise KeyError("OHLCV panel must contain Open or Close for execution prices")
        out = source.copy()
    else:
        frame = ohlcv_or_prices.copy()
        chosen = field if field in frame.columns else "Close" if "Close" in frame.columns else frame.columns[0]
        symbol = str(frame.attrs.get("symbol", "asset"))
        out = frame[chosen].rename(symbol).to_frame()
    out = out.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    return out.shift(-1) if next_bar else out


def _fill_dates(index: pd.Index) -> pd.Series:
    if len(index) == 0:
        return pd.Series(dtype="datetime64[ns]")
    values = list(index[1:]) + [pd.NaT]
    return pd.Series(values, index=index)


def build_order_ledger(weights: pd.DataFrame, execution_prices: pd.DataFrame, *, min_delta_weight: float = 1e-8) -> pd.DataFrame:
    """Return every target-weight change as an executable order record."""

    w = weights.reindex(index=execution_prices.index, columns=execution_prices.columns).fillna(0.0)
    delta = w.diff().fillna(w)
    fill_dates = _fill_dates(w.index)
    rows: list[dict[str, object]] = []
    for asset in w.columns:
        for signal_date, change in delta[asset].items():
            if not np.isfinite(change) or abs(float(change)) <= float(min_delta_weight):
                continue
            fill_date = fill_dates.loc[signal_date]
            fill_price = execution_prices.loc[signal_date, asset] if asset in execution_prices.columns else np.nan
            if pd.isna(fill_date) or not np.isfinite(fill_price):
                continue
            prev_weight = float(w[asset].shift(1).fillna(0.0).loc[signal_date])
            new_weight = float(w.loc[signal_date, asset])
            if change > 0 and prev_weight < 0 <= new_weight:
                action = "cover_to_long" if new_weight > 0 else "cover"
            elif change > 0:
                action = "buy"
            elif change < 0 and prev_weight > 0 >= new_weight:
                action = "sell_to_short" if new_weight < 0 else "sell"
            else:
                action = "sell_or_short"
            rows.append(
                {
                    "asset": asset,
                    "signal_date": signal_date,
                    "fill_date": fill_date,
                    "action": action,
                    "previous_weight": prev_weight,
                    "new_weight": new_weight,
                    "delta_weight": float(change),
                    "fill_price": float(fill_price),
                }
            )
    return pd.DataFrame(rows)


def build_round_trip_trades(weights: pd.DataFrame, execution_prices: pd.DataFrame, *, cost_rate: float = 0.0) -> pd.DataFrame:
    """Build approximate round-trip trades from sign changes in target weights."""

    w = weights.reindex(index=execution_prices.index, columns=execution_prices.columns).fillna(0.0)
    fill_dates = _fill_dates(w.index)
    rows: list[dict[str, object]] = []
    for asset in w.columns:
        current: dict[str, object] | None = None
        sign_prev = 0
        for i, signal_date in enumerate(w.index):
            weight = float(w.loc[signal_date, asset])
            sign_now = int(np.sign(weight))
            fill_date = fill_dates.loc[signal_date]
            fill_price = execution_prices.loc[signal_date, asset]
            if pd.isna(fill_date) or not np.isfinite(fill_price):
                continue

            if current is not None and (sign_now == 0 or sign_now != sign_prev):
                side = int(current["side"])
                entry_price = float(current["entry_price"])
                directional_return = side * (float(fill_price) / entry_price - 1.0)
                entry_weight = abs(float(current["entry_weight"]))
                trade_cost = float(cost_rate) * (entry_weight + abs(float(w.loc[signal_date, asset])))
                rows.append(
                    {
                        "asset": asset,
                        "side": "long" if side > 0 else "short",
                        "entry_signal_date": current["entry_signal_date"],
                        "entry_fill_date": current["entry_fill_date"],
                        "exit_signal_date": signal_date,
                        "exit_fill_date": fill_date,
                        "entry_price": entry_price,
                        "exit_price": float(fill_price),
                        "bars_held": int(i - int(current["entry_i"])),
                        "entry_weight": float(current["entry_weight"]),
                        "directional_return": float(directional_return),
                        "approx_weighted_return_after_cost": float(directional_return * entry_weight - trade_cost),
                    }
                )
                current = None

            if current is None and sign_now != 0:
                current = {
                    "asset": asset,
                    "side": sign_now,
                    "entry_i": i,
                    "entry_signal_date": signal_date,
                    "entry_fill_date": fill_date,
                    "entry_price": float(fill_price),
                    "entry_weight": float(weight),
                }
            sign_prev = sign_now
    return pd.DataFrame(rows)


def backtest_target_weights_next_bar(
    prices: pd.DataFrame,
    weights: pd.DataFrame,
    *,
    execution_prices: pd.DataFrame | None = None,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    periods_per_year: int = 252,
    name: str = "strategy",
) -> DetailedBacktestResult:
    """Backtest target weights with next-bar execution prices.

    ``weights`` are interpreted as target portfolio weights decided after seeing
    bar t.  They are filled on the next execution price aligned to t, and earn
    the forward return to the following execution price.
    """

    px = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    if execution_prices is None:
        execution_prices = px.shift(-1)
    exec_px = execution_prices.reindex(index=px.index, columns=px.columns).replace([np.inf, -np.inf], np.nan).ffill()
    w = weights.reindex(index=px.index, columns=px.columns).replace([np.inf, -np.inf], np.nan).ffill().fillna(0.0)
    fwd_returns = exec_px.shift(-1).div(exec_px).sub(1.0).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    gross_returns = (w * fwd_returns).sum(axis=1)
    turnover = w.diff().abs().sum(axis=1).fillna(w.abs().sum(axis=1))
    cost_rate = (float(fee_bps) + float(slippage_bps)) / 10000.0
    costs = turnover * cost_rate
    returns = (gross_returns - costs).fillna(0.0)
    equity = (1.0 + returns).cumprod()
    stats = summarize_returns(returns, periods_per_year=periods_per_year)
    stats.update(
        {
            "average_turnover": float(turnover.mean()),
            "average_gross_exposure": float(w.abs().sum(axis=1).mean()),
            "orders": 0.0,
            "round_trips": 0.0,
            "fee_bps": float(fee_bps),
            "slippage_bps": float(slippage_bps),
            "periods_per_year": float(periods_per_year),
            "execution_model": "signal_on_bar_t_fill_next_bar_open_or_proxy",
        }
    )
    orders = build_order_ledger(w, exec_px)
    trades = build_round_trip_trades(w, exec_px, cost_rate=cost_rate)
    stats["orders"] = float(len(orders))
    stats["round_trips"] = float(len(trades))
    if not trades.empty:
        stats["trade_win_rate"] = float((trades["directional_return"] > 0).mean())
        stats["average_trade_directional_return"] = float(trades["directional_return"].mean())
        stats["median_bars_held"] = float(trades["bars_held"].median())
    else:
        stats["trade_win_rate"] = float("nan")
        stats["average_trade_directional_return"] = float("nan")
        stats["median_bars_held"] = float("nan")
    return DetailedBacktestResult(
        name=name,
        returns=returns,
        equity=equity,
        weights=w,
        asset_forward_returns=fwd_returns,
        costs=costs,
        turnover=turnover,
        orders=orders,
        trades=trades,
        stats=stats,
    )


def backtest_signal_set(
    prices: pd.DataFrame,
    signal_set: SignalSet,
    *,
    execution_prices: pd.DataFrame | None = None,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    periods_per_year: int = 252,
) -> DetailedBacktestResult:
    return backtest_target_weights_next_bar(
        prices,
        signal_set.target_weights,
        execution_prices=execution_prices,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        periods_per_year=periods_per_year,
        name=signal_set.name,
    )


def stats_table(results: Mapping[str, DetailedBacktestResult]) -> pd.DataFrame:
    rows = []
    for name, result in results.items():
        row = {"strategy": name}
        row.update(result.stats)
        rows.append(row)
    table = pd.DataFrame(rows)
    if table.empty:
        return table
    preferred = [
        "strategy",
        "total_return",
        "cagr",
        "sharpe",
        "max_drawdown",
        "calmar",
        "volatility",
        "hit_rate",
        "trade_win_rate",
        "average_trade_directional_return",
        "orders",
        "round_trips",
        "median_bars_held",
        "average_turnover",
        "average_gross_exposure",
    ]
    return table[[c for c in preferred if c in table.columns] + [c for c in table.columns if c not in preferred]].sort_values("sharpe", ascending=False, na_position="last")


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_signal_analysis(
    ohlcv: pd.DataFrame,
    signal_set: SignalSet,
    backtest: DetailedBacktestResult,
    *,
    asset: str | None = None,
    output_path: str | Path | None = None,
    title: str | None = None,
) -> Path | None:
    """Create a compact buy/sell analysis chart for one asset."""

    import matplotlib.pyplot as plt

    symbol = asset or str(ohlcv.attrs.get("symbol", signal_set.target_weights.columns[0]))
    if symbol not in signal_set.target_weights.columns:
        symbol = signal_set.target_weights.columns[0]
    price_col = "Close" if "Close" in ohlcv.columns else ohlcv.columns[0]
    close = ohlcv[price_col].reindex(signal_set.target_weights.index).ffill()
    idx = close.index

    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.0, 1.0, 1.0]})
    axes[0].plot(idx, close, label="close")
    if "fair_value" in signal_set.diagnostics:
        fv = signal_set.diagnostics["fair_value"][symbol].reindex(idx)
        axes[0].plot(idx, fv, label="trend + cycle fair value", alpha=0.8)
    if "upper_residual_band" in signal_set.diagnostics and "lower_residual_band" in signal_set.diagnostics:
        upper = signal_set.diagnostics["upper_residual_band"][symbol].reindex(idx)
        lower = signal_set.diagnostics["lower_residual_band"][symbol].reindex(idx)
        axes[0].plot(idx, upper, linestyle="--", alpha=0.6, label="residual upper band")
        axes[0].plot(idx, lower, linestyle="--", alpha=0.6, label="residual lower band")

    # Plot executed target-weight changes rather than every raw exit condition.
    orders = backtest.orders.copy() if isinstance(backtest.orders, pd.DataFrame) else pd.DataFrame()
    if not orders.empty and "asset" in orders.columns:
        orders = orders[orders["asset"].astype(str).eq(str(symbol))].copy()
        orders["fill_date"] = pd.to_datetime(orders["fill_date"], errors="coerce")
        orders = orders.dropna(subset=["fill_date"])
        order_price = close.reindex(orders["fill_date"]).to_numpy()
        long_entry_mask = (orders["new_weight"] > 0) & (orders["previous_weight"] <= 0)
        long_exit_mask = (orders["previous_weight"] > 0) & (orders["new_weight"] <= 0)
        short_entry_mask = (orders["new_weight"] < 0) & (orders["previous_weight"] >= 0)
        short_exit_mask = (orders["previous_weight"] < 0) & (orders["new_weight"] >= 0)
        axes[0].scatter(orders.loc[long_entry_mask, "fill_date"], order_price[long_entry_mask.to_numpy()], marker="^", s=55, label="buy / long entry")
        axes[0].scatter(orders.loc[long_exit_mask, "fill_date"], order_price[long_exit_mask.to_numpy()], marker="v", s=45, label="sell / long exit")
        if short_entry_mask.any():
            axes[0].scatter(orders.loc[short_entry_mask, "fill_date"], order_price[short_entry_mask.to_numpy()], marker="v", s=55, label="short entry")
        if short_exit_mask.any():
            axes[0].scatter(orders.loc[short_exit_mask, "fill_date"], order_price[short_exit_mask.to_numpy()], marker="^", s=45, label="cover / short exit")
    axes[0].set_ylabel("price")
    axes[0].legend(loc="best", fontsize=8)

    if "trend_strength" in signal_set.diagnostics:
        axes[1].plot(idx, signal_set.diagnostics["trend_strength"][symbol].reindex(idx), label="trend strength")
        axes[1].axhline(0.0, linewidth=0.8)
        axes[1].legend(loc="best", fontsize=8)
    elif "residual_z" in signal_set.diagnostics:
        axes[1].plot(idx, signal_set.diagnostics["residual_z"][symbol].reindex(idx), label="residual z")
        axes[1].axhline(0.0, linewidth=0.8)
        axes[1].legend(loc="best", fontsize=8)

    if "residual_z" in signal_set.diagnostics:
        axes[2].plot(idx, signal_set.diagnostics["residual_z"][symbol].reindex(idx), label="residual z")
        axes[2].axhline(0.0, linewidth=0.8)
    elif "cycle_position" in signal_set.diagnostics:
        axes[2].plot(idx, signal_set.diagnostics["cycle_position"][symbol].reindex(idx), label="cycle position")
        axes[2].axhline(0.0, linewidth=0.8)
    handles2, labels2 = axes[2].get_legend_handles_labels()
    if labels2:
        axes[2].legend(loc="best", fontsize=8)

    axes[3].plot(idx, signal_set.target_weights[symbol].reindex(idx), label="target weight")
    ax2 = axes[3].twinx()
    ax2.plot(backtest.equity.reindex(idx), label="equity", alpha=0.75)
    axes[3].axhline(0.0, linewidth=0.8)
    axes[3].set_ylabel("weight")
    ax2.set_ylabel("equity")
    lines, labels = axes[3].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    axes[3].legend(lines + lines2, labels + labels2, loc="best", fontsize=8)

    fig.suptitle(title or f"{signal_set.name}: {symbol}")
    fig.tight_layout()
    if output_path is None:
        plt.show()
        return None
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


__all__ = [
    "TrendFollowingConfig",
    "OscillationReversionConfig",
    "HybridRegimeConfig",
    "SignalSet",
    "DetailedBacktestResult",
    "decomposition_trend_following_signals",
    "decomposition_oscillation_reversion_signals",
    "decomposition_hybrid_regime_signals",
    "positions_from_signals",
    "execution_price_panel",
    "backtest_target_weights_next_bar",
    "backtest_signal_set",
    "build_order_ledger",
    "build_round_trip_trades",
    "stats_table",
    "plot_signal_analysis",
]
