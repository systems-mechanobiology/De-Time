# Column 05-06 Development Plan

## Column 05: pair spread decomposition and stat-arb

Goal: move pair trading from raw ratio/spread z-scores to a structural spread model.

Implementation objects:

- rolling hedge-ratio spread construction;
- classical pair baselines: ratio z-score, rolling-beta spread z-score, correlation-filtered spread;
- De-Time spread strategies: residual-z reversion, cycle-timed residual reversion, trend-drift blocker;
- pair diagnostics: rolling beta, spread z-score, rolling correlation, trend drift, residual state;
- report outputs: spread panel, beta panel, pair diagnostics, feature snapshot, strategy comparison, turnover report and run manifest.

## Column 06: cross-sectional rotation and portfolio construction

Goal: turn De-Time features into a cross-sectional allocation score rather than treating decomposition as a single-asset indicator.

Implementation objects:

- classical rotation baselines: equal weight, momentum rank, multi-MA trend rank, inverse-volatility allocation;
- De-Time rotation score: trend strength, trend slope, cycle slope, residual pullback/overextension, volume participation and component stability;
- portfolio recipes: top-N long-only, low-turnover monthly variant, no-vol-target ablation and long-short rotation;
- diagnostics: factor snapshot, feature coverage, input-volume availability, turnover and run manifest.

## Data policy

Bundled offline runs use real historical FX OHLCV files from the uploaded Learn Algorithmic Trading material. FX volume is unavailable in that source, so the implementation records volume unavailable and uses neutral volume participation rather than inventing volume. Live-data scripts support equities and ETFs with real volume fields.

## Execution stages

| Stage | Command | Evidence status |
|---|---|---|
| smoke | `make smoke-05-06` | import + real sample + small backtest plumbing |
| tutorial run | `make quant-columns-05-06` | bundled real-data strategy tables and manifests |
| live pilot | `make quant-columns-05-06-live` | requires network/yfinance; not run in offline sandbox |
| full benchmark | future BlueBEAR CPU sweep | not part of tutorial evidence |

## Boundary

The columns are educational strategy research examples. They are designed to show how decomposition enters pair trading and portfolio rotation. They are not production trading recommendations.
