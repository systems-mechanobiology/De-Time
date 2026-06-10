# Decomposition-First Quant Trading Tutorials with DeTime

This tutorial sequence rebuilds the quant-trading examples around one thesis:
classic technical strategies are rough, implicit estimates of trend, cycle,
residual deviation, and market participation. DeTime makes those structures
explicit before the strategy layer.

The revised tutorial uses a seven-part path rather than a loose collection of
indicator notebooks.

[Open the executed tutorial notebook index](quant-trading/notebooks/index.md)
to jump directly between Tutorial 00-07, the strategy lab notebooks, and the
strategy expansion notebooks.

| Tutorial | Status | Topic | Main DeTime role |
|---|---|---|---|
| 00 | implemented | roadmap | strategy design map |
| 01 | implemented | market data and feature factory | price + volume decomposition |
| 02 | implemented | moving average, multi-MA and MACD | explicit trend filters with cycle/residual/volume gates |
| 03 | implemented | RSI, Bollinger and residual mean reversion | residual deviation, cycle timing and volume filter |
| 04 | implemented | Turtle/Donchian breakout | trend, cycle, residual overextension and volume confirmation |
| 05 | implemented | pairs trading and stat arb | spread trend drift + spread residual + optional volume news filter |
| 06 | implemented | cross-sectional rotation | trend/cycle/residual/volume decomposition factor score |
| 07 | implemented | native SSA high-return / low-drawdown replay | fast/slow SSA trends, next-open fills, drawdown and monthly trade diagnostics |

## Strategy-lab correction: two concrete trading systems

The clearest entry point is now the strategy lab, not the broad seven-tutorial map.
It implements two complete strategy families:

1. **Trend following**: `trend_slope` and `trend_strength` create the trading signal; `cycle_position`, `residual_abs_z`, and volume decomposition control entry timing and overextension.
2. **Oscillation / residual reversion**: when `abs(trend_strength)` is small, the strategy trades `residual_z` around `trend + cycle`; negative residual buys, positive residual sells or shorts.

Run it with:

```bash
make strategy-lab
```

Main implementation files:

```text
examples/quant_trading/strategy_lab.py
examples/quant_trading/scripts/run_strategy_lab.py
examples/notebooks/quant_trading/01_detime_trend_following_strategy_lab.ipynb
examples/notebooks/quant_trading/02_detime_oscillation_reversion_strategy_lab.ipynb
docs/tutorials/quant-trading/two-strategy-families.md
```

The script writes strategy stats, order records, round-trip trades, feature coverage, run manifest, and buy/sell charts under `examples/quant_trading/reports/strategy_lab/`.

## Implemented notebooks

The executable notebooks are in `examples/notebooks/quant_trading/`:
install the optional notebook and market-data dependencies from
`examples/quant_trading/requirements.txt`. The rendered documentation publishes
the captured outputs directly at
`quant-trading/notebooks/01_market_data_and_decomposition_feature_factory.md`
and the companion pages in the same notebook directory.

| Notebook | What it teaches |
|---|---|
| `00_decomposition_first_quant_trading_roadmap.ipynb` | Why the tutorial is organized around decomposition rather than isolated indicators. |
| `01_market_data_and_decomposition_feature_factory.ipynb` | OHLCV audit, period estimation, and walk-forward price/volume feature construction. |
| `02_decomposition_aware_moving_average_macd.ipynb` | Classical buy-and-hold, dual MA, MACD, multi-MA and momentum compared with DeTime rewrites. |
| `03_residual_mean_reversion_rsi_bollinger.ipynb` | Price z-score, RSI, Bollinger and APO baselines rewritten as residual mean-reversion with cycle timing. |
| `04_turtle_donchian_breakout_volume_confirmation.ipynb` | Donchian/Turtle breakout rewritten with trend, cycle, residual and volume confirmation. |
| `05_pairs_spread_decomposition_stat_arb.ipynb` | Pair z-score and rolling-beta spread baselines rewritten as residual spread trading with spread-trend drift control. |
| `06_cross_sectional_rotation_portfolio.ipynb` | Momentum, multi-MA and inverse-volatility rotation compared with DeTime cross-sectional scoring. |
| `07_native_ssa_high_return_low_drawdown_tutorial.ipynb` | Native SSA dual-trend mean-reversion replay for selected high-return FX and crypto strategies under a 20% drawdown constraint. |

## Core design

For price and volume we use:

