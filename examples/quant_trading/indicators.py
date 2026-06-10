from __future__ import annotations

"""Classical technical indicators used as transparent baselines.

These functions intentionally use vectorized pandas rather than copying the
loop-heavy examples from older tutorials. The objective is not to invent new
indicator formulas; it is to provide clean baselines before replacing their
implicit filters with explicit DeTime components.
"""

import numpy as np
import pandas as pd


def _as_frame(x: pd.Series | pd.DataFrame) -> pd.DataFrame:
    if isinstance(x, pd.Series):
        return x.to_frame(x.name or "asset")
    return x.copy()


def sma(prices: pd.Series | pd.DataFrame, window: int = 20) -> pd.Series | pd.DataFrame:
    out = _as_frame(prices).rolling(int(window), min_periods=max(2, int(window) // 3)).mean()
    return out.iloc[:, 0] if isinstance(prices, pd.Series) else out


def ema(prices: pd.Series | pd.DataFrame, span: int = 20) -> pd.Series | pd.DataFrame:
    out = _as_frame(prices).ewm(span=int(span), adjust=False, min_periods=max(2, int(span) // 3)).mean()
    return out.iloc[:, 0] if isinstance(prices, pd.Series) else out


def momentum(prices: pd.Series | pd.DataFrame, window: int = 20, *, log: bool = True) -> pd.Series | pd.DataFrame:
    clean = _as_frame(prices).astype(float)
    if log:
        out = np.log(clean).diff(int(window))
    else:
        out = clean.pct_change(int(window))
    return out.iloc[:, 0] if isinstance(prices, pd.Series) else out


def macd(
    prices: pd.Series | pd.DataFrame,
    *,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    use_log_price: bool = False,
) -> tuple[pd.Series | pd.DataFrame, pd.Series | pd.DataFrame, pd.Series | pd.DataFrame]:
    """Return MACD line, signal line, and histogram."""

    clean = _as_frame(prices).astype(float)
    base = np.log(clean) if use_log_price else clean
    macd_line = ema(base, fast) - ema(base, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    if isinstance(prices, pd.Series):
        return macd_line.iloc[:, 0], signal_line.iloc[:, 0], hist.iloc[:, 0]
    return macd_line, signal_line, hist


def rsi(prices: pd.Series | pd.DataFrame, window: int = 14) -> pd.Series | pd.DataFrame:
    clean = _as_frame(prices).astype(float)
    delta = clean.diff()
    gain = delta.clip(lower=0.0).ewm(alpha=1 / int(window), adjust=False, min_periods=int(window)).mean()
    loss = (-delta.clip(upper=0.0)).ewm(alpha=1 / int(window), adjust=False, min_periods=int(window)).mean()
    rs = gain / (loss + 1e-12)
    out = 100.0 - 100.0 / (1.0 + rs)
    return out.iloc[:, 0] if isinstance(prices, pd.Series) else out


def bollinger_bands(
    prices: pd.Series | pd.DataFrame,
    *,
    window: int = 20,
    num_std: float = 2.0,
) -> tuple[pd.Series | pd.DataFrame, pd.Series | pd.DataFrame, pd.Series | pd.DataFrame]:
    clean = _as_frame(prices).astype(float)
    mid = sma(clean, window)
    sd = clean.rolling(int(window), min_periods=max(2, int(window) // 3)).std(ddof=0)
    upper = mid + float(num_std) * sd
    lower = mid - float(num_std) * sd
    if isinstance(prices, pd.Series):
        return mid.iloc[:, 0], upper.iloc[:, 0], lower.iloc[:, 0]
    return mid, upper, lower


def rolling_volatility(prices: pd.Series | pd.DataFrame, window: int = 20, periods_per_year: int = 252) -> pd.Series | pd.DataFrame:
    ret = _as_frame(prices).pct_change()
    out = ret.rolling(int(window), min_periods=max(2, int(window) // 2)).std(ddof=0) * np.sqrt(int(periods_per_year))
    return out.iloc[:, 0] if isinstance(prices, pd.Series) else out


def dual_moving_average_signal(
    prices: pd.DataFrame,
    *,
    fast: int = 20,
    slow: int = 100,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Classic long/flat dual moving-average signal."""

    clean = _as_frame(prices).sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    fast_ma = sma(clean, fast)
    slow_ma = sma(clean, slow)
    entries = fast_ma > slow_ma
    exits = fast_ma < slow_ma
    return entries.fillna(False), exits.fillna(False)


def macd_signal(
    prices: pd.DataFrame,
    *,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    use_log_price: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Classic long/flat MACD crossover signal."""

    macd_line, signal_line, hist = macd(prices, fast=fast, slow=slow, signal=signal, use_log_price=use_log_price)
    entries = (macd_line > signal_line) & (hist > 0)
    exits = (macd_line < signal_line) | (hist < 0)
    return entries.fillna(False), exits.fillna(False)


def multi_ma_alignment(
    prices: pd.DataFrame,
    *,
    windows: tuple[int, ...] = (20, 50, 100),
) -> pd.DataFrame:
    """Score whether shorter moving averages sit above longer ones."""

    if len(windows) < 2:
        raise ValueError("At least two windows are required.")
    clean = _as_frame(prices).sort_index().ffill().bfill()
    mas = [sma(clean, w) for w in windows]
    score = pd.DataFrame(0.0, index=clean.index, columns=clean.columns)
    for left, right in zip(mas[:-1], mas[1:]):
        score += (left > right).astype(float)
    return score / float(len(mas) - 1)


def classic_indicator_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """Build a compact indicator panel for tutorial tables and diagnostics."""

    clean = _as_frame(prices).astype(float).sort_index().ffill().bfill()
    macd_line, signal_line, hist = macd(clean)
    panel = {
        "sma_20": sma(clean, 20),
        "sma_100": sma(clean, 100),
        "ema_20": ema(clean, 20),
        "mom_20": momentum(clean, 20),
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_hist": hist,
        "rsi_14": rsi(clean, 14),
        "vol_20": rolling_volatility(clean, 20),
        "multi_ma_alignment": multi_ma_alignment(clean),
    }
    return pd.concat(panel, axis=1).sort_index(axis=1)
