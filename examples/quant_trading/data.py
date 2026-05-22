from __future__ import annotations

"""Real-market data loaders for the De-Time quant trading tutorial column.

The column deliberately does not generate artificial price series. When market
or network data is unavailable, these functions raise an explicit error instead
of silently fabricating prices.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


US_LARGE_CAP = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "JPM", "XOM", "UNH",
    "AVGO", "LLY", "V", "MA", "COST", "NFLX", "AMD", "BAC", "WMT", "HD",
]

US_STYLE_ETFS = ["SPY", "QQQ", "IWM", "DIA", "MTUM", "QUAL", "VLUE", "USMV", "IVE", "IVW"]

US_SECTOR_ETFS = ["XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC"]

KOREA_LARGE_CAP = [
    "005930.KS",  # Samsung Electronics
    "000660.KS",  # SK Hynix
    "035420.KS",  # NAVER
    "035720.KS",  # Kakao
    "051910.KS",  # LG Chem
    "005380.KS",  # Hyundai Motor
    "000270.KS",  # Kia
    "068270.KS",  # Celltrion
    "005490.KS",  # POSCO Holdings
    "105560.KS",  # KB Financial
    "012450.KS",  # Hanwha Aerospace
    "373220.KS",  # LG Energy Solution
]

KOSDAQ_EXAMPLES = ["247540.KQ", "035900.KQ", "263750.KQ", "196170.KQ", "086520.KQ"]

CRYPTO_LARGE_CAP = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD"]

DEFAULT_UNIVERSES: dict[str, list[str]] = {
    "us_large_cap": US_LARGE_CAP,
    "us_style_etfs": US_STYLE_ETFS,
    "us_sector_etfs": US_SECTOR_ETFS,
    "korea_large_cap": KOREA_LARGE_CAP,
    "kosdaq_examples": KOSDAQ_EXAMPLES,
    "crypto_large_cap": CRYPTO_LARGE_CAP,
}


class MarketDataError(RuntimeError):
    """Raised when real market data cannot be fetched or validated."""


@dataclass(frozen=True)
class DownloadSpec:
    tickers: tuple[str, ...]
    start: str = "2018-01-01"
    end: str | None = None
    interval: str = "1d"
    auto_adjust: bool = True
    min_observations: int = 120


def resolve_universe(universe: str | Sequence[str]) -> list[str]:
    """Return a ticker list from a named universe or an explicit sequence."""

    if isinstance(universe, str):
        try:
            return list(DEFAULT_UNIVERSES[universe])
        except KeyError as exc:
            choices = ", ".join(sorted(DEFAULT_UNIVERSES))
            raise KeyError(f"Unknown universe {universe!r}. Available universes: {choices}") from exc
    return [str(t) for t in universe]


def _cache_path(cache_dir: str | Path, spec: DownloadSpec, field: str) -> Path:
    safe = "__".join(t.replace("/", "_") for t in spec.tickers)
    end = spec.end or "latest"
    name = f"yfinance_{field}_{safe}_{spec.start}_{end}_{spec.interval}.csv"
    return Path(cache_dir) / name.replace(":", "-")


def _extract_field(raw: pd.DataFrame, tickers: Sequence[str], field: str) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        levels = [list(raw.columns.get_level_values(i)) for i in range(raw.columns.nlevels)]
        if field in levels[0]:
            out = raw[field]
        elif field in levels[-1]:
            out = raw.xs(field, axis=1, level=raw.columns.nlevels - 1)
        elif field == "Close" and "Adj Close" in levels[0]:
            out = raw["Adj Close"]
        elif field == "Close" and "Adj Close" in levels[-1]:
            out = raw.xs("Adj Close", axis=1, level=raw.columns.nlevels - 1)
        else:
            raise MarketDataError(f"Could not locate {field!r} in yfinance output columns.")
    else:
        chosen = field if field in raw.columns else "Adj Close" if field == "Close" and "Adj Close" in raw.columns else None
        if chosen is None:
            raise MarketDataError(f"Could not locate {field!r} in yfinance output columns.")
        out = raw[[chosen]].copy()
        out.columns = [tickers[0] if tickers else "asset"]

    if isinstance(out, pd.Series):
        out = out.to_frame(tickers[0] if tickers else "asset")

    out = out.apply(pd.to_numeric, errors="coerce")
    out = out.sort_index().replace([np.inf, -np.inf], np.nan).dropna(how="all")
    return out.ffill().bfill()


def _validate_frame(frame: pd.DataFrame, spec: DownloadSpec, *, field: str) -> pd.DataFrame:
    if frame.empty:
        raise MarketDataError(
            f"No real market data returned for {list(spec.tickers)}. Check ticker symbols, date range, network access, or vendor availability."
        )
    keep = [t for t in spec.tickers if t in frame.columns]
    if not keep:
        raise MarketDataError(f"No requested tickers were present after extracting {field!r}.")
    frame = frame[keep].dropna(how="all").ffill().bfill()
    if len(frame) < int(spec.min_observations):
        raise MarketDataError(
            f"Only {len(frame)} observations returned; require at least {spec.min_observations}. "
            "Use a longer date range or verify the data vendor response."
        )
    if frame.isna().all().any():
        empty = list(frame.columns[frame.isna().all()])
        raise MarketDataError(f"These tickers have no usable {field} data: {empty}")
    return frame


def fetch_yahoo_prices(
    tickers: Sequence[str] | str,
    *,
    start: str = "2018-01-01",
    end: str | None = None,
    interval: str = "1d",
    field: str = "Close",
    auto_adjust: bool = True,
    min_observations: int = 120,
    cache_dir: str | Path | None = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Download real close prices from Yahoo Finance through `yfinance`.

    No fallback price generator is provided. If the vendor request fails or the
    returned data fails validation, a `MarketDataError` is raised.
    """

    resolved = resolve_universe(tickers) if isinstance(tickers, str) else [str(t) for t in tickers]
    spec = DownloadSpec(tuple(resolved), start=start, end=end, interval=interval, auto_adjust=auto_adjust, min_observations=min_observations)
    if cache_dir is not None:
        path = _cache_path(cache_dir, spec, field)
        if use_cache and path.exists():
            cached = pd.read_csv(path, index_col=0, parse_dates=True)
            return _validate_frame(cached, spec, field=field)

    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("Install yfinance to run the real-market-data notebooks: python -m pip install yfinance") from exc

    try:
        raw = yf.download(
            tickers=list(spec.tickers),
            start=spec.start,
            end=spec.end,
            interval=spec.interval,
            auto_adjust=spec.auto_adjust,
            progress=False,
            threads=True,
            group_by="column",
        )
    except Exception as exc:  # pragma: no cover - depends on network/vendor
        raise MarketDataError(f"yfinance download failed for {list(spec.tickers)}: {exc}") from exc

    frame = _validate_frame(_extract_field(raw, spec.tickers, field), spec, field=field)
    if cache_dir is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path)
    return frame


