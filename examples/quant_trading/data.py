from __future__ import annotations

"""Market data loaders for the decomposition-first quant tutorials.

The code supports Yahoo Finance downloads through ``yfinance`` and a small
archived GOOG/OHLCV sample copied from the public *Learn Algorithmic Trading*
material for offline execution. Serious research should replace these
educational sources with licensed point-in-time market data.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


US_LARGE_CAP = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "JPM", "XOM", "UNH",
    "AVGO", "LLY", "V", "MA", "COST", "NFLX", "AMD", "BAC", "WMT", "HD",
]
US_STYLE_ETFS = ["SPY", "QQQ", "IWM", "DIA", "MTUM", "QUAL", "VLUE", "USMV", "IVE", "IVW"]
US_SECTOR_ETFS = ["XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC"]
KOREA_LARGE_CAP = [
    "005930.KS", "000660.KS", "035420.KS", "035720.KS", "051910.KS", "005380.KS",
    "000270.KS", "068270.KS", "005490.KS", "105560.KS", "012450.KS", "373220.KS",
]
KOSDAQ_EXAMPLES = ["247540.KQ", "035900.KQ", "263750.KQ", "196170.KQ", "086520.KQ"]
CRYPTO_LARGE_CAP = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD"]
FX_EXAMPLES = ["AUDUSD=X", "CADUSD=X", "CHFUSD=X", "EURUSD=X", "GBPUSD=X", "JPYUSD=X", "NZDUSD=X"]
BUNDLED_REAL_SAMPLE = ["GOOG", *FX_EXAMPLES]

DEFAULT_UNIVERSES: dict[str, list[str]] = {
    "us_large_cap": US_LARGE_CAP,
    "us_style_etfs": US_STYLE_ETFS,
    "us_sector_etfs": US_SECTOR_ETFS,
    "korea_large_cap": KOREA_LARGE_CAP,
    "kosdaq_examples": KOSDAQ_EXAMPLES,
    "crypto_large_cap": CRYPTO_LARGE_CAP,
    "fx_examples": FX_EXAMPLES,
    "bundled_real_sample": BUNDLED_REAL_SAMPLE,
}

DATA_DIR = Path(__file__).resolve().parent / "data"
BUNDLED_SAMPLE_DIR = DATA_DIR / "learn_algorithmic_trading"
SAMPLE_GOOGLIKE_SOURCE = "Learn-Algorithmic-Trading GOOG Yahoo Finance export, bundled for offline tutorial smoke tests"


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
    safe = "__".join(t.replace("/", "_").replace(":", "-") for t in spec.tickers)
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


def _validate_price_frame(frame: pd.DataFrame, spec: DownloadSpec, *, field: str) -> pd.DataFrame:
    if frame.empty:
        raise MarketDataError(
            f"No real market data returned for {list(spec.tickers)}. Check ticker symbols, date range, network access, or vendor availability."
        )
    keep = [t for t in spec.tickers if t in frame.columns]
    if not keep:
        raise MarketDataError(f"No requested tickers were present after extracting {field!r}.")
    frame = frame[keep].dropna(how="all").ffill().bfill()
    if len(frame) < int(spec.min_observations):
        raise MarketDataError(f"Only {len(frame)} observations returned; require at least {spec.min_observations}.")
    if frame.isna().all().any():
        empty = list(frame.columns[frame.isna().all()])
        raise MarketDataError(f"These tickers have no usable {field} data: {empty}")
    return frame


def validate_ohlcv(frame: pd.DataFrame, *, ticker: str | None = None, min_observations: int = 120) -> pd.DataFrame:
    """Validate a single OHLCV table."""

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise MarketDataError(f"Missing OHLCV fields for {ticker or 'asset'}: {missing}")
    out = frame[required + (["Adj Close"] if "Adj Close" in frame.columns else [])].apply(pd.to_numeric, errors="coerce")
    out = out.sort_index().replace([np.inf, -np.inf], np.nan).dropna(how="all").ffill().bfill()
    out = out[out["Close"] > 0]
    if len(out) < min_observations:
        raise MarketDataError(f"Only {len(out)} OHLCV bars for {ticker or 'asset'}; require {min_observations}.")
    return out


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
    """Download real price data from Yahoo Finance through ``yfinance``."""

    resolved = resolve_universe(tickers) if isinstance(tickers, str) else [str(t) for t in tickers]
    spec = DownloadSpec(tuple(resolved), start=start, end=end, interval=interval, auto_adjust=auto_adjust, min_observations=min_observations)
    if cache_dir is not None:
        path = _cache_path(cache_dir, spec, field)
        if use_cache and path.exists():
            cached = pd.read_csv(path, index_col=0, parse_dates=True)
            return _validate_price_frame(cached, spec, field=field)
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("Install yfinance to run live market-data notebooks: python -m pip install yfinance") from exc
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
    except Exception as exc:  # pragma: no cover
        raise MarketDataError(f"yfinance download failed for {list(spec.tickers)}: {exc}") from exc
    frame = _validate_price_frame(_extract_field(raw, spec.tickers, field), spec, field=field)
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
            return validate_ohlcv(cached, ticker=ticker, min_observations=min_observations)
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
    out = validate_ohlcv(raw, ticker=ticker, min_observations=min_observations)
    if cache_dir is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(path)
    return out


def fetch_yahoo_ohlcv_panel(
    tickers: Sequence[str] | str,
    *,
    start: str = "2018-01-01",
    end: str | None = None,
    interval: str = "1d",
    auto_adjust: bool = True,
    min_observations: int = 120,
    cache_dir: str | Path | None = None,
    use_cache: bool = True,
    allow_partial: bool = False,
) -> dict[str, pd.DataFrame]:
    """Download OHLCV fields for multiple tickers.

    Returns a dictionary with ``Open``, ``High``, ``Low``, ``Close`` and
    ``Volume`` panels.
    """

    resolved = resolve_universe(tickers) if isinstance(tickers, str) else [str(t) for t in tickers]
    fields: dict[str, list[pd.Series]] = {field: [] for field in ["Open", "High", "Low", "Close", "Volume"]}
    failed: dict[str, str] = {}
    for ticker in resolved:
        try:
            one = fetch_yahoo_ohlcv(
                ticker,
                start=start,
                end=end,
                interval=interval,
                auto_adjust=auto_adjust,
                min_observations=min_observations,
                cache_dir=cache_dir,
                use_cache=use_cache,
            )
        except Exception as exc:
            failed[ticker] = str(exc)
            if allow_partial:
                continue
            raise MarketDataError(f"Failed to fetch {ticker}: {exc}") from exc
        for field in fields:
            fields[field].append(one[field].rename(ticker))
    if not fields["Close"]:
        raise MarketDataError(f"No usable tickers were downloaded. Failures: {failed}")
    panels = {field: pd.concat(series_list, axis=1).sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill() for field, series_list in fields.items() if series_list}
    if failed:
        panels["_failed"] = pd.DataFrame([{"ticker": k, "reason": v} for k, v in failed.items()])
    return panels


def load_bundled_real_ohlcv(ticker: str = "GOOG", *, min_observations: int = 120) -> pd.DataFrame:
    """Load an archived real OHLCV sample shipped for offline tutorial tests."""

    path = BUNDLED_SAMPLE_DIR / f"{ticker}.csv"
    if not path.exists():
        choices = ", ".join(BUNDLED_REAL_SAMPLE)
        raise MarketDataError(f"No bundled real sample for {ticker!r}. Available: {choices}")
    frame = pd.read_csv(path, index_col=0, parse_dates=True)
    out = validate_ohlcv(frame, ticker=ticker, min_observations=min_observations)
    out.attrs["source"] = SAMPLE_GOOGLIKE_SOURCE if ticker == "GOOG" else "Learn-Algorithmic-Trading FX Yahoo Finance export"
    out.attrs["symbol"] = ticker
    return out


def load_sample_goog_ohlcv(*, trim_start: str | None = "2014-01-01", trim_end: str | None = None) -> pd.DataFrame:
    """Load bundled historical GOOG OHLCV data for offline tutorial execution."""

    out = load_bundled_real_ohlcv("GOOG", min_observations=1)
    if trim_start is not None:
        out = out.loc[out.index >= pd.Timestamp(trim_start)]
    if trim_end is not None:
        out = out.loc[out.index <= pd.Timestamp(trim_end)]
    out.attrs["source"] = SAMPLE_GOOGLIKE_SOURCE
    out.attrs["symbol"] = "GOOG"
    return out


def load_bundled_real_price_panel(
    tickers: Sequence[str] | str = ("GOOG",),
    *,
    field: str = "Close",
    min_observations: int = 120,
) -> pd.DataFrame:
    """Load a price panel from bundled archived real data."""

    resolved = resolve_universe(tickers) if isinstance(tickers, str) else [str(t) for t in tickers]
    frames = []
    for ticker in resolved:
        ohlcv = load_bundled_real_ohlcv(ticker, min_observations=min_observations)
        chosen = field if field in ohlcv.columns else "Close"
        frames.append(ohlcv[chosen].rename(ticker))
    out = pd.concat(frames, axis=1).sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    return _validate_price_frame(out, DownloadSpec(tuple(resolved), min_observations=min_observations), field=field)




def load_bundled_real_ohlcv_panel(
    tickers: Sequence[str] | str = ("GOOG",),
    *,
    min_observations: int = 120,
) -> dict[str, pd.DataFrame]:
    """Load a bundled OHLCV field-panel dictionary from archived real data.

    The bundled files are educational Yahoo Finance exports carried over from
    the Learn Algorithmic Trading material.  They are useful for deterministic
    offline smoke tests; live research runs should use ``fetch_yahoo_ohlcv_panel``
    or a licensed point-in-time data source.
    """

    resolved = resolve_universe(tickers) if isinstance(tickers, str) else [str(t) for t in tickers]
    fields: dict[str, list[pd.Series]] = {field: [] for field in ["Open", "High", "Low", "Close", "Volume"]}
    for ticker in resolved:
        ohlcv = load_bundled_real_ohlcv(ticker, min_observations=min_observations)
        for field in fields:
            fields[field].append(ohlcv[field].rename(ticker))
    return {
        field: pd.concat(series_list, axis=1).sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
        for field, series_list in fields.items()
    }

def ohlcv_panel_to_field(panel: Mapping[str, pd.DataFrame], field: str) -> pd.DataFrame:
    """Extract one OHLCV field from either field-panel or ticker-table dictionaries."""

    if field in panel and isinstance(panel[field], pd.DataFrame):
        return panel[field].sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    pieces = []
    for ticker, table in panel.items():
        if str(ticker).startswith("_"):
            continue
        if field not in table.columns:
            raise MarketDataError(f"{ticker} is missing field {field!r}")
        pieces.append(table[field].rename(str(ticker)))
    if not pieces:
        raise MarketDataError("OHLCV panel is empty")
    return pd.concat(pieces, axis=1).sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()


def load_or_download_ohlcv_for_tutorial(
    ticker: str = "SPY",
    *,
    start: str = "2016-01-01",
    end: str | None = None,
    cache_dir: str | Path | None = None,
    allow_sample_fallback: bool = True,
) -> tuple[pd.DataFrame, str]:
    """Download one ticker, or use bundled real data if explicitly allowed."""

    try:
        table = fetch_yahoo_ohlcv(ticker, start=start, end=end, cache_dir=cache_dir)
        table.attrs["source"] = "Yahoo Finance via yfinance live download"
        table.attrs["symbol"] = ticker
        return table, "Yahoo Finance via yfinance live download"
    except Exception as exc:
        if not allow_sample_fallback:
            raise
        sample = load_sample_goog_ohlcv(trim_start="2014-01-01")
        sample.attrs["download_error"] = str(exc)
        return sample, SAMPLE_GOOGLIKE_SOURCE + f"; live download fallback reason: {exc}"


def data_audit_report(prices: pd.DataFrame) -> pd.DataFrame:
    """Return a compact per-asset audit table for a price panel."""

    if prices.empty:
        raise MarketDataError("Cannot audit an empty price frame.")
    rows: list[dict[str, object]] = []
    for col in prices.columns:
        s = prices[col]
        valid = s.dropna()
        rows.append(
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
    return pd.DataFrame(rows)


def ohlcv_audit_report(ohlcv: pd.DataFrame | Mapping[str, pd.DataFrame], *, ticker: str | None = None) -> pd.DataFrame:
    """Audit a single OHLCV table or a field-panel dictionary."""

    if isinstance(ohlcv, Mapping):
        close = ohlcv_panel_to_field(ohlcv, "Close")
        volume = ohlcv_panel_to_field(ohlcv, "Volume") if "Volume" in ohlcv else pd.DataFrame(index=close.index, columns=close.columns)
        rows: list[dict[str, object]] = []
        for col in close.columns:
            c = close[col].dropna()
            v = volume[col].reindex(close.index) if col in volume else pd.Series(index=close.index, dtype=float)
            rows.append(
                {
                    "ticker": col,
                    "first_timestamp": c.index.min() if not c.empty else pd.NaT,
                    "last_timestamp": c.index.max() if not c.empty else pd.NaT,
                    "observations": int(c.shape[0]),
                    "close_missing_ratio": float(close[col].isna().mean()),
                    "volume_missing_ratio": float(v.isna().mean()),
                    "zero_volume_ratio": float((v.fillna(0) == 0).mean()),
                    "min_close": float(c.min()) if not c.empty else np.nan,
                    "max_close": float(c.max()) if not c.empty else np.nan,
                    "median_volume": float(v.median()) if v.notna().any() else np.nan,
                }
            )
        return pd.DataFrame(rows)
    validated = validate_ohlcv(ohlcv, ticker=ticker or "asset", min_observations=1)
    return pd.DataFrame(
        [
            {
                "ticker": ticker or validated.attrs.get("symbol", "asset"),
                "first_timestamp": validated.index.min(),
                "last_timestamp": validated.index.max(),
                "observations": int(len(validated)),
                "close_missing_ratio": float(validated["Close"].isna().mean()),
                "volume_missing_ratio": float(validated["Volume"].isna().mean()),
                "zero_volume_ratio": float((validated["Volume"].fillna(0) == 0).mean()),
                "min_close": float(validated["Close"].min()),
                "max_close": float(validated["Close"].max()),
                "median_volume": float(validated["Volume"].median()),
            }
        ]
    )


def market_data_manifest(
    *,
    tickers: Sequence[str] | str,
    start: str,
    end: str | None = None,
    interval: str = "1d",
    source: str = "Yahoo Finance via yfinance",
    auto_adjust: bool = True,
) -> pd.DataFrame:
    """Create a machine-readable data manifest for tutorial runs."""

    resolved = resolve_universe(tickers) if isinstance(tickers, str) else [str(t) for t in tickers]
    return pd.DataFrame(
        [
            {
                "source": source,
                "tickers": " ".join(resolved),
                "start": start,
                "end": end or "latest",
                "interval": interval,
                "auto_adjust": bool(auto_adjust),
                "archived_or_vendor_market_data": True,
                "research_note": "Educational source; replace with licensed point-in-time data for formal trading research.",
            }
        ]
    )


def prices_to_returns(prices: pd.DataFrame, *, log: bool = False) -> pd.DataFrame:
    """Convert a price panel to simple or log returns."""

    clean = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    if log:
        return np.log(clean).diff().replace([np.inf, -np.inf], np.nan).dropna(how="all")
    return clean.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="all")


def write_dataset_passport(
    prices: pd.DataFrame,
    output_path: str | Path,
    *,
    source: str = "Yahoo Finance via yfinance",
    start: str | None = None,
    end: str | None = None,
    interval: str = "1d",
) -> Path:
    """Write a dataset passport for a downloaded market-data panel."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    audit = data_audit_report(prices)
    for _, row in audit.iterrows():
        rows.append(
            {
                "dataset_name": str(row["ticker"]),
                "canonical_source": source,
                "version_or_access_window": f"{start or row['first_timestamp']}:{end or row['last_timestamp']}",
                "interval": interval,
                "raw_or_processed": "vendor_adjusted_ohlcv" if "yfinance" in source.lower() else "vendor_or_archived_real_data",
                "observations": int(row["observations"]),
                "first_timestamp": row["first_timestamp"],
                "last_timestamp": row["last_timestamp"],
                "missing_ratio": float(row["missing_ratio"]),
                "reproducibility_note": "Educational data source; replace with point-in-time licensed data for production research.",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path
