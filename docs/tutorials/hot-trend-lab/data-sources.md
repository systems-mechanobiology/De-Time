# Hot Trend Lab Data Sources

The column uses live public data only. No notebook fabricates a replacement series when a source is unavailable.

## Source registry

| Source | What it measures | Notebook use | Freshness rule | Main caveat |
|---|---|---|---|---|
| arXiv API | preprint counts and metadata | category pulse, agent research pulse | refresh weekly or monthly | preprints are not peer-reviewed; cross-listing can double count |
| Hugging Face Hub API | model metadata, downloads, likes | open-model pulse | collect daily or weekly snapshots | one snapshot is not a time series; downloads are an adoption proxy |
| GitHub REST API | repo metadata and stargazer timestamps | developer attention | collect weekly; use token for high-volume pulls | stars are attention, not production usage |
| Wikimedia Analytics API | article pageviews | public attention and hype decay | refresh daily or weekly | pageviews reflect attention, not correctness or importance |
| DeFiLlama stablecoin API | stablecoin supply and chain distribution | crypto liquidity pulse | refresh daily or weekly | endpoint structure can change; verify before publication |
| CoinGecko API | crypto price and market data | crypto pulse | refresh per run | rate limits and plan limits apply |
| Yahoo Finance through `yfinance` | public market prices | AI infrastructure market pulse | refresh per run | tutorial-grade source; use a licensed point-in-time vendor for production |

## What counts as real data

A table counts as real data only if it is derived from one of the public sources above or from a clearly documented replacement source. The notebook must record:

- source name;
- URL or API endpoint;
- access date;
- query parameters;
- time range;
- data-quality caveat.

## What is not allowed

The Hot Trend Lab notebooks do not use artificial fallback series, simulated prices, random counts, or placeholder snapshots. If a source fails, the notebook should fail loudly so the reader does not confuse a demo with evidence.

## Caching policy

A cache is allowed only after a real source has been fetched. Cache files should be treated as source snapshots and should include an access date in the filename or metadata.
