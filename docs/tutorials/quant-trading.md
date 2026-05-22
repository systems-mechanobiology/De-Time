# Quant Trading Column: Decomposition Signals with Real Market Data

This tutorial column shows how to use De-Time as a decomposition layer for
quantitative trading research. The core idea is simple:

<div class="quant-column-stage">
  <div class="quant-column-copy">
    <span class="section-kicker">Notebook research column</span>
    <h2>Expose trend, cycle, and residual before the signal layer.</h2>
    <p>Each tutorial keeps the De-Time interface visible while market data, strategy logic, backtest adapters, and validation remain explicit research steps.</p>
    <div class="quant-stage-metrics">
      <span><b>10</b> notebooks</span>
      <span><b>4</b> guide pages</span>
      <span><b>1</b> result contract</span>
    </div>
  </div>
  <div class="quant-research-ui" aria-label="De-Time quantitative trading tutorial interface">
    <div class="quant-ui-bar">
      <strong>Quant column</strong>
      <span>features.py</span>
      <i>real market input</i>
    </div>
    <div class="quant-ui-body">
      <div class="quant-ui-rail">
        <b>Data</b>
        <span>US</span>
        <span>Korea</span>
        <span>ETF</span>
        <span>Crypto</span>
      </div>
      <div class="quant-ui-canvas">
        <div class="quant-timeline">
          <span>252d train</span>
          <span>21d step</span>
          <span>costs on</span>
        </div>
        <div class="quant-price-chart"><span>Price</span><i></i></div>
        <div class="quant-component trend"><span>Trend slope</span><i></i></div>
        <div class="quant-component seasonal"><span>Cycle timing</span><i></i></div>
        <div class="quant-component residual"><span>Residual stress</span><i></i></div>
      </div>
      <div class="quant-ui-cards">
        <span><b>Signal</b> trend pullback</span>
        <span><b>Adapter</b> pandas -> vectorbt</span>
        <span><b>Audit</b> shift and cost check</span>
      </div>
    </div>
  </div>
</div>

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

## Market Data Sources

The column downloads market data at runtime through `yfinance`, validates the
returned tables, and records the ticker universe, date window, and data source
used by each notebook.
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
    <p>US, Korea, ETF, and crypto market data loading with source and table validation.</p>
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
    <p>Walk-forward alignment, transaction costs, and benchmark reporting.</p>
  </a>
</div>

## Notebook series

The pages below render the notebook code and captured outputs directly in the
documentation. The original executable notebooks remain in
`examples/notebooks/quant_trading/`.

| Rendered page | Topic | Main asset class |
|---|---|---|
| [00 quant trading column overview](quant-trading/notebooks/00_quant_trading_column_overview.md) | column roadmap and setup | all |
| [01 real market data and De-Time features](quant-trading/notebooks/01_real_market_data_and_detime_features.md) | real data download and feature factory | US, Korea, crypto |
| [02 single-asset timing with vectorbt](quant-trading/notebooks/02_single_asset_timing_vectorbt.md) | trend pullback and residual timing | SPY / QQQ |
| [03 Turtle Donchian trend filter](quant-trading/notebooks/03_turtle_donchian_trend_filter.md) | Turtle/Donchian trend filter | ETFs |
| [04 pairs trading residual cycle](quant-trading/notebooks/04_pairs_trading_residual_cycle.md) | spread decomposition for pairs | US equities |
| [05 cross-sectional factor selection](quant-trading/notebooks/05_cross_sectional_factor_selection.md) | decomposition alpha features | US stocks |
| [06 style and sector rotation](quant-trading/notebooks/06_style_sector_asset_rotation_bt.md) | style/sector ETF rotation | ETFs |
| [07 Korea, US, and crypto multimarket](quant-trading/notebooks/07_korea_us_crypto_multimarket.md) | multi-market cycle and regime ideas | Korea, US, crypto |
| [08 backtesting framework adapters](quant-trading/notebooks/08_backtesting_framework_adapters.md) | framework adapters | all |
| [09 walk-forward validation](quant-trading/notebooks/09_walkforward_validation_and_audit.md) | validation and reporting protocol | all |

<div class="quant-notebook-grid">
  <a href="notebooks/00_quant_trading_column_overview/">
    <span>00</span>
    <strong>Column Overview</strong>
    <small>Setup, reading order, and the decomposition-to-signal map.</small>
  </a>
  <a href="notebooks/01_real_market_data_and_detime_features/">
    <span>01</span>
    <strong>Real Data Features</strong>
    <small>Market downloads, audits, and De-Time feature construction.</small>
  </a>
  <a href="notebooks/02_single_asset_timing_vectorbt/">
    <span>02</span>
    <strong>Single Asset Timing</strong>
    <small>Trend pullbacks and residual timing with vectorbt routing.</small>
  </a>
  <a href="notebooks/03_turtle_donchian_trend_filter/">
    <span>03</span>
    <strong>Turtle Trend Filter</strong>
    <small>Donchian breakouts gated by decomposition trend context.</small>
  </a>
  <a href="notebooks/04_pairs_trading_residual_cycle/">
    <span>04</span>
    <strong>Pairs Residual Cycle</strong>
    <small>Spread features with trend drift and residual checks.</small>
  </a>
  <a href="notebooks/05_cross_sectional_factor_selection/">
    <span>05</span>
    <strong>Factor Selection</strong>
    <small>Cross-sectional ranking from decomposition alpha features.</small>
  </a>
  <a href="notebooks/06_style_sector_asset_rotation_bt/">
    <span>06</span>
    <strong>ETF Rotation</strong>
    <small>Style and sector target weights for portfolio research.</small>
  </a>
  <a href="notebooks/07_korea_us_crypto_multimarket/">
    <span>07</span>
    <strong>Multi-Market Regimes</strong>
    <small>Korea, US, and crypto cycle and stress examples.</small>
  </a>
  <a href="notebooks/08_backtesting_framework_adapters/">
    <span>08</span>
    <strong>Framework Adapters</strong>
    <small>Route signals into pandas and optional backtesting tools.</small>
  </a>
  <a href="notebooks/09_walkforward_validation_and_audit/">
    <span>09</span>
    <strong>Validation Audit</strong>
    <small>Walk-forward features, position shifting, and failure logs.</small>
  </a>
</div>

## Install the optional tutorial dependencies

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/quant_trading/requirements.txt
```

Then open:

```bash
jupyter lab examples/notebooks/quant_trading
```

## Research Scope

Use these examples to understand how decomposition features can become research
signals. Live-trading evaluation requires point-in-time data, realistic costs,
execution modeling, risk controls, and independent validation.