def fetch_yahoo_ohlcv(
    ticker: str,
    *,
    start: str = "2018-01-01",
    end: str | None = None,
    interval: str = "1d",
    auto_adjust: bool = True,
    min_observations: int = 120,
    cache_dir: str | Path | None = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Download real OHLCV bars for one ticker from Yahoo Finance."""

    spec = DownloadSpec((str(ticker),), start=start, end=end, interval=interval, auto_adjust=auto_adjust, min_observations=min_observations)
    if cache_dir is not None:
        path = _cache_path(cache_dir, spec, "ohlcv")
        if use_cache and path.exists():
            cached = pd.read_csv(path, index_col=0, parse_dates=True)
            required = ["Open", "High", "Low", "Close", "Volume"]
            if set(required).issubset(cached.columns) and len(cached) >= min_observations:
                return cached[required]

    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("Install yfinance to download OHLCV data: python -m pip install yfinance") from exc

    try:
        raw = yf.download(
            tickers=str(ticker),
            start=spec.start,
            end=spec.end,
            interval=spec.interval,
            auto_adjust=spec.auto_adjust,
            progress=False,
            threads=False,
            group_by="column",
        )
    except Exception as exc:  # pragma: no cover
        raise MarketDataError(f"yfinance OHLCV download failed for {ticker}: {exc}") from exc

    if raw is None or raw.empty:
        raise MarketDataError(f"No OHLCV data returned for {ticker}.")
    if isinstance(raw.columns, pd.MultiIndex):
        if ticker in raw.columns.get_level_values(-1):
            raw = raw.xs(ticker, axis=1, level=-1)
        elif ticker in raw.columns.get_level_values(0):
            raw = raw[ticker]
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise MarketDataError(f"Missing OHLCV fields for {ticker}: {missing}")
    out = raw[required].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna(how="all")
    out = out.ffill().bfill()
    if len(out) < min_observations:
        raise MarketDataError(f"Only {len(out)} OHLCV bars returned for {ticker}; require {min_observations}.")
    if cache_dir is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(path)
    return out


def data_audit_report(prices: pd.DataFrame) -> pd.DataFrame:
    """Return a compact per-asset audit table for a real-price panel."""

    if prices.empty:
        raise MarketDataError("Cannot audit an empty price frame.")
    records: list[dict[str, object]] = []
    for col in prices.columns:
        s = prices[col]
        valid = s.dropna()
        records.append(
            {
                "ticker": col,
                "first_timestamp": valid.index.min() if not valid.empty else pd.NaT,
                "last_timestamp": valid.index.max() if not valid.empty else pd.NaT,
                "observations": int(valid.shape[0]),
                "missing_ratio": float(s.isna().mean()),
                "min_price": float(valid.min()) if not valid.empty else np.nan,
                "max_price": float(valid.max()) if not valid.empty else np.nan,
            }
        )
    return pd.DataFrame.from_records(records)


def prices_to_returns(prices: pd.DataFrame, *, log: bool = False) -> pd.DataFrame:
    clean = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    if log:
        return np.log(clean).diff().replace([np.inf, -np.inf], np.nan).dropna(how="all")
    return clean.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="all")
