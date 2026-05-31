from __future__ import annotations

"""Column 06: cross-sectional rotation and portfolio construction.

Classic rotation ranks assets by raw trailing return or moving-average state.
The De-Time rewrite ranks assets by explicit trend quality, cycle timing,
residual pullback/overextension, volume participation and decomposition risk.
"""

from typing import Mapping

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_weights
from .classic_indicators import sma
from .strategy_baselines import buy_and_hold_weights, stats_table


def _clean(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.sort_index().astype(float).replace([np.inf, -np.inf], np.nan).ffill().bfill()


def _align(frame: pd.DataFrame | None, prices: pd.DataFrame, *, fill: float = 0.0) -> pd.DataFrame:
    if frame is None:
        return pd.DataFrame(float(fill), index=prices.index, columns=prices.columns)
    return frame.reindex(index=prices.index, columns=prices.columns).replace([np.inf, -np.inf], np.nan).ffill().fillna(float(fill))


def _rank(frame: pd.DataFrame, *, higher_is_better: bool = True) -> pd.DataFrame:
    return frame.rank(axis=1, pct=True, ascending=higher_is_better).fillna(0.5)


def normalize_gross(weights: pd.DataFrame, *, gross: float = 1.0) -> pd.DataFrame:
    w = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    denom = w.abs().sum(axis=1).replace(0.0, np.nan)
    return w.div(denom, axis=0).fillna(0.0) * float(gross)


def cap_and_normalize(weights: pd.DataFrame, *, max_weight: float = 0.40, gross: float = 1.0) -> pd.DataFrame:
    w = weights.clip(lower=-float(max_weight), upper=float(max_weight)) if max_weight else weights
    return normalize_gross(w, gross=gross)


def rebalance_weights(weights: pd.DataFrame, *, freq: str | None = "W-FRI") -> pd.DataFrame:
    """Hold target weights between rebalance dates without DataFrame.resample."""

    if freq is None or str(freq).upper() in {"D", "DAILY", "NONE"}:
        return weights.fillna(0.0)
    w = weights.sort_index().copy()
    idx = pd.DatetimeIndex(w.index)
    f = str(freq).upper()
    if f.startswith("W"):
        periods = idx.to_period("W-FRI")
    elif f in {"M", "ME", "MONTH", "MONTHLY"}:
        periods = idx.to_period("M")
    else:
        periods = idx.to_period(freq)
    marker = pd.Series(np.arange(len(idx)), index=idx)
    last_pos = marker.groupby(periods).max().astype(int).to_numpy()
    rebal_dates = idx[last_pos]
    held = w.copy()
    held.loc[~w.index.isin(rebal_dates), :] = np.nan
    return held.ffill().fillna(0.0)


def volatility_target_weights(prices: pd.DataFrame, weights: pd.DataFrame, *, target_vol: float | None = 0.15, lookback: int = 60, max_leverage: float = 1.5) -> pd.DataFrame:
    if target_vol is None:
        return weights.fillna(0.0)
    ret = _clean(prices).pct_change().fillna(0.0)
    strat = (weights.shift(1).fillna(0.0) * ret).sum(axis=1)
    vol = strat.rolling(int(lookback), min_periods=max(10, int(lookback) // 3)).std(ddof=0) * np.sqrt(252)
    lev = (float(target_vol) / (vol + 1e-12)).clip(0.0, float(max_leverage)).fillna(1.0)
    return weights.mul(lev, axis=0).fillna(0.0)


def _select_from_score(score: pd.DataFrame, *, top_n: int = 3, bottom_n: int = 0, long_short: bool = False) -> pd.DataFrame:
    w = pd.DataFrame(0.0, index=score.index, columns=score.columns)
    ncols = len(score.columns)
    for dt, row in score.iterrows():
        valid = row.replace([np.inf, -np.inf], np.nan).dropna()
        if valid.empty:
            continue
        n_long = min(max(int(top_n), 0), len(valid))
        if n_long:
            longs = valid.nlargest(n_long).index
            w.loc[dt, longs] = 1.0 / n_long
        if long_short and int(bottom_n) > 0 and len(valid) > n_long:
            n_short = min(int(bottom_n), len(valid) - n_long)
            shorts = valid.nsmallest(n_short).index
            w.loc[dt, shorts] = -1.0 / max(n_short, 1)
    return w


def classic_momentum_score(prices: pd.DataFrame, *, lookback: int = 63, skip: int = 0) -> pd.DataFrame:
    clean = _clean(prices)
    if int(skip) > 0:
        return clean.shift(int(skip)) / clean.shift(int(skip) + int(lookback)) - 1.0
    return clean / clean.shift(int(lookback)) - 1.0


def classic_momentum_rotation_weights(prices: pd.DataFrame, *, lookback: int = 63, skip: int = 0, top_n: int = 3, rebalance_freq: str | None = "W-FRI", vol_target: float | None = 0.15) -> pd.DataFrame:
    w = _select_from_score(classic_momentum_score(prices, lookback=lookback, skip=skip), top_n=top_n)
    w = cap_and_normalize(rebalance_weights(w, freq=rebalance_freq), max_weight=0.40)
    return volatility_target_weights(prices, w, target_vol=vol_target)


def classic_ma_trend_rotation_weights(prices: pd.DataFrame, *, fast: int = 50, slow: int = 200, top_n: int = 3, rebalance_freq: str | None = "W-FRI", vol_target: float | None = 0.15) -> pd.DataFrame:
    clean = _clean(prices)
    score = sma(clean, fast) / (sma(clean, slow) + 1e-12) - 1.0
    w = _select_from_score(score, top_n=top_n)
    w = cap_and_normalize(rebalance_weights(w, freq=rebalance_freq), max_weight=0.40)
    return volatility_target_weights(clean, w, target_vol=vol_target)


def inverse_vol_equal_weight(prices: pd.DataFrame, *, lookback: int = 60, rebalance_freq: str | None = "W-FRI", vol_target: float | None = 0.15) -> pd.DataFrame:
    clean = _clean(prices)
    vol = clean.pct_change().rolling(int(lookback), min_periods=max(10, int(lookback) // 3)).std(ddof=0)
    inv = 1.0 / (vol + 1e-12)
    w = inv.div(inv.sum(axis=1), axis=0).fillna(0.0)
    w = normalize_gross(rebalance_weights(w, freq=rebalance_freq))
    return volatility_target_weights(clean, w, target_vol=vol_target)


def detime_cross_sectional_score(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    clean = _clean(prices)
    trend_strength = _align(features.get("trend_strength"), clean)
    trend_slope = _align(features.get("trend_slope"), clean)
    cycle_slope = _align(features.get("cycle_slope"), clean)
    residual_z = _align(features.get("residual_z"), clean).clip(-3, 3)
    residual_abs_z = _align(features.get("residual_abs_z"), clean).clip(0, 5)
    stability = _align(features.get("component_stability"), clean, fill=1.0)
    volume = _align(features.get("volume_participation"), clean, fill=0.5)
    reconstruction_error = _align(features.get("reconstruction_error"), clean)
    score = (
        1.10 * _rank(trend_strength)
        + 0.55 * _rank(trend_slope)
        + 0.65 * _rank(cycle_slope)
        + 0.70 * _rank(-residual_z)
        + 0.45 * _rank(volume)
        + 0.25 * _rank(stability)
        - 0.65 * _rank(residual_abs_z)
        - 0.20 * _rank(reconstruction_error)
    )
    return score.where(trend_slope > 0.0, score - 0.75).replace([np.inf, -np.inf], np.nan)


def detime_rotation_score(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Backward-compatible alias used in the Column 06 notebook."""

    return detime_cross_sectional_score(prices, features)

def detime_rotation_weights(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, top_n: int = 3, rebalance_freq: str | None = "W-FRI", vol_target: float | None = 0.15, long_short: bool = False, bottom_n: int | None = None) -> pd.DataFrame:
    clean = _clean(prices)
    score = detime_cross_sectional_score(clean, features)
    stress = _align(features.get("residual_abs_z"), clean)
    score = score.where(stress <= 3.0)
    w = _select_from_score(score, top_n=top_n, bottom_n=int(bottom_n or top_n), long_short=long_short)
    w = cap_and_normalize(rebalance_weights(w, freq=rebalance_freq), max_weight=0.40)
    return volatility_target_weights(clean, w, target_vol=vol_target)


def detime_trend_rotation_weights(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, top_n: int = 3) -> pd.DataFrame:
    clean = _clean(prices)
    score = _rank(_align(features.get("trend_strength"), clean)) + _rank(_align(features.get("trend_slope"), clean))
    w = _select_from_score(score, top_n=top_n)
    return volatility_target_weights(clean, cap_and_normalize(rebalance_weights(w)), target_vol=0.15)


def detime_long_short_rotation_weights(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, top_n: int = 3, bottom_n: int = 3) -> pd.DataFrame:
    return detime_rotation_weights(prices, features, top_n=top_n, bottom_n=bottom_n, long_short=True, rebalance_freq="W-FRI", vol_target=0.12)


def make_classic_rotation_weight_grid(prices: pd.DataFrame, *, top_n: int = 3, rebalance: str | None = "W-FRI") -> dict[str, pd.DataFrame]:
    return {
        "buy_hold_equal_weight": buy_and_hold_weights(prices),
        "classic_momentum_63_top": classic_momentum_rotation_weights(prices, lookback=63, top_n=top_n, rebalance_freq=rebalance),
        "classic_momentum_252_21_top": classic_momentum_rotation_weights(prices, lookback=252, skip=21, top_n=top_n, rebalance_freq="M"),
        "classic_ma_trend_50_200_top": classic_ma_trend_rotation_weights(prices, top_n=top_n, rebalance_freq=rebalance),
        "classic_inverse_vol_equal_weight": inverse_vol_equal_weight(prices, rebalance_freq=rebalance),
    }


def make_detime_rotation_weight_grid(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, top_n: int = 3, rebalance: str | None = "W-FRI") -> dict[str, pd.DataFrame]:
    return {
        "detime_rotation_top_trend_cycle_residual_volume": detime_rotation_weights(prices, features, top_n=top_n, rebalance_freq=rebalance),
        "detime_rotation_monthly_low_turnover": detime_rotation_weights(prices, features, top_n=top_n, rebalance_freq="M", vol_target=0.12),
        "detime_rotation_no_voltarget_ablation": detime_rotation_weights(prices, features, top_n=top_n, rebalance_freq=rebalance, vol_target=None),
        "detime_rotation_long_short": detime_long_short_rotation_weights(prices, features, top_n=top_n, bottom_n=top_n),
    }


def rotation_factor_snapshot(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, tail_date: pd.Timestamp | None = None) -> pd.DataFrame:
    clean = _clean(prices)
    date = pd.Timestamp(tail_date) if tail_date is not None else clean.index[-1]
    score = detime_cross_sectional_score(clean, features).reindex(index=clean.index).ffill()
    rows = []
    for asset in clean.columns:
        rows.append({
            "date": date,
            "asset": asset,
            "score": float(score.loc[date, asset]),
            "trend_strength": float(_align(features.get("trend_strength"), clean).loc[date, asset]),
            "cycle_slope": float(_align(features.get("cycle_slope"), clean).loc[date, asset]),
            "residual_z": float(_align(features.get("residual_z"), clean).loc[date, asset]),
            "volume_participation": float(_align(features.get("volume_participation"), clean, fill=0.5).loc[date, asset]),
        })
    return pd.DataFrame(rows).sort_values("score", ascending=False)


def rotation_diagnostic_table(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, tail: int = 3) -> pd.DataFrame:
    return pd.concat([rotation_factor_snapshot(prices, features, tail_date=dt) for dt in prices.index[-int(tail):]], ignore_index=True)


def volume_availability(volumes: pd.DataFrame | None) -> bool:
    if volumes is None or volumes.empty:
        return False
    return bool(float(volumes.replace([np.inf, -np.inf], np.nan).fillna(0.0).abs().sum().sum()) > 0.0)


def compare_rotation_suites(classical: Mapping[str, BacktestResult], detime: Mapping[str, BacktestResult]) -> pd.DataFrame:
    table = pd.concat([stats_table(dict(classical)).assign(strategy_group="classical_rotation"), stats_table(dict(detime)).assign(strategy_group="detime_rotation")], axis=0)
    order = ["strategy_group", "cagr", "sharpe", "max_drawdown", "calmar", "average_turnover", "average_gross_exposure", "total_return", "volatility", "hit_rate"]
    return table[[c for c in order if c in table.columns]].sort_values("sharpe", ascending=False)


def run_classical_rotation_baselines(prices: pd.DataFrame, *, top_n: int = 3, rebalance: str | None = "W-FRI", fee_bps: float = 1.0, slippage_bps: float = 2.0) -> dict[str, BacktestResult]:
    return {name: backtest_weights(prices, w, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, w in make_classic_rotation_weight_grid(prices, top_n=top_n, rebalance=rebalance).items()}


def run_detime_rotation_baselines(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, top_n: int = 3, rebalance: str | None = "W-FRI", fee_bps: float = 1.0, slippage_bps: float = 2.0) -> dict[str, BacktestResult]:
    return {name: backtest_weights(prices, w, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, w in make_detime_rotation_weight_grid(prices, features, top_n=top_n, rebalance=rebalance).items()}


def run_rotation_suites(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame], *, top_n: int = 3, fee_bps: float = 1.0, slippage_bps: float = 2.0) -> tuple[pd.DataFrame, dict[str, BacktestResult]]:
    classical = run_classical_rotation_baselines(prices, top_n=top_n, fee_bps=fee_bps, slippage_bps=slippage_bps)
    detime = run_detime_rotation_baselines(prices, features, top_n=top_n, fee_bps=fee_bps, slippage_bps=slippage_bps)
    results = {**classical, **detime}
    table = compare_rotation_suites(classical, detime)
    return table, results


__all__ = [name for name in globals() if not name.startswith("_")]
