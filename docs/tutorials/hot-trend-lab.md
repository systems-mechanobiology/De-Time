# Hot Trend Lab: Real Data Trend and Cycle Decomposition

Hot topics usually have three time structures: a durable trend, a repeating
cadence, and a residual shock that breaks the normal pattern. DeTime is useful
here because it makes those structures explicit before the column turns them
into a story.

Consider a model-release week. arXiv may show a category or query spike before
the launch, Hugging Face may show a same-day snapshot jump, GitHub stars may
accelerate after demos ship, and Wikimedia or market proxies may react later.
Those signals are interesting together, but they answer different questions.
The column keeps source coverage, freshness, query context, timestamp, and
interpretation boundary next to each chart so a reader can tell what changed and
what still needs outside evidence.

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Public source</strong>
      <span>arXiv, Hugging Face, GitHub, Wikimedia, DeFiLlama, market data</span>
    </div>
    <div class="pipeline-step">
      <strong>DeTime</strong>
      <span><code>trend</code>, <code>season</code>, <code>residual</code>, <code>meta</code></span>
    </div>
    <div class="pipeline-step">
      <strong>Evidence table</strong>
      <span>source card, coverage, trend score, residual event rank</span>
    </div>
    <div class="pipeline-step">
      <strong>Column judgment</strong>
      <span>what moved, why it matters, what not to infer</span>
    </div>
  </div>
</div>

## What the reader gets

Each case study starts with a source protocol, then produces a table or figure
that supports a specific editorial judgment:

| Component | What to read | Example question |
|---|---|---|
| `trend` | durable direction over the selected window | Is a topic still building after the launch week? |
| `season` | repeated cadence | Is the pattern mostly deadline or weekday rhythm? |
| `residual` | event-like deviation from the smooth baseline | Which week deserves a closer read? |
| `meta` | source, query, timestamp, coverage, limits | Can this chart support the sentence being written? |

The result is not a popularity scoreboard. A single source rarely measures
quality, adoption, or economic value on its own.

## Column map

<div class="info-grid">
  <a class="info-card" href="data-sources/">
    <h3>Source Protocol</h3>
    <p>Source cards, reliability matrix, API limits, cache rules, and timestamp discipline.</p>
  </a>
  <a class="info-card" href="arxiv-research-pulse/">
    <h3>arXiv Research Pulse</h3>
    <p>Category and query counts with deadline-aware interpretation.</p>
  </a>
  <a class="info-card" href="open-model-and-developer-attention/">
    <h3>Open Models and Developer Attention</h3>
    <p>Launch-to-retention reading across Hugging Face snapshots and GitHub star velocity.</p>
  </a>
  <a class="info-card" href="wiki-market-crypto-attention/">
    <h3>Public Attention, Markets, and Crypto</h3>
    <p>A hub for public attention and market-proxy series, with market-structure boundaries.</p>
  </a>
  <a class="info-card" href="release-calendar/">
    <h3>Publishing Protocol</h3>
    <p>Monday scan, midweek verification, Friday publish, and residual-trigger rules.</p>
  </a>
</div>

## Case-study notebooks

The pages below render notebook code, tables, figures, and captured outputs directly
from `examples/notebooks/hot_trends/`. Read each notebook for three things: why the
source is interesting, how to read the tables or axes, and what decision the
output can support.

| Rendered page | Primary judgment | Main boundary |
|---|---|---|
| [01 arXiv category pulse](hot-trend-lab/notebooks/01_arxiv_category_pulse.md) | which fields are structurally growing or spiking | paper count is not paper quality |
| [02 arXiv agent research pulse](hot-trend-lab/notebooks/02_arxiv_agent_research_pulse.md) | which agent topics deserve a weekly read | query wording changes the sample |
| [03 Hugging Face open-model pulse](hot-trend-lab/notebooks/03_huggingface_open_model_pulse.md) | current public model attention and later retention | one snapshot cannot show momentum |
| [04 GitHub AI-agent star velocity](hot-trend-lab/notebooks/04_github_ai_agent_star_velocity.md) | developer attention during the covered window | stars are not production adoption |
| [05 Wikipedia attention hype decay](hot-trend-lab/notebooks/05_wikipedia_attention_hype_decay.md) | public-attention decay after a burst | pageviews are attention, not importance |
| [06 crypto stablecoin liquidity pulse](hot-trend-lab/notebooks/06_crypto_stablecoin_liquidity_pulse.md) | price residuals next to stablecoin context | not a trading signal |
| [07 AI infrastructure market pulse](hot-trend-lab/notebooks/07_ai_infrastructure_market_pulse.md) | market-price proxy movement around AI infrastructure | valuation needs financial statements |

The [rendered notebook index](hot-trend-lab/notebooks/index.md) and the
[00 overview notebook](hot-trend-lab/notebooks/00_hot_trend_lab_overview.md)
are appendix material for readers who want the full transcript list.

## Install optional dependencies

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/hot_trends/requirements.txt
```

Then open:

```bash
jupyter lab examples/notebooks/hot_trends
```

## Research scope

Use this column to analyze public attention, research activity, open-source
activity, liquidity, and market-proxy time series. Adoption, quality,
valuation, and investment decisions need separate evidence.
