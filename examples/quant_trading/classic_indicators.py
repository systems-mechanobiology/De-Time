from __future__ import annotations

"""Classical technical indicators used as transparent baselines."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

FrameLike = pd.Series | pd.DataFrame


def _clean(x: FrameLike) -> FrameLike:
    return x.astype(float).replace([np.inf, -np.inf], np.nan)


def sma(x: FrameLike, window: int = 20, *, min_periods: int | None = None) -> FrameLike:
    return _clean(x).rolling(int(window), min_periods=min_periods or max(1, int(window) // 2)).mean()


def ema(x: FrameLike, span: int = 20, *, min_periods: int | None = None, adjust: bool = False) -> FrameLike:
    return _clean(x).ewm(span=int(span), min_periods=min_periods or max(1, int(span) // 2), adjust=adjust).mean()


def momentum(x: FrameLike, window: int = 20, *, pct: bool = False, log: bool = False) -> FrameLike:
    clean = _clean(x)
    if pct:
        return clean.pct_change(int(window))
    if log:
        return np.log(clean.clip(lower=1e-12)).diff(int(window))
    return clean.diff(int(window))


def average_price_oscillator(x: FrameLike, fast: int = 10, slow: int = 40) -> FrameLike:
    return ema(x, fast) - ema(x, slow)


def macd(x: FrameLike, *, fast: int = 12, slow: int = 26, signal: int = 9) -> dict[str, FrameLike]:
    line = ema(x, fast) - ema(x, slow)
    sig = ema(line, signal)
    hist = line - sig
    return {"macd": line, "signal": sig, "histogram": hist}


def rsi(x: FrameLike, window: int = 14) -> FrameLike:
    clean = _clean(x)
    delta = clean.diff()
    gain = delta.clip(lower=0.0).ewm(alpha=1 / int(window), min_periods=int(window), adjust=False).mean()
    loss = (-delta.clip(upper=0.0)).ewm(alpha=1 / int(window), min_periods=int(window), adjust=False).mean()
    rs = gain / (loss + 1e-12)
    return 100.0 - 100.0 / (1.0 + rs)


def rolling_zscore(x: FrameLike, window: int = 63, *, min_periods: int | None = None) -> FrameLike:
    """Rolling z-score used by classical mean-reversion baselines."""

    clean = _clean(x)
    w = int(window)
    mp = min_periods or max(10, w // 3)
    mu = clean.rolling(w, min_periods=mp).mean()
    sd = clean.rolling(w, min_periods=mp).std(ddof=0)
    return (clean - mu) / (sd + 1e-12)


def log_price_zscore(prices: pd.DataFrame, window: int = 63) -> pd.DataFrame:
    clean = _clean(prices).astype(float).clip(lower=1e-12)
    return rolling_zscore(np.log(clean), window=window)


@dataclass(frozen=True)
class BollingerBands:
    middle: FrameLike
    upper: FrameLike
    lower: FrameLike
    zscore: FrameLike
    width: FrameLike


def bollinger_bands(x: FrameLike, window: int = 20, num_std: float = 2.0) -> BollingerBands:
    clean = _clean(x)
    middle = sma(clean, window)
    sd = clean.rolling(int(window), min_periods=max(5, int(window) // 2)).std(ddof=0)
    upper = middle + float(num_std) * sd
    lower = middle - float(num_std) * sd
    z = (clean - middle) / (sd + 1e-12)
    width = (upper - lower) / (middle.abs() + 1e-12)
    return BollingerBands(middle=middle, upper=upper, lower=lower, zscore=z, width=width)


# ---------------------------------------------------------------------------
# Mean-reversion signal helpers
# ---------------------------------------------------------------------------

def rsi_reversion_signals(
    prices: pd.DataFrame,
    *,
    window: int = 14,
    lower: float = 30.0,
    upper: float = 70.0,
    exit_level: float = 50.0,
    allow_short: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    r = rsi(prices, window=window)
    long_entries = (r < float(lower)).fillna(False)
    long_exits = (r > float(exit_level)).fillna(False)
    if not allow_short:
        return long_entries, long_exits, None, None
    short_entries = (r > float(upper)).fillna(False)
    short_exits = (r < float(exit_level)).fillna(False)
    return long_entries, long_exits, short_entries, short_exits


def bollinger_reversion_signals(
    prices: pd.DataFrame,
    *,
    window: int = 20,
    entry_z: float = 2.0,
    exit_z: float = 0.0,
    allow_short: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    z = bollinger_bands(prices, window=window, num_std=float(entry_z)).zscore
    long_entries = (z < -float(entry_z)).fillna(False)
    long_exits = (z > -float(exit_z)).fillna(False)
    if not allow_short:
        return long_entries, long_exits, None, None
    short_entries = (z > float(entry_z)).fillna(False)
    short_exits = (z < float(exit_z)).fillna(False)
    return long_entries, long_exits, short_entries, short_exits


def price_zscore_reversion_signals(
    prices: pd.DataFrame,
    *,
    window: int = 63,
    entry_z: float = 1.5,
    exit_z: float = 0.0,
    allow_short: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    z = log_price_zscore(prices, window=window)
    long_entries = (z < -float(entry_z)).fillna(False)
    long_exits = (z > -float(exit_z)).fillna(False)
    if not allow_short:
        return long_entries, long_exits, None, None
    short_entries = (z > float(entry_z)).fillna(False)
    short_exits = (z < float(exit_z)).fillna(False)
    return long_entries, long_exits, short_entries, short_exits


def apo_reversion_signals(
    prices: pd.DataFrame,
    *,
    fast: int = 10,
    slow: int = 40,
    z_window: int = 63,
    entry_z: float = 1.5,
    exit_z: float = 0.0,
    allow_short: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    z = rolling_zscore(average_price_oscillator(prices, fast=fast, slow=slow), window=z_window)
    long_entries = (z < -float(entry_z)).fillna(False)
    long_exits = (z > -float(exit_z)).fillna(False)
    if not allow_short:
        return long_entries, long_exits, None, None
    short_entries = (z > float(entry_z)).fillna(False)
    short_exits = (z < float(exit_z)).fillna(False)
    return long_entries, long_exits, short_entries, short_exits


# Backward-readable aliases used by notebooks and strategy modules.
zscore_mean_reversion_signals = price_zscore_reversion_signals
bollinger_mean_reversion_signals = bollinger_reversion_signals
rsi_mean_reversion_signals = rsi_reversion_signals


# ---------------------------------------------------------------------------
# Breakout / Turtle helpers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DonchianChannels:
    upper: FrameLike
    lower: FrameLike
    middle: FrameLike
    width: FrameLike
    upper_entry: FrameLike
    lower_entry: FrameLike
    upper_exit: FrameLike
    lower_exit: FrameLike


def _one_donchian(high: FrameLike, low: FrameLike | None, *, window: int, shift: int = 1) -> tuple[FrameLike, FrameLike, FrameLike, FrameLike]:
    h = _clean(high)
    l = _clean(low if low is not None else high)
    upper = h.rolling(int(window), min_periods=max(5, int(window) // 2)).max().shift(int(shift))
    lower = l.rolling(int(window), min_periods=max(5, int(window) // 2)).min().shift(int(shift))
    middle = (upper + lower) / 2.0
    width = (upper - lower) / (middle.abs() + 1e-12)
    return upper, lower, middle, width


def donchian_channels(
    high: FrameLike,
    low: FrameLike | None = None,
    *,
    window: int | None = None,
    shift: int = 1,
    entry_window: int | None = None,
    exit_window: int | None = None,
) -> DonchianChannels:
    """Prior-bar Donchian channels.

    Supports both a single-window call (`window=20`) and a Turtle-style
    entry/exit call (`entry_window=55, exit_window=20`).
    """

    if entry_window is not None or exit_window is not None:
        ew = int(entry_window or window or 55)
        xw = int(exit_window or window or 20)
        upper_entry, lower_entry, middle, width = _one_donchian(high, low, window=ew, shift=shift)
        upper_exit, lower_exit, _, _ = _one_donchian(high, low, window=xw, shift=shift)
        return DonchianChannels(
            upper=upper_entry,
            lower=lower_entry,
            middle=middle,
            width=width,
            upper_entry=upper_entry,
            lower_entry=lower_entry,
            upper_exit=upper_exit,
            lower_exit=lower_exit,
        )
    w = int(window or 20)
    upper, lower, middle, width = _one_donchian(high, low, window=w, shift=shift)
    return DonchianChannels(upper=upper, lower=lower, middle=middle, width=width, upper_entry=upper, lower_entry=lower, upper_exit=upper, lower_exit=lower)


donchian_channel = donchian_channels


def true_range(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame) -> pd.DataFrame:
    h = _clean(high).astype(float).sort_index().ffill().bfill()
    l = _clean(low).astype(float).reindex_like(h).ffill().bfill()
    c = _clean(close).astype(float).reindex_like(h).ffill().bfill()
    prev_close = c.shift(1)
    arr = np.maximum.reduce([(h - l).abs().to_numpy(), (h - prev_close).abs().to_numpy(), (l - prev_close).abs().to_numpy()])
    return pd.DataFrame(arr, index=h.index, columns=h.columns)


def atr(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    return true_range(high, low, close).ewm(alpha=1 / int(window), min_periods=max(5, int(window) // 2), adjust=False).mean()


average_true_range = atr


def donchian_breakout_signals(
    close: pd.DataFrame,
    high: pd.DataFrame | None = None,
    low: pd.DataFrame | None = None,
    *,
    entry_window: int = 55,
    exit_window: int = 20,
    allow_short: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    c = _clean(close).sort_index().ffill().bfill()
    h = _clean(high).reindex_like(c).ffill().bfill() if high is not None else c
    l = _clean(low).reindex_like(c).ffill().bfill() if low is not None else c
    ch = donchian_channels(h, l, entry_window=entry_window, exit_window=exit_window)
    long_entries = (c > ch.upper_entry).fillna(False)
    long_exits = (c < ch.lower_exit).fillna(False)
    if not allow_short:
        return long_entries, long_exits, None, None
    short_entries = (c < ch.lower_entry).fillna(False)
    short_exits = (c > ch.upper_exit).fillna(False)
    return long_entries, long_exits, short_entries, short_exits


# ---------------------------------------------------------------------------
# Indicator tables and trend baselines
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IndicatorSpec:
    fast: int = 20
    medium: int = 50
    slow: int = 100
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    momentum_window: int = 63
    rsi_window: int = 14


def moving_average_crossover_state(prices: pd.DataFrame, fast: int = 20, slow: int = 100) -> pd.DataFrame:
    return (sma(prices, fast) > sma(prices, slow)).fillna(False)


def dual_ma_signals(prices: pd.DataFrame, *, fast: int = 20, slow: int = 100) -> tuple[pd.DataFrame, pd.DataFrame]:
    fast_ma, slow_ma = sma(prices, fast), sma(prices, slow)
    return (fast_ma > slow_ma).fillna(False), (fast_ma < slow_ma).fillna(False)


def macd_state(prices: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    parts = macd(prices, fast=fast, slow=slow, signal=signal)
    return (parts["macd"] > parts["signal"]).fillna(False)


def macd_signals(prices: pd.DataFrame, *, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts = macd(prices, fast=fast, slow=slow, signal=signal)
    entries = (parts["macd"] > parts["signal"]) & (parts["histogram"] > 0)
    exits = (parts["macd"] < parts["signal"]) | (parts["histogram"] < 0)
    return entries.fillna(False), exits.fillna(False)


def momentum_signals(prices: pd.DataFrame, *, lookback: int = 63) -> tuple[pd.DataFrame, pd.DataFrame]:
    mom = prices.pct_change(int(lookback))
    return (mom > 0).fillna(False), (mom <= 0).fillna(False)


def multi_ma_alignment_state(prices: pd.DataFrame, windows: tuple[int, ...] = (20, 50, 100)) -> pd.DataFrame:
    if len(windows) < 2:
        raise ValueError("windows must contain at least two entries")
    avgs = [sma(prices, w) for w in windows]
    state = pd.DataFrame(True, index=prices.index, columns=prices.columns)
    for left, right in zip(avgs[:-1], avgs[1:]):
        state &= left > right
    return state.fillna(False)


def multi_ma_alignment_score(prices: pd.DataFrame, windows: tuple[int, ...] = (20, 50, 100)) -> pd.DataFrame:
    avgs = [sma(prices, w) for w in windows]
    score = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for left, right in zip(avgs[:-1], avgs[1:]):
        score += (left > right).astype(float)
    return score / max(len(avgs) - 1, 1)


moving_average_stack_score = multi_ma_alignment_score


def build_indicator_table(prices: pd.DataFrame, spec: IndicatorSpec | None = None) -> pd.DataFrame:
    spec = spec or IndicatorSpec()
    clean = _clean(prices).astype(float).sort_index().ffill().bfill()
    m = macd(clean, fast=spec.macd_fast, slow=spec.macd_slow, signal=spec.macd_signal)
    b = bollinger_bands(clean)
    blocks: dict[str, pd.DataFrame] = {
        "close": clean,
        f"sma_{spec.fast}": sma(clean, spec.fast),
        f"sma_{spec.medium}": sma(clean, spec.medium),
        f"sma_{spec.slow}": sma(clean, spec.slow),
        f"ema_{spec.fast}": ema(clean, spec.fast),
        f"ema_{spec.slow}": ema(clean, spec.slow),
        "macd": m["macd"],
        "macd_signal": m["signal"],
        "macd_histogram": m["histogram"],
        f"momentum_{spec.momentum_window}": momentum(clean, spec.momentum_window, pct=True),
        f"rsi_{spec.rsi_window}": rsi(clean, spec.rsi_window),
        "bb_zscore": b.zscore,
        "bb_width": b.width,
        "price_zscore_63": log_price_zscore(clean, 63),
        "multi_ma_alignment": multi_ma_alignment_score(clean),
    }
    return pd.concat(blocks, axis=1).sort_index(axis=1)


def indicator_feature_table(prices: pd.DataFrame) -> pd.DataFrame:
    return build_indicator_table(prices)
