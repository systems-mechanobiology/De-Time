# Hot Trend Lab: Real Data Trend and Cycle Decomposition

This tutorial column shows how to use De-Time as a real-data decomposition layer for fast-moving research, open-source, market, and public-attention time series.

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Real source</strong>
      <span>arXiv, Hugging Face, GitHub, Wikimedia, DeFiLlama, market data</span>
    </div>
    <div class="pipeline-step">
      <strong>De-Time</strong>
      <span><code>trend</code>, <code>season</code>, <code>residual</code>, <code>meta</code></span>
    </div>
    <div class="pipeline-step">
      <strong>Table</strong>
      <span>trend score, cycle strength, residual shock rank</span>
    </div>
    <div class="pipeline-step">
      <strong>Column</strong>
      <span>weekly research pulse, model pulse, developer pulse, liquidity pulse</span>
    </div>
  </div>
</div>

## Real-data policy

The Hot Trend Lab uses real public data fetched at runtime. It does **not** generate synthetic fallback data. If a source cannot be reached, the notebooks raise an explicit data error and stop.

This matters because the column is meant for overseas readers who may reuse the notebooks as a public-data workflow. A table is publishable only when its source, access date, query, and interpretation limits are visible.

## Why this column belongs in De-Time

A fast-moving public topic usually mixes three signals:

| Component | Interpretation | Example |
|---|---|---|
| `trend` | durable direction | AI paper production is rising across several arXiv categories |
| `season` | repeated cadence | weekly developer activity or monthly submission cycles |
| `residual` | shock outside the smooth pattern | a model release, policy event, ETF-flow break, or media burst |
| `meta` | reproducibility context | source URL, query, period, method, access date |

The point is not to claim prediction. The point is to force every viral topic into the same interpretable result contract before writing the narrative.

## Column map

<div class="info-grid">
  <a class="info-card" href="data-sources/">
    <h3>Real Data Sources</h3>
    <p>Source registry, API rules, access-date discipline, and no-synthetic-data policy.</p>
  </a>
  <a class="info-card" href="arxiv-research-pulse/">
    <h3>arXiv Research Pulse</h3>
    <p>Paper-count trend and cycle by category, plus query-based agent and coding-agent topic pulses.</p>
  </a>
  <a class="info-card" href="open-model-and-developer-attention/">
    <h3>Open Models and Developer Attention</h3>
    <p>Hugging Face model snapshots and GitHub star velocity as real attention proxies.</p>
  </a>
  <a class="info-card" href="wiki-market-crypto-attention/">
    <h3>Public Attention, Markets, and Crypto</h3>
    <p>Wikimedia pageviews, BTC/ETH, stablecoin supply, and AI infrastructure market proxies.</p>
  </a>
  <a class="info-card" href="release-calendar/">
    <h3>Release Calendar</h3>
    <p>A practical editorial calendar for weekly trend tables and deeper monthly case studies.</p>
  </a>
</div>

## Notebook series

The pages below render the notebook code and captured outputs directly in the
documentation. The original executable notebooks remain in
`examples/notebooks/hot_trends/`.

| Rendered page | Topic | Primary source |
|---|---|---|
| [00 Hot Trend Lab overview](hot-trend-lab/notebooks/00_hot_trend_lab_overview.md) | column roadmap and setup | source registry |
| [01 arXiv category pulse](hot-trend-lab/notebooks/01_arxiv_category_pulse.md) | research output by field | arXiv API |
| [02 arXiv agent research pulse](hot-trend-lab/notebooks/02_arxiv_agent_research_pulse.md) | AI agent / coding-agent paper pulse | arXiv API |
| [03 Hugging Face open-model pulse](hot-trend-lab/notebooks/03_huggingface_open_model_pulse.md) | open-model download and like snapshots | Hugging Face Hub API |
| [04 GitHub AI-agent star velocity](hot-trend-lab/notebooks/04_github_ai_agent_star_velocity.md) | developer attention and star velocity | GitHub REST API |
| [05 Wikipedia attention hype decay](hot-trend-lab/notebooks/05_wikipedia_attention_hype_decay.md) | public attention cycles | Wikimedia Analytics API |
| [06 crypto stablecoin liquidity pulse](hot-trend-lab/notebooks/06_crypto_stablecoin_liquidity_pulse.md) | crypto liquidity and stablecoin supply | DeFiLlama / CoinGecko / market data |
| [07 AI infrastructure market pulse](hot-trend-lab/notebooks/07_ai_infrastructure_market_pulse.md) | AI infrastructure market proxies | Yahoo Finance through `yfinance` |

## Install optional dependencies

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/hot_trends/requirements.txt
```

Then open:

```bash
jupyter lab examples/notebooks/hot_trends
```

## Important boundary

This is a research and documentation column. It is not investment advice, not a leaderboard, and not a claim that attention metrics equal adoption or quality.
