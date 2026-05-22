from __future__ import annotations

"""Small vectorized research backtester for the De-Time quant column."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    equity = pd.Series(equity).dropna()
    if equity.empty:
        return float("nan")
    dd = equity / equity.cummax() - 1.0
    return float(dd.min())


def summarize_returns(returns: pd.Series, *, periods_per_year: int = 252) -> dict[str, float]:
    r = pd.Series(returns).replace([np.inf, -np.inf], np.nan).dropna()
    keys = ["total_return", "cagr", "volatility", "sharpe", "max_drawdown", "calmar", "hit_rate"]
    if r.empty:
        return {k: float("nan") for k in keys}
    equity = (1.0 + r).cumprod()
    n_years = max(len(r) / float(periods_per_year), 1e-12)
    total_return = float(equity.iloc[-1] - 1.0)
    cagr = float(equity.iloc[-1] ** (1.0 / n_years) - 1.0)
    vol = float(r.std(ddof=0) * np.sqrt(periods_per_year))
    sharpe = float((r.mean() * periods_per_year) / (vol + 1e-12))
    mdd = max_drawdown(equity)
    calmar = float(cagr / abs(mdd)) if mdd < 0 else float("nan")
    hit_rate = float((r > 0).mean())
    return {
        "total_return": total_return,
        "cagr": cagr,
        "volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "calmar": calmar,
        "hit_rate": hit_rate,
    }


@dataclass
class BacktestResult:
    returns: pd.Series
    equity: pd.Series
    weights: pd.DataFrame
    asset_returns: pd.DataFrame
    costs: pd.Series
    turnover: pd.Series
    stats: dict[str, float]

    def stats_frame(self) -> pd.DataFrame:
        return pd.DataFrame([self.stats]).T.rename(columns={0: "value"})


def backtest_weights(
    prices: pd.DataFrame,
    weights: pd.DataFrame,
    *,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    periods_per_year: int = 252,
) -> BacktestResult:
    """Close-to-close backtest from target weights.

    Positions are shifted by one bar to reduce same-bar look-ahead. Costs are
    charged on absolute target-weight turnover. This is a research-level signal
    tester, not a fill simulator.
    """

    clean = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    w = weights.reindex(index=clean.index, columns=clean.columns).fillna(0.0)
    asset_returns = clean.pct_change().fillna(0.0)
    held = w.shift(1).fillna(0.0)
    gross_returns = (held * asset_returns).sum(axis=1)
    turnover = w.diff().abs().sum(axis=1).fillna(w.abs().sum(axis=1))
    costs = turnover * (float(fee_bps) + float(slippage_bps)) / 10000.0
    returns = gross_returns - costs
    equity = (1.0 + returns).cumprod()
    stats = summarize_returns(returns, periods_per_year=periods_per_year)
    stats.update(
        {
            "average_turnover": float(turnover.mean()),
            "average_gross_exposure": float(w.abs().sum(axis=1).mean()),
            "fee_bps": float(fee_bps),
            "slippage_bps": float(slippage_bps),
            "periods_per_year": float(periods_per_year),
        }
    )
    return BacktestResult(returns=returns, equity=equity, weights=w, asset_returns=asset_returns, costs=costs, turnover=turnover, stats=stats)


def signals_to_weights(
    long_entries: pd.DataFrame,
    long_exits: pd.DataFrame,
    *,
    short_entries: pd.DataFrame | None = None,
    short_exits: pd.DataFrame | None = None,
    equal_weight: bool = True,
) -> pd.DataFrame:
    idx = long_entries.index
    cols = long_entries.columns
    pos = pd.DataFrame(0.0, index=idx, columns=cols)
    for col in cols:
        state = 0.0
        values: list[float] = []
        se = short_entries[col] if short_entries is not None and col in short_entries else pd.Series(False, index=idx)
        sx = short_exits[col] if short_exits is not None and col in short_exits else pd.Series(False, index=idx)
        for dt in idx:
            if state > 0 and bool(long_exits.loc[dt, col]):
                state = 0.0
            if state < 0 and bool(sx.loc[dt]):
                state = 0.0
            if state == 0.0 and bool(long_entries.loc[dt, col]):
                state = 1.0
            if state == 0.0 and bool(se.loc[dt]):
                state = -1.0
            values.append(state)
        pos[col] = values
    if equal_weight:
        gross = pos.abs().sum(axis=1).replace(0.0, np.nan)
        pos = pos.div(gross, axis=0).fillna(0.0)
    return pos


def backtest_long_short_signals(
    prices: pd.DataFrame,
    long_entries: pd.DataFrame,
    long_exits: pd.DataFrame,
    short_entries: pd.DataFrame | None = None,
    short_exits: pd.DataFrame | None = None,
    *,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    periods_per_year: int = 252,
) -> BacktestResult:
    weights = signals_to_weights(long_entries, long_exits, short_entries=short_entries, short_exits=short_exits)
    return backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps, periods_per_year=periods_per_year)


def train_test_split_by_date(frame: pd.DataFrame, split_date: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    split = pd.Timestamp(split_date)
    return frame.loc[frame.index < split], frame.loc[frame.index >= split]
