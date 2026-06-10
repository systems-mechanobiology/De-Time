from __future__ import annotations

"""Classical and decomposition-aware strategy recipes for tutorials 01-02."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_long_short_signals, backtest_weights, signals_to_weights
from .indicators import dual_moving_average_signal, macd, macd_signal, multi_ma_alignment


def _align(frame: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    return frame.reindex(index=prices.index, columns=prices.columns).ffill()


@dataclass(frozen=True)
class StrategySpec:
    name: str
    family: str
    description: str
    uses_decomposition: bool
    uses_volume: bool = False


STRATEGY_SPECS: dict[str, StrategySpec] = {
    "classic_dual_ma": StrategySpec(
        "classic_dual_ma", "trend_following", "Classic long/flat dual moving-average crossover.", False
    ),
    "classic_macd": StrategySpec("classic_macd", "trend_following", "Classic MACD crossover on raw price.", False),
    "detime_trend_gate": StrategySpec(
        "detime_trend_gate", "trend_following", "Trend signal from explicit DeTime trend slope and reliability filters.", True
    ),
    "detime_dual_ma": StrategySpec(
        "detime_dual_ma", "trend_following", "Dual moving-average logic gated by trend, cycle, and residual state.", True
    ),
    "detime_macd": StrategySpec(
        "detime_macd", "trend_following", "MACD computed on DeTime trend instead of raw noisy price.", True
    ),
    "detime_volume_confirmed_trend": StrategySpec(
        "detime_volume_confirmed_trend", "trend_following", "DeTime trend signal confirmed by decomposed volume participation.", True, True
    ),
}


def buy_and_hold_weights(prices: pd.DataFrame) -> pd.DataFrame:
    """Equal-weight buy-and-hold target weights."""

    w = pd.DataFrame(1.0, index=prices.index, columns=prices.columns)
    return w.div(w.sum(axis=1), axis=0).fillna(0.0)


def classic_dual_ma_weights(
    prices: pd.DataFrame,
    *,
    fast: int = 20,
    slow: int = 100,
    equal_weight: bool = True,
) -> pd.DataFrame:
    entries, exits = dual_moving_average_signal(prices, fast=fast, slow=slow)
    return signals_to_weights(entries, exits, equal_weight=equal_weight)


def classic_macd_weights(
    prices: pd.DataFrame,
    *,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    equal_weight: bool = True,
) -> pd.DataFrame:
    entries, exits = macd_signal(prices, fast=fast, slow=slow, signal=signal)
    return signals_to_weights(entries, exits, equal_weight=equal_weight)


def detime_trend_gate_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    min_trend_slope: float = 0.0,
    min_trend_strength: float = 0.0,
    max_abs_residual_z: float = 2.5,
    require_cycle_not_falling: bool = True,
    equal_weight: bool = True,
) -> pd.DataFrame:
    """Long when explicit trend is positive and component reliability is acceptable."""

    trend = _align(features["trend_slope"], prices)
    strength = _align(features.get("trend_strength", pd.DataFrame(0.0, index=prices.index, columns=prices.columns)), prices)
    rz_abs = _align(features["residual_abs_z"], prices)
    cycle_slope = _align(features.get("cycle_slope", features.get("season_slope")), prices)

    entries = (trend > float(min_trend_slope)) & (strength >= float(min_trend_strength)) & (rz_abs < float(max_abs_residual_z))
    if require_cycle_not_falling:
        entries = entries & (cycle_slope >= 0)
    exits = (trend <= float(min_trend_slope)) | (rz_abs >= float(max_abs_residual_z)) | (cycle_slope < 0)
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=equal_weight)


def detime_dual_ma_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    fast: int = 20,
    slow: int = 100,
    min_trend_slope: float = 0.0,
    max_abs_residual_z: float = 2.5,
    equal_weight: bool = True,
) -> pd.DataFrame:
    """Classic dual-MA entries gated by DeTime trend/cycle/residual context."""

    ma_entries, ma_exits = dual_moving_average_signal(prices, fast=fast, slow=slow)
    trend = _align(features["trend_slope"], prices)
    cycle_slope = _align(features.get("cycle_slope", features.get("season_slope")), prices)
    rz_abs = _align(features["residual_abs_z"], prices)
    entries = ma_entries & (trend > float(min_trend_slope)) & (cycle_slope >= 0) & (rz_abs < float(max_abs_residual_z))
    exits = ma_exits | (trend <= float(min_trend_slope)) | (rz_abs >= float(max_abs_residual_z))
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=equal_weight)


def detime_macd_weights(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    max_abs_residual_z: float = 2.5,
    equal_weight: bool = True,
) -> pd.DataFrame:
    """Compute MACD on the explicit DeTime trend component."""

    trend = _align(features["trend"], prices)
    macd_line, signal_line, hist = macd(trend, fast=fast, slow=slow, signal=signal)
    rz_abs = _align(features["residual_abs_z"], prices)
    cycle_slope = _align(features.get("cycle_slope", features.get("season_slope")), prices)
    entries = (macd_line > signal_line) & (hist > 0) & (cycle_slope >= 0) & (rz_abs < float(max_abs_residual_z))
    exits = (macd_line < signal_line) | (hist < 0) | (rz_abs >= float(max_abs_residual_z))
    return signals_to_weights(entries.fillna(False), exits.fillna(False), equal_weight=equal_weight)


def detime_volume_confirmed_trend_weights(
    prices: pd.DataFrame,
    ohlcv_features: pd.DataFrame,
    *,
    min_price_trend_slope: float = 0.0,
    min_volume_trend_slope: float = 0.0,
    min_volume_residual_z: float = -1.0,
    max_abs_price_residual_z: float = 2.5,
) -> pd.DataFrame:
    """Single-asset long/flat trend following with volume decomposition confirmation."""

    idx = prices.index
    cols = prices.columns
    if len(cols) != 1:
        raise ValueError("detime_volume_confirmed_trend_weights expects a one-column price frame.")
    f = ohlcv_features.reindex(idx).ffill()
    entries = pd.DataFrame(False, index=idx, columns=cols)
    exits = pd.DataFrame(False, index=idx, columns=cols)
    asset = cols[0]
    long_ok = (
        (f["price_trend_slope"] > float(min_price_trend_slope))
        & (f["volume_trend_slope"] >= float(min_volume_trend_slope))
        & (f["volume_residual_z"] >= float(min_volume_residual_z))
        & (f["price_residual_abs_z"] < float(max_abs_price_residual_z))
    )
    exit_rule = (
        (f["price_trend_slope"] <= float(min_price_trend_slope))
        | (f["price_residual_abs_z"] >= float(max_abs_price_residual_z))
        | (f["volume_residual_z"] < float(min_volume_residual_z))
    )
    entries[asset] = long_ok.fillna(False)
    exits[asset] = exit_rule.fillna(False)
    return signals_to_weights(entries, exits, equal_weight=True)


def decomposition_strategy_score(prices: pd.DataFrame, features: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """A transparent score used in tutorial tables, not a trading claim."""

    trend = _align(features["trend_slope"], prices)
    trend_strength = _align(features.get("trend_strength", pd.DataFrame(0.0, index=prices.index, columns=prices.columns)), prices)
    cycle_slope = _align(features.get("cycle_slope", features.get("season_slope")), prices)
    residual_z = _align(features["residual_z"], prices)
    residual_stress = _align(features["residual_abs_z"], prices)
    return (
        trend.rank(axis=1, pct=True)
        + trend_strength.rank(axis=1, pct=True)
        + cycle_slope.rank(axis=1, pct=True)
        - residual_z.rank(axis=1, pct=True)
        - 0.5 * residual_stress.rank(axis=1, pct=True)
    )


def run_trend_strategy_benchmark(
    prices: pd.DataFrame,
    features: dict[str, pd.DataFrame],
    *,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    """Run the baseline-vs-DeTime strategy set used in article 02."""

    weights = {
        "buy_and_hold": buy_and_hold_weights(prices),
        "classic_dual_ma": classic_dual_ma_weights(prices),
        "classic_macd": classic_macd_weights(prices),
        "detime_trend_gate": detime_trend_gate_weights(prices, features),
        "detime_dual_ma": detime_dual_ma_weights(prices, features),
        "detime_macd": detime_macd_weights(prices, features),
    }
    return {
        name: backtest_weights(prices, w, fee_bps=fee_bps, slippage_bps=slippage_bps)
        for name, w in weights.items()
    }


def strategy_result_table(results: dict[str, BacktestResult]) -> pd.DataFrame:
    """Turn a dict of BacktestResult objects into a ranked statistics table."""

    rows = []
    for name, result in results.items():
        row = dict(result.stats)
        row["strategy"] = name
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    table = pd.DataFrame(rows).set_index("strategy")
    order = ["cagr", "sharpe", "max_drawdown", "calmar", "average_turnover", "total_return", "volatility", "hit_rate"]
    return table[[c for c in order if c in table.columns]].sort_values("sharpe", ascending=False)
