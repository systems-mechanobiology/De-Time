from __future__ import annotations

"""Real public-data loaders for the Hot Trend Lab.

The module deliberately has no artificial data generator. If a source is
unavailable, functions raise HotTrendDataError instead of producing a synthetic
series.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Mapping, Sequence
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import pandas as pd


class HotTrendDataError(RuntimeError):
    """Raised when a real public source cannot be fetched or validated."""


ARXIV_API = "https://export.arxiv.org/api/query"
ARXIV_NS = {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"}


@dataclass(frozen=True)
class SourceRecord:
    source: str
    endpoint: str
    access_date: str
    query: str
    notes: str = ""


def _read_url(
    url: str,
    *,
    timeout: int = 30,
    headers: Mapping[str, str] | None = None,
    retries: int = 0,
    retry_sleep: float = 5.0,
) -> bytes:
    request = urllib.request.Request(url, headers=dict(headers or {}))
    transient_http_codes = {429, 500, 502, 503, 504}
    for attempt in range(int(retries) + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except Exception as exc:  # pragma: no cover - network dependent
            status = exc.code if isinstance(exc, urllib.error.HTTPError) else None
            if attempt < int(retries) and status in transient_http_codes:
                time.sleep(float(retry_sleep) * (attempt + 1))
                continue
            raise HotTrendDataError(f"Could not fetch real data from {url}: {exc}") from exc
    raise HotTrendDataError(f"Could not fetch real data from {url}")


def _read_json(url: str, *, timeout: int = 30, headers: Mapping[str, str] | None = None):
    raw = _read_url(url, timeout=timeout, headers=headers)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise HotTrendDataError(f"Source returned non-JSON content: {url}") from exc


def arxiv_count(search_query: str, *, start_date: str, end_date: str, sleep_seconds: float = 3.0) -> int:
    """Count arXiv records for a query and submitted-date window.

    Parameters
    ----------
    search_query:
        Raw arXiv search query, e.g. ``cat:cs.LG`` or ``all:"coding agent"``.
    start_date, end_date:
        ISO date strings. The submittedDate window is inclusive at day level.
    sleep_seconds:
        arXiv asks automated clients not to make rapid-fire requests. Keep the
        default unless you are using your own controlled cache.
    """

    start = pd.Timestamp(start_date).strftime("%Y%m%d0000")
    end = pd.Timestamp(end_date).strftime("%Y%m%d2359")
    dated_query = f"({search_query}) AND submittedDate:[{start} TO {end}]"
    params = {
        "search_query": dated_query,
        "start": 0,
        "max_results": 1,
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
    }
    url = ARXIV_API + "?" + urllib.parse.urlencode(params)
    raw = _read_url(
        url,
        headers={"User-Agent": "De-Time-Hot-Trend-Lab/0.1"},
        timeout=45,
        retries=5,
        retry_sleep=max(30.0, float(sleep_seconds)),
    )
    if sleep_seconds:
        time.sleep(float(sleep_seconds))
    try:
        root = ET.fromstring(raw)
        total = root.find("opensearch:totalResults", ARXIV_NS)
        if total is None or total.text is None:
            raise HotTrendDataError("arXiv response did not contain totalResults")
        return int(total.text)
    except HotTrendDataError:
        raise
    except Exception as exc:
        raise HotTrendDataError("Could not parse arXiv Atom response") from exc


def monthly_windows(start_month: str, end_month: str) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    months = pd.date_range(pd.Timestamp(start_month).to_period("M").to_timestamp(), pd.Timestamp(end_month).to_period("M").to_timestamp(), freq="MS")
    return [(m, m + pd.offsets.MonthEnd(0)) for m in months]


def build_arxiv_monthly_counts(
    queries: Mapping[str, str],
    *,
    start_month: str,
    end_month: str,
    sleep_seconds: float = 3.0,
) -> pd.DataFrame:
    """Build a real monthly count table from the arXiv API."""

    rows: list[dict[str, object]] = []
    for label, query in queries.items():
        for start, end in monthly_windows(start_month, end_month):
            count = arxiv_count(query, start_date=start.date().isoformat(), end_date=end.date().isoformat(), sleep_seconds=sleep_seconds)
            rows.append(
                {
                    "month": start.date().isoformat(),
                    "series": label,
                    "query": query,
                    "count": count,
                    "source": "arXiv API",
                    "access_date": date.today().isoformat(),
                    "data_quality": "live_public_api_no_synthetic_fallback",
                }
            )
    if not rows:
        raise HotTrendDataError("No arXiv rows were fetched")
    return pd.DataFrame(rows)


def fetch_huggingface_models(*, limit: int = 50, sort: str = "downloads", direction: int = -1, search: str | None = None) -> pd.DataFrame:
    """Fetch a real Hugging Face Hub model metadata snapshot."""

    params: dict[str, object] = {"limit": int(limit), "sort": sort, "direction": int(direction)}
    if search:
        params["search"] = search
    url = "https://huggingface.co/api/models?" + urllib.parse.urlencode(params)
    data = _read_json(url)
    if not isinstance(data, list) or not data:
        raise HotTrendDataError("Hugging Face API returned no model records")
    rows = []
    access_date = date.today().isoformat()
    for item in data:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "snapshot_date": access_date,
                "model_id": item.get("modelId"),
                "pipeline_tag": item.get("pipeline_tag"),
                "downloads": item.get("downloads"),
                "likes": item.get("likes"),
                "last_modified": item.get("lastModified"),
                "private": item.get("private"),
                "source": "Hugging Face Hub API",
                "data_quality": "live_public_api_no_synthetic_fallback",
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        raise HotTrendDataError("Hugging Face API response could not be tabulated")
    return out


def append_real_snapshot(snapshot: pd.DataFrame, path: str | Path) -> pd.DataFrame:
    """Append a real snapshot to a CSV log and return the full log."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        previous = pd.read_csv(path)
        full = pd.concat([previous, snapshot], ignore_index=True)
    else:
        full = snapshot.copy()
    full.to_csv(path, index=False)
    return full


