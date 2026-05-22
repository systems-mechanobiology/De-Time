# Quant Trading Column: Decomposition Signals with Real Market Data

This tutorial column shows how to use De-Time as a decomposition layer for
quantitative trading research. The core idea is simple:

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Price</strong>
      <span>US equities, Korea equities, ETFs, crypto</span>
    </div>
    <div class="pipeline-step">
      <strong>De-Time</strong>
      <span><code>trend</code>, <code>season</code>, <code>residual</code></span>
    </div>
    <div class="pipeline-step">
      <strong>Signal</strong>
      <span>timing, pairs, factors, rotation, risk filter</span>
    </div>
    <div class="pipeline-step">
      <strong>Backtest</strong>
      <span>pandas, vectorbt, backtesting.py, bt, Backtrader, Zipline, QuantStats</span>
    </div>
  </div>
</div>

## Real-data policy

The column uses real market data downloaded at runtime through `yfinance`.
It does not create artificial price data. If the vendor request fails, the
notebook stops with a data error instead of silently replacing market data.
The example universes include US large-cap stocks, US style and sector ETFs,
Korean equities using `.KS` / `.KQ` symbols, and crypto pairs such as
`BTC-USD` and `ETH-USD`.

For production research, replace the tutorial data source with a licensed,
point-in-time vendor and document the calendar, corporate-action adjustment,
borrow, liquidity, FX, and execution assumptions.

## Why decomposition matters to a trader

Raw prices mix several structures that should not always drive the same action.
De-Time returns a common `DecompResult` with `trend`, `season`, `residual`,
method-specific `components`, and `meta`. The same result contract is then used
to derive practical trading features:

| Component | Trading interpretation | Example signal |
|---|---|---|
| `trend` | Direction and persistence | only trade long breakouts when `trend_slope > 0` |
| `season` | Timing, cycle, oscillatory rhythm | enter when the cycle turns upward |
| `residual` | Deviation from modeled structure | buy pullbacks or mean-revert pair spread residuals |
| reconstruction error / residual stress | reliability and risk | reduce exposure when `residual_abs_z` is extreme |

## Column map

<div class="info-grid">
  <a class="info-card" href="data/">
    <h3>Real Data and Universes</h3>
    <p>US, Korea, ETF, and crypto market data loading with explicit validation and no artificial fallback.</p>
  </a>
  <a class="info-card" href="strategy-map/">
    <h3>Strategy Map</h3>
    <p>Trend following, Turtle/Donchian, residual mean reversion, pairs, factors, rotation, crypto regimes.</p>
  </a>
  <a class="info-card" href="backtesting-frameworks/">
    <h3>Backtesting Frameworks</h3>
    <p>Adapters for pandas, vectorbt, backtesting.py, bt, Backtrader, Zipline-Reloaded, and QuantStats.</p>
  </a>
  <a class="info-card" href="walkforward/">
    <h3>Walk-Forward Validation</h3>
    <p>How to avoid full-sample decomposition leakage, unrealistic costs, and hidden benchmark reduction.</p>
  </a>
</div>

## Notebook series

The GitHub-rendered notebooks live in `examples/notebooks/quant_trading/`.

| Notebook | Topic | Main asset class |
|---|---|---|
| `00_quant_trading_column_overview.ipynb` | column roadmap and setup | all |
| `01_real_market_data_and_detime_features.ipynb` | real data download and feature factory | US, Korea, crypto |
| `02_single_asset_timing_vectorbt.ipynb` | trend pullback and residual timing | SPY / QQQ |
| `03_turtle_donchian_trend_filter.ipynb` | Turtle/Donchian trend filter | ETFs |
| `04_pairs_trading_residual_cycle.ipynb` | spread decomposition for pairs | US equities |
| `05_cross_sectional_factor_selection.ipynb` | decomposition alpha features | US stocks |
| `06_style_sector_asset_rotation_bt.ipynb` | style/sector ETF rotation | ETFs |
| `07_korea_us_crypto_multimarket.ipynb` | multi-market cycle and regime ideas | Korea, US, crypto |
| `08_backtesting_framework_adapters.ipynb` | framework adapters | all |
| `09_walkforward_validation_and_audit.ipynb` | validation and audit protocol | all |

## Install the optional tutorial dependencies

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/quant_trading/requirements.txt
```

Then open:

```bash
jupyter lab examples/notebooks/quant_trading
```

## Important boundary

This is a research tutorial, not investment advice. The examples are intended
to help readers understand how decomposition features can be transformed into
signals. They do not claim live-trading profitability.
