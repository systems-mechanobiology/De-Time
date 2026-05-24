# Quant Trading Column: Decomposition Signals with Real Market Data

This column is a task entrance for quantitative research with De-Time. The
workflow is: get market data, audit the table, compute walk-forward
decomposition features, test a baseline, test a strategy, report the boundary,
then route the signal into a backtesting framework only after the alignment is
understood.

The Quant examples use `ROBUST_STL` as the default decomposition method. It keeps
the trend/season/residual contract readable while reducing the edge and shock
sensitivity that makes simple moving-average-style decomposition unsuitable for
market prices.

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Data</strong>
      <span>universe, calendar, adjusted prices, cache date</span>
    </div>
    <div class="pipeline-step">
      <strong>Features</strong>
      <span><code>trend</code>, <code>season</code>, <code>residual</code>, timestamp</span>
    </div>
    <div class="pipeline-step">
      <strong>Signal</strong>
      <span>single asset, pairs, factors, rotation, risk filter</span>
    </div>
    <div class="pipeline-step">
      <strong>Validation</strong>
      <span>baseline, costs, turnover, drawdown, leakage audit</span>
    </div>
  </div>
</div>

## Start here

| Task | Page | What to decide |
|---|---|---|
| Audit the data | [Data Due Diligence](quant-trading/data.md) | whether the source can support the experiment |
| Pick a strategy family | [Strategy Selection Map](quant-trading/strategy-map.md) | the hypothesis, baseline, and failure mode |
| Choose a backtest route | [Backtesting Adapter Contract](quant-trading/backtesting-frameworks.md) | what must be preserved when moving frameworks |
| Run the audit gate | [Validation First](quant-trading/walkforward.md) | whether the result is confirming, inconclusive, or failed |

## Result contract

Every notebook result should report the same fields before it is discussed:

| Field | Required content |
|---|---|
| Sample | ticker universe, start date, end date, data source, cache or access date |
| Parameters | method, period, train window, step, signal thresholds, rebalance rule |
| Baseline | equal-weight, buy-and-hold benchmark, classical strategy, or momentum-only comparator |
| Costs | fees, slippage, turnover, borrow or FX assumptions when relevant |
| Metrics | total return, CAGR, volatility, Sharpe, max drawdown, turnover |
| Boundary | confirming, inconclusive, or failed; state why |

Strong results need baselines and overfitting checks. Weak results should be
written as validation findings, not wrapped as strategy success.

## De-Time feature roles

Raw prices mix structures that should not all trigger the same action. De-Time
returns a common `DecompResult` with `trend`, `season`, `residual`,
method-specific `components`, and `meta`. `ROBUST_STL` is the default in this
column because equity and crypto series often contain shocks, gaps, and
month-end effects that should be treated as residual stress rather than pulled
into the smooth trend.

| Component | Research interpretation | Example signal use |
|---|---|---|
| `trend` | direction and persistence | require positive `trend_slope` before long breakouts |
| `season` | timing or oscillatory rhythm | compare cycle direction with entry timing |
| `residual` | deviation from modeled structure | screen pullbacks or spread dislocations |
| residual stress / reconstruction error | reliability warning | reduce exposure or reject a trade |

## Notebook series

The original executable notebooks remain in `examples/notebooks/quant_trading/`.
The rendered pages below show code, figures, tables, and captured outputs directly.

| Rendered page | Research question | Required boundary |
|---|---|---|
| [01 real market data and De-Time features](quant-trading/notebooks/01_real_market_data_and_detime_features.md) | can the source support walk-forward features? | public data source and coverage limits |
| [02 single-asset timing with vectorbt](quant-trading/notebooks/02_single_asset_timing_vectorbt.md) | does trend plus residual timing beat simple timing baselines? | after-cost and same-bar shift check |
| [03 Turtle Donchian trend filter](quant-trading/notebooks/03_turtle_donchian_trend_filter.md) | does a trend filter improve a classical breakout? | compare with unfiltered Donchian |
| [04 pairs trading residual cycle](quant-trading/notebooks/04_pairs_trading_residual_cycle.md) | does spread residual help avoid trend drift? | cointegration and spread-stability checks |
| [05 cross-sectional factor selection](quant-trading/notebooks/05_cross_sectional_factor_selection.md) | do decomposition factor candidates beat baselines? | equal-weight, benchmark, momentum, and random baselines |
| [06 style and sector rotation](quant-trading/notebooks/06_style_sector_asset_rotation_bt.md) | does decomposition scoring help ETF rotation? | turnover and benchmark comparison |
| [07 Korea, US, and crypto multimarket](quant-trading/notebooks/07_korea_us_crypto_multimarket.md) | what changes across calendars and asset classes? | calendar, FX, and 24/7 trading boundaries |
| [08 backtesting framework adapters](quant-trading/notebooks/08_backtesting_framework_adapters.md) | can signals move into another framework without changing meaning? | adapter contract and alignment checks |
| [09 walk-forward validation](quant-trading/notebooks/09_walkforward_validation_and_audit.md) | did the experiment pass the validation gate? | leakage, shift, coverage, baseline, and failed-run log |

The [rendered notebook index](quant-trading/notebooks/index.md) and
[00 overview notebook](quant-trading/notebooks/00_quant_trading_column_overview.md)
are appendix references.

## Install the optional tutorial dependencies

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/quant_trading/requirements.txt
```

Then open:

```bash
jupyter lab examples/notebooks/quant_trading
```

## Research scope

Use these examples to understand whether decomposition features survive data
audits, baseline comparison, costs, and leakage checks. Live trading decisions
need point-in-time data, broker-aware execution assumptions, risk controls, and
independent validation.