def fetch_github_repo_metadata(repo: str, *, token: str | None = None) -> dict[str, object]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"https://api.github.com/repos/{repo}"
    data = _read_json(url, headers=headers)
    if not isinstance(data, dict) or "full_name" not in data:
        raise HotTrendDataError(f"GitHub API did not return repository metadata for {repo}")
    return data


def fetch_github_stargazers(repo: str, *, pages: int = 5, token: str | None = None, per_page: int = 100) -> pd.DataFrame:
    """Fetch real stargazer timestamps from GitHub REST API."""

    headers = {"Accept": "application/vnd.github.star+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    rows: list[dict[str, object]] = []
    for page in range(1, int(pages) + 1):
        url = f"https://api.github.com/repos/{repo}/stargazers?" + urllib.parse.urlencode({"per_page": int(per_page), "page": int(page)})
        data = _read_json(url, headers=headers)
        if not data:
            break
        if not isinstance(data, list):
            raise HotTrendDataError(f"GitHub stargazer response was not a list for {repo}")
        for item in data:
            if isinstance(item, dict):
                user = item.get("user") or {}
                rows.append(
                    {
                        "repo": repo,
                        "starred_at": item.get("starred_at"),
                        "login": user.get("login") if isinstance(user, dict) else None,
                        "source": "GitHub REST API",
                        "data_quality": "live_public_api_no_synthetic_fallback",
                    }
                )
    if not rows:
        raise HotTrendDataError(f"No stargazer rows fetched for {repo}. Use a token or increase permissions if needed.")
    return pd.DataFrame(rows)


def fetch_wikipedia_pageviews(
    article: str,
    *,
    project: str = "en.wikipedia.org",
    start: str,
    end: str,
    access: str = "all-access",
    agent: str = "user",
    granularity: str = "daily",
) -> pd.DataFrame:
    """Fetch real Wikimedia pageviews for one article."""

    article_quoted = urllib.parse.quote(article.replace(" ", "_"), safe="")
    start_s = pd.Timestamp(start).strftime("%Y%m%d00")
    end_s = pd.Timestamp(end).strftime("%Y%m%d00")
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"{project}/{access}/{agent}/{article_quoted}/{granularity}/{start_s}/{end_s}"
    )
    data = _read_json(url, headers={"User-Agent": "De-Time-Hot-Trend-Lab/0.1"})
    items = data.get("items") if isinstance(data, dict) else None
    if not items:
        raise HotTrendDataError(f"No Wikimedia pageviews returned for {article}")
    rows = []
    for item in items:
        rows.append(
            {
                "date": pd.to_datetime(str(item.get("timestamp"))[:8], format="%Y%m%d").date().isoformat(),
                "article": article,
                "views": item.get("views"),
                "project": project,
                "source": "Wikimedia Analytics API",
                "data_quality": "live_public_api_no_synthetic_fallback",
            }
        )
    return pd.DataFrame(rows)


def fetch_defillama_stablecoin_chains() -> pd.DataFrame:
    """Fetch real stablecoin chain data from DeFiLlama."""

    url = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
    data = _read_json(url)
    chains = data.get("chains") if isinstance(data, dict) else None
    if chains is None:
        # Some endpoint responses expose stablecoins directly; keep the error explicit.
        raise HotTrendDataError("DeFiLlama stablecoin response did not contain a 'chains' table")
    return pd.DataFrame(chains)


def fetch_coingecko_market_chart(coin_id: str, *, vs_currency: str = "usd", days: int = 365) -> pd.DataFrame:
    """Fetch real crypto market chart data from CoinGecko's public API."""

    params = {"vs_currency": vs_currency, "days": int(days)}
    url = f"https://api.coingecko.com/api/v3/coins/{urllib.parse.quote(coin_id)}/market_chart?" + urllib.parse.urlencode(params)
    data = _read_json(url)
    if not isinstance(data, dict) or "prices" not in data:
        raise HotTrendDataError(f"CoinGecko returned no market chart for {coin_id}")
    prices = pd.DataFrame(data["prices"], columns=["timestamp_ms", "price"])
    prices["date"] = pd.to_datetime(prices["timestamp_ms"], unit="ms").dt.date.astype(str)
    prices["coin_id"] = coin_id
    prices["source"] = "CoinGecko API"
    prices["data_quality"] = "live_public_api_no_synthetic_fallback"
    return prices[["date", "coin_id", "price", "source", "data_quality"]]


def source_audit_table(frame: pd.DataFrame, *, value_col: str, entity_col: str, time_col: str) -> pd.DataFrame:
    if frame.empty:
        raise HotTrendDataError("Cannot audit an empty frame")
    rows = []
    for entity, sub in frame.groupby(entity_col):
        values = pd.to_numeric(sub[value_col], errors="coerce")
        rows.append(
            {
                "series": entity,
                "first_timestamp": str(pd.to_datetime(sub[time_col]).min()),
                "last_timestamp": str(pd.to_datetime(sub[time_col]).max()),
                "observations": int(values.notna().sum()),
                "missing_ratio": float(values.isna().mean()),
                "min_value": float(values.min()) if values.notna().any() else None,
                "max_value": float(values.max()) if values.notna().any() else None,
            }
        )
    return pd.DataFrame(rows)
