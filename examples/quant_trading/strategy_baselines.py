from __future__ import annotations

"""Classical strategy baselines for the decomposition-first quant column."""

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_weights, signals_to_weights
from .classic_indicators import (
    average_price_oscillator,
    bollinger_mean_reversion_signals,
    donchian_breakout_signals,
    dual_ma_signals,
    macd_signals,
    momentum_signals,
    multi_ma_alignment_state,
    rsi_mean_reversion_signals,
    zscore_mean_reversion_signals,
)


def _equal_weight_from_state(state: pd.DataFrame, *, max_gross: float = 1.0) -> pd.DataFrame:
    pos = state.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    gross = pos.abs().sum(axis=1).replace(0.0, np.nan)
    return pos.div(gross, axis=0).fillna(0.0) * float(max_gross)


def buy_and_hold_weights(prices: pd.DataFrame, *, max_gross: float = 1.0) -> pd.DataFrame:
    w = pd.DataFrame(1.0, index=prices.index, columns=prices.columns)
    return w.div(w.sum(axis=1), axis=0).fillna(0.0) * float(max_gross)


def dual_moving_average_weights(prices: pd.DataFrame, *, fast: int = 20, slow: int = 100, max_gross: float = 1.0) -> pd.DataFrame:
    entries, exits = dual_ma_signals(prices, fast=fast, slow=slow)
    return signals_to_weights(entries, exits, equal_weight=True) * float(max_gross)


def macd_weights(prices: pd.DataFrame, *, fast: int = 12, slow: int = 26, signal: int = 9, max_gross: float = 1.0) -> pd.DataFrame:
    entries, exits = macd_signals(prices, fast=fast, slow=slow, signal=signal)
    return signals_to_weights(entries, exits, equal_weight=True) * float(max_gross)


def multi_ma_alignment_weights(prices: pd.DataFrame, *, windows: tuple[int, ...] = (20, 50, 100), max_gross: float = 1.0) -> pd.DataFrame:
    return _equal_weight_from_state(multi_ma_alignment_state(prices, windows=windows), max_gross=max_gross)


def naive_momentum_weights(prices: pd.DataFrame, *, lookback: int = 63, max_gross: float = 1.0) -> pd.DataFrame:
    entries, exits = momentum_signals(prices, lookback=lookback)
    return signals_to_weights(entries, exits, equal_weight=True) * float(max_gross)


# ---------------------------------------------------------------------------
# Column 03: classical mean-reversion baselines
# ---------------------------------------------------------------------------

