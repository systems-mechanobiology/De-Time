# Hot Trend Lab Data Sources

The column uses public data sources fetched by the notebooks and records source
coverage in the registry below.

## Source registry

| Source | What it measures | Notebook use | Freshness rule | Interpretation scope |
|---|---|---|---|---|
| arXiv API | preprint counts and metadata | category pulse, agent research pulse | refresh weekly or monthly | preprints are not peer-reviewed; cross-listing can double count |
| Hugging Face Hub API | model metadata, downloads, likes | open-model pulse | collect daily or weekly snapshots | repeated snapshots support time-series analysis; downloads are a public adoption proxy |
| GitHub REST API | repo metadata and stargazer timestamps | developer attention | collect weekly; use token for high-volume pulls | stars are attention, not production usage |
| Wikimedia Analytics API | article pageviews | public attention and hype decay | refresh daily or weekly | pageviews reflect public attention during the selected period |
| DeFiLlama stablecoin API | stablecoin supply and chain distribution | crypto liquidity pulse | refresh daily or weekly | endpoint structure can change; verify before publication |
| CoinGecko API | crypto price and market data | crypto pulse | refresh per run | rate limits and plan limits apply |
| Yahoo Finance through `yfinance` | public market prices | AI infrastructure market pulse | refresh per run | tutorial-grade source; use a licensed point-in-time vendor for production |

## Source table requirements

Tables should be derived from one of the public sources above or from a clearly
documented replacement source. The notebook must record:

- source name;
- URL or API endpoint;
- access date;
- query parameters;
- time range;
- data-quality and interpretation-scope notes.

## Source snapshot rules

Each table should be tied to a named source, query context, access date, and
time range. Cached files are treated as source snapshots and should carry the
same provenance fields as freshly fetched data.

## Caching policy

Cache files represent fetched source snapshots and should include an access date
in the filename or metadata.