\[
\log P_t = T^P_t + C^P_t + R^P_t,
\qquad
\log(1 + V_t) = T^V_t + C^V_t + R^V_t.
\]

The strategy layer then reads:

| Component | Trading interpretation | Example use |
|---|---|---|
| price trend | direction and persistence | trend-following state, decomposed MA/MACD |
| price cycle | timing and local oscillation | avoid buying into overextended cycle peaks |
| price residual | deviation from current structure | pullback and mean-reversion logic |
| volume trend | participation | confirm trend or breakout |
| volume residual | abnormal activity | detect volume shock or weak participation |
| reconstruction error / stability | feature reliability | reduce exposure when component quality weakens |

## Data layer

The code supports live downloads through `yfinance`. The rendered documentation
uses archived historical GOOG and FX OHLCV samples from the user-provided Learn
Algorithmic Trading material so the pages can be rebuilt without network access.

For formal trading research, replace the educational data source with a licensed
point-in-time vendor and document symbol membership, corporate actions,
delistings, borrow, funding, FX, and execution assumptions.

## Code modules

| Module | Purpose |
|---|---|
| `data.py` | OHLCV download, panel extraction, archived market-data loader |
| `classic_indicators.py` | SMA, EMA, MACD, RSI, Bollinger, momentum, APO |
| `decomposition_features.py` | walk-forward price and volume DeTime features |
| `strategy_baselines.py` | classical baseline weight recipes |
| `strategy_detime.py` | decomposition-aware strategy recipes |
| `strategy_pairs.py` | pair spread decomposition and stat-arb recipes |
| `strategy_rotation.py` | cross-sectional rotation and portfolio recipes |
| `validation.py` | common backtest comparison, turnover, manifest helpers |
| `backtest.py` | transparent close-to-close research backtester |

## Smoke test

```bash
export PYTHONPATH="$PWD/src:$PWD/examples:$PYTHONPATH"
make smoke-05-06
```

The smoke tests run on CPU and write hardware/audit outputs under
`examples/quant_trading/reports/`.


## Latest Implemented Tutorials

Tutorials 03-04 cover single-asset reversion and breakout strategies:

- Tutorial 03 keeps familiar entry points, including RSI, Bollinger Bands, APO and price z-score, but changes the traded object from raw price deviation to residual deviation after trend/cycle removal.
- Tutorial 04 keeps the Donchian/Turtle breakout scaffold but adds trend, cycle, residual-overextension and volume-participation gates.

Tutorials 05-07 complete the current arc:

- Tutorial 05 rewrites pairs trading by decomposing the rolling hedge spread and trading residual deviation only when spread trend drift is controlled.
- Tutorial 06 turns decomposition outputs into a cross-sectional factor score for top-N, long-short and volatility-targeted rotation portfolios.
- Tutorial 07 replays selected native SSA dual-trend strategies, including buy/sell markers, strategy-vs-buy-hold equity, drawdown curves, and monthly return / win-rate tables.

Run the latest batch on bundled real FX samples:

```bash
make quant-columns-05-06
```

Run the bundled-sample Tutorial 01-06 batch:

```bash
make quant-columns-01-06
```

Tutorial 07 is a notebook replay for local 3-minute intraday files. Open it from
the rendered documentation or run
`examples/notebooks/quant_trading/07_native_ssa_high_return_low_drawdown_tutorial.ipynb`
after placing the referenced FX and crypto CSVs under
`examples/quant_trading/data/intraday_crypto_fx/`.

Live-data versions are available through `make quant-columns-03-04-live` and `make quant-columns-05-06-live`.


## Strategy expansion: method-specific variants and component pair trading

The strategy lab now includes an additional expansion layer that treats a decomposition method and horizon as part of the strategy definition.

```bash
make strategy-expansion
```

This command runs:

1. method-specific strategy variants: STL/SSA/STD configurations produce different trend, cycle, and residual inputs for the same trend-following, oscillation-reversion, residual-Bollinger, trend-MACD, and trend-crossover rules;
2. component-level pair trading: both assets in a pair are decomposed, trend/cycle similarity is measured, cointegration and stationarity diagnostics are reported, and the residual gap or trend+cycle spread deviation is traded.

Tutorial document:

```text
docs/tutorials/quant-trading/method-specific-strategy-expansion.md
```

New notebooks:

```text
examples/notebooks/quant_trading/03_detime_method_specific_strategy_variants.ipynb
examples/notebooks/quant_trading/04_detime_component_pair_trading_cointegration.ipynb
```
