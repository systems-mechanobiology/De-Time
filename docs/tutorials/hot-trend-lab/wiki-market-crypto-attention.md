# Public Attention, Markets, and Crypto

This page is a hub for public attention and market-proxy series. The topics are
related because readers care about the same news cycle, but the measurements are
not interchangeable. Pageviews, crypto prices, stablecoin supply, and AI
infrastructure equity prices each need their own source card and boundary.

## Wikimedia attention

Wikimedia pageviews measure public attention during the selected period. The
chart is useful when a topic has moved from a technical audience into a broader
public audience.

Use [05 Wikipedia attention hype decay](notebooks/05_wikipedia_attention_hype_decay.md)
to read:

| Output | How to read it | Boundary |
|---|---|---|
| Pageview components | trend and residual attention for selected article titles | article naming and news events can dominate |
| Residual event table | dates with attention spikes outside the smooth baseline | event pointer, not importance score |
| Hype-decay table | how quickly attention falls after the spike | public attention only |

## Crypto and stablecoin liquidity

The crypto notebook combines BTC/ETH price residuals with current stablecoin
chain context. It is a market-structure read: price deviations and liquidity
context can help explain what moved, but the notebook does not produce entries,
exits, or risk sizing.

Use [06 crypto stablecoin liquidity pulse](notebooks/06_crypto_stablecoin_liquidity_pulse.md)
to read:

| Output | How to read it | Boundary |
|---|---|---|
| BTC/ETH components | transformed price, trend, and residual shocks | historical public prices, not trade signals |
| Residual events | event-like deviations from the decomposition baseline | inspect news and liquidity before interpretation |
| Stablecoin chain context | supply scale by chain from DeFiLlama | supply is not the same as executable liquidity |

## AI infrastructure market pulse

The AI infrastructure notebook uses a defined basket of public tickers as a
market-price proxy for AI infrastructure attention. The basket should be named
in the article, and it should be benchmarked against a broad market or sector
proxy before any relative-performance sentence is written.

Use [07 AI infrastructure market pulse](notebooks/07_ai_infrastructure_market_pulse.md)
to read:

| Output | How to read it | Boundary |
|---|---|---|
| Basket definition | selected tickers and date window | basket choice shapes the result |
| Trend index | normalized price and trend levels | price proxy, not fundamentals |
| Return versus trend slope | relation between simple return and DeTime trend slope | add benchmark before performance claims |
| Residual heatmap | dates where deviations cluster across names | event screen, not valuation analysis |

Revenue, capex, margins, guidance, and valuation require official financial
statements or licensed fundamentals data.

## Publication phrasing

| Overstated sentence | Evidence-based sentence |
|---|---|
| This residual predicts price. | This residual marks an event-like deviation from the decomposition baseline. |
| Downloads establish model quality. | Downloads are a public adoption proxy that needs benchmark context. |
| Stars establish production adoption. | Stars measure developer attention for the selected repository and period. |
| Pageviews establish importance. | Pageviews measure public attention during the selected period. |