def zscore_mean_reversion_weights(
    prices: pd.DataFrame,
    *,
    window: int = 63,
    entry_z: float = 1.5,
    exit_z: float = 0.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = zscore_mean_reversion_signals(prices, window=window, entry_z=entry_z, exit_z=exit_z, allow_short=allow_short)
    return signals_to_weights(le, lx, short_entries=se, short_exits=sx, equal_weight=True) * float(max_gross)


def price_zscore_mean_reversion_weights(
    prices: pd.DataFrame,
    *,
    window: int = 63,
    entry_z: float = -1.5,
    exit_z: float = 0.0,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Legacy-compatible wrapper: negative ``entry_z`` means buy low."""

    return zscore_mean_reversion_weights(prices, window=window, entry_z=abs(float(entry_z)), exit_z=abs(float(exit_z)), allow_short=allow_short, max_gross=max_gross)


def bollinger_mean_reversion_weights(
    prices: pd.DataFrame,
    *,
    window: int = 20,
    entry_z: float = 2.0,
    num_std: float | None = None,
    exit_z: float = 0.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    threshold = float(entry_z if num_std is None else num_std)
    le, lx, se, sx = bollinger_mean_reversion_signals(prices, window=window, entry_z=threshold, exit_z=exit_z, allow_short=allow_short)
    return signals_to_weights(le, lx, short_entries=se, short_exits=sx, equal_weight=True) * float(max_gross)


def rsi_mean_reversion_weights(
    prices: pd.DataFrame,
    *,
    window: int = 14,
    lower: float = 30.0,
    upper: float = 70.0,
    exit_level: float = 50.0,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = rsi_mean_reversion_signals(prices, window=window, lower=lower, upper=upper, exit_level=exit_level, allow_short=allow_short)
    return signals_to_weights(le, lx, short_entries=se, short_exits=sx, equal_weight=True) * float(max_gross)


def apo_mean_reversion_weights(
    prices: pd.DataFrame,
    *,
    fast: int = 10,
    slow: int = 40,
    entry: float | None = None,
    allow_short: bool = True,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Average-price-oscillator reversion baseline from raw prices."""

    apo = average_price_oscillator(prices, fast=fast, slow=slow)
    sd = apo.rolling(max(int(slow), 20), min_periods=max(10, int(slow) // 2)).std(ddof=0)
    threshold = sd if entry is None else float(entry)
    long_entries = (apo < -threshold).fillna(False)
    long_exits = (apo >= 0.0).fillna(False)
    if allow_short:
        short_entries = (apo > threshold).fillna(False)
        short_exits = (apo <= 0.0).fillna(False)
    else:
        short_entries = short_exits = None
    return signals_to_weights(long_entries, long_exits, short_entries=short_entries, short_exits=short_exits, equal_weight=True) * float(max_gross)


def make_classic_mean_reversion_weight_grid(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Column 03 classical baselines: raw z-score, Bollinger, RSI, APO."""

    return {
        "classic_price_zscore_63_1p5": zscore_mean_reversion_weights(prices, window=63, entry_z=1.5, allow_short=True),
        "classic_bollinger_20_2p0": bollinger_mean_reversion_weights(prices, window=20, entry_z=2.0, allow_short=True),
        "classic_rsi_14_30_70": rsi_mean_reversion_weights(prices, window=14, lower=30.0, upper=70.0, allow_short=True),
        "classic_apo_10_40": apo_mean_reversion_weights(prices, fast=10, slow=40, allow_short=True),
        "classic_long_only_bollinger_20_2p0": bollinger_mean_reversion_weights(prices, window=20, entry_z=2.0, allow_short=False),
    }


# ---------------------------------------------------------------------------
# Column 04: classical breakout baselines
# ---------------------------------------------------------------------------

def donchian_breakout_weights(
    prices: pd.DataFrame,
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
    entry_window: int = 55,
    exit_window: int = 20,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    le, lx, se, sx = donchian_breakout_signals(prices, high=high, low=low, entry_window=entry_window, exit_window=exit_window, allow_short=allow_short)
    return signals_to_weights(le, lx, short_entries=se, short_exits=sx, equal_weight=True) * float(max_gross)


def turtle_breakout_weights(
    prices: pd.DataFrame,
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
    allow_short: bool = False,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """Classic Turtle-style 55/20 Donchian breakout baseline."""

    return donchian_breakout_weights(prices, high=high, low=low, entry_window=55, exit_window=20, allow_short=allow_short, max_gross=max_gross)


def make_classic_breakout_weight_grid(
    prices: pd.DataFrame,
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    """Column 04 classical Donchian/Turtle breakout baselines."""

    return {
        "classic_donchian_20_10": donchian_breakout_weights(prices, high=high, low=low, entry_window=20, exit_window=10, allow_short=False),
        "classic_turtle_55_20": turtle_breakout_weights(prices, high=high, low=low, allow_short=False),
        "classic_turtle_55_20_long_short": turtle_breakout_weights(prices, high=high, low=low, allow_short=True),
    }


# ---------------------------------------------------------------------------
# Suites and reports
# ---------------------------------------------------------------------------

def make_classic_baseline_weight_grid(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "buy_hold": buy_and_hold_weights(prices),
        "classic_sma_20_100": dual_moving_average_weights(prices, fast=20, slow=100),
        "classic_sma_50_120": dual_moving_average_weights(prices, fast=50, slow=120),
        "classic_macd_12_26_9": macd_weights(prices, fast=12, slow=26, signal=9),
        "classic_multi_ma_20_50_100": multi_ma_alignment_weights(prices, windows=(20, 50, 100)),
        "classic_momentum_63": naive_momentum_weights(prices, lookback=63),
    }


baseline_weight_suite = make_classic_baseline_weight_grid
classic_mean_reversion_weight_suite = make_classic_mean_reversion_weight_grid
classic_breakout_weight_suite = make_classic_breakout_weight_grid


def run_classical_baselines(prices: pd.DataFrame, *, fee_bps: float = 5.0, slippage_bps: float = 2.0) -> dict[str, BacktestResult]:
    return {name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, weights in make_classic_baseline_weight_grid(prices).items()}


def run_classical_mean_reversion_baselines(prices: pd.DataFrame, *, fee_bps: float = 5.0, slippage_bps: float = 2.0) -> dict[str, BacktestResult]:
    return {name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, weights in make_classic_mean_reversion_weight_grid(prices).items()}


def run_classical_breakout_baselines(
    prices: pd.DataFrame,
    *,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    return {
        name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps)
        for name, weights in make_classic_breakout_weight_grid(prices, high=high, low=low).items()
    }


def stats_table(results: dict[str, BacktestResult]) -> pd.DataFrame:
    rows = []
    for name, result in results.items():
        row = dict(result.stats)
        row["strategy"] = name
        rows.append(row)
    return pd.DataFrame(rows).set_index("strategy") if rows else pd.DataFrame()


def classical_strategy_weights(prices: pd.DataFrame, *, strategy: str, **kwargs) -> pd.DataFrame:
    """Name-based dispatcher kept for notebook readability."""

    key = strategy.lower().replace("-", "_")
    if key in {"buy_hold", "buy_and_hold", "bh"}:
        return buy_and_hold_weights(prices, **kwargs)
    if key in {"double_ma", "dual_ma", "sma_cross", "sma_crossover"}:
        return dual_moving_average_weights(prices, fast=kwargs.get("fast", kwargs.get("short_window", 20)), slow=kwargs.get("slow", kwargs.get("long_window", 100)))
    if key == "macd":
        return macd_weights(prices, fast=kwargs.get("fast", 12), slow=kwargs.get("slow", 26), signal=kwargs.get("signal", kwargs.get("signal_span", 9)))
    if key in {"multi_ma", "ma_stack"}:
        return multi_ma_alignment_weights(prices, windows=kwargs.get("windows", (20, 50, 100)))
    if key == "momentum":
        return naive_momentum_weights(prices, lookback=kwargs.get("lookback", kwargs.get("momentum_lookback", 63)))
    if key in {"price_z", "price_zscore", "zscore_mean_reversion"}:
        return zscore_mean_reversion_weights(prices, window=kwargs.get("window", 63), entry_z=abs(kwargs.get("entry_z", 1.5)), exit_z=abs(kwargs.get("exit_z", 0.0)), allow_short=kwargs.get("allow_short", True))
    if key in {"bollinger", "bbands", "bollinger_mean_reversion"}:
        return bollinger_mean_reversion_weights(prices, window=kwargs.get("window", 20), entry_z=kwargs.get("entry_z", kwargs.get("num_std", 2.0)), allow_short=kwargs.get("allow_short", True))
    if key in {"rsi", "rsi_mean_reversion"}:
        return rsi_mean_reversion_weights(prices, window=kwargs.get("window", 14), lower=kwargs.get("lower", 30.0), upper=kwargs.get("upper", 70.0), exit_level=kwargs.get("exit_level", 50.0), allow_short=kwargs.get("allow_short", True))
    if key in {"donchian", "turtle", "breakout"}:
        return donchian_breakout_weights(prices, high=kwargs.get("high"), low=kwargs.get("low"), entry_window=kwargs.get("entry_window", 55), exit_window=kwargs.get("exit_window", 20), allow_short=kwargs.get("allow_short", False))
    raise ValueError(f"Unknown classical strategy: {strategy}")
