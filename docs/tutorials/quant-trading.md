# Decomposition-First Quant Trading with De-Time

This tutorial column rebuilds the quant-trading examples around one thesis:
classic technical strategies are rough, implicit estimates of trend, cycle,
residual deviation, and market participation. De-Time makes those structures
explicit before the strategy layer.

The revised column uses a six-part path instead of the earlier loose collection
of indicator notebooks.

| Column | Status | Topic | Main De-Time role |
|---|---|---|---|
| 00 | implemented | roadmap | strategy design map |
| 01 | implemented | market data and feature factory | price and volume decomposition |
| 02 | implemented | moving average, multi-MA and MACD | explicit trend filters with cycle, residual and volume gates |
| 03 | implemented | RSI, Bollinger and residual mean reversion | residual deviation, cycle timing and volume filter |
| 04 | implemented | Turtle/Donchian breakout | trend, cycle, residual overextension and volume confirmation |
| 05 | implemented | pairs trading and stat arb | spread trend drift plus spread residual |
| 06 | implemented | cross-sectional rotation | trend/cycle/residual/volume decomposition factor score |

## Implemented notebooks

The executable notebooks are in `examples/notebooks/quant_trading/`:

| Notebook | What it teaches |
|---|---|
| `00_decomposition_first_quant_trading_roadmap.ipynb` | Why the column is organized around decomposition rather than isolated indicators. |
| `01_market_data_and_decomposition_feature_factory.ipynb` | OHLCV audit, period estimation, and walk-forward price/volume feature construction. |
| `02_decomposition_aware_moving_average_macd.ipynb` | Classical buy-and-hold, dual MA, MACD, multi-MA and momentum compared with De-Time rewrites. |
| `03_residual_mean_reversion_rsi_bollinger.ipynb` | Price z-score, RSI, Bollinger and APO baselines rewritten as residual mean reversion with cycle timing. |
| `04_turtle_donchian_breakout_volume_confirmation.ipynb` | Donchian/Turtle breakout rewritten with trend, cycle, residual and volume confirmation. |
| `05_pairs_spread_decomposition_stat_arb.ipynb` | Pair z-score and rolling-beta spread baselines rewritten as residual spread trading with spread-trend drift control. |
| `06_cross_sectional_rotation_portfolio.ipynb` | Momentum, multi-MA and inverse-volatility rotation compared with De-Time cross-sectional scoring. |

Install optional notebook dependencies from `examples/quant_trading/requirements.txt`.
The rendered notebook pages include captured outputs directly, starting with
[Column 01](quant-trading/notebooks/01_market_data_and_decomposition_feature_factory.md).

## Data layer

The code supports live OHLCV downloads through `yfinance`; the experiment
scripts write cache files, manifests and data-audit CSVs under
`examples/quant_trading/`. The notebooks also support archived real GOOG and FX
Yahoo exports from the Learn Algorithmic Trading material so the documentation
can be rebuilt without inventing or simulating market data.

For formal trading research, replace the educational data source with a licensed
point-in-time vendor and document symbol membership, corporate actions,
delistings, borrow, funding, FX and execution assumptions.

## Core design

For price and volume the feature layer uses:

```text
log(P_t) = trend_price_t + cycle_price_t + residual_price_t
log(1 + V_t) = trend_volume_t + cycle_volume_t + residual_volume_t
```

The strategy layer then reads:

| Component | Trading interpretation | Example use |
|---|---|---|
| price trend | direction and persistence | trend-following state, decomposed MA/MACD |
| price cycle | timing and local oscillation | avoid buying into overextended cycle peaks |
| price residual | deviation from current structure | pullback and mean-reversion logic |
| volume trend | participation | confirm trend or breakout |
| volume residual | abnormal activity | detect volume shock or weak participation |
| reconstruction error / stability | feature reliability | reduce exposure when component quality weakens |

## Run the column

```bash
python examples/quant_trading/scripts/download_real_market_data.py \
  --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD \
  --start 2018-01-01
python examples/quant_trading/scripts/run_columns_01_02.py
python examples/quant_trading/scripts/run_columns_03_04.py
python examples/quant_trading/scripts/run_columns_05_06.py
python scripts/generate_column_notebook_pages.py
mkdocs build --strict
```
