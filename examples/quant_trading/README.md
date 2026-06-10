# DeTime Quant Trading Column

This directory contains the decomposition-first quant trading tutorial code. The previous indicator-first sequence has been replaced by a smaller, clearer six-part curriculum. Tutorials 01-06 are implemented.

## Implemented now

1. `01_market_data_and_decomposition_feature_factory.ipynb`
   Real OHLCV data, dataset audit, period estimation, walk-forward price and volume decomposition, and feature coverage reporting.

2. `02_decomposition_aware_moving_average_macd.ipynb`
   Classical buy-and-hold, moving-average, MACD, multi-MA and momentum baselines, then DeTime rewrites that use explicit trend, cycle, residual, and volume features.

3. `03_residual_mean_reversion_rsi_bollinger.ipynb`
   Price z-score, RSI, Bollinger and APO mean-reversion baselines, then DeTime residual mean-reversion variants using residual z-score, residual RSI, residual Bollinger bands, cycle timing and volume filters.

4. `04_turtle_donchian_breakout_volume_confirmation.ipynb`
   Donchian/Turtle breakout baselines, then DeTime breakout rewrites using trend direction, cycle state, residual overextension caps and volume confirmation.

5. `05_pairs_spread_decomposition_stat_arb.ipynb`
   Pair ratio/spread z-score baselines, then DeTime spread-residual trading with spread trend-drift control and optional pair volume/news filters.

6. `06_cross_sectional_rotation_portfolio.ipynb`
   Momentum, multi-MA and inverse-volatility allocation baselines, then DeTime trend/cycle/residual/volume factor scoring and portfolio construction.

## Core modules

- `data.py`: yfinance downloaders, OHLCV panel helpers, and offline real-data GOOG and FX sample loaders for smoke tests.
- `classic_indicators.py`: SMA, EMA, MACD, RSI, Bollinger, Donchian, momentum, APO.
- `decomposition_features.py`: walk-forward DeTime feature factory for price and volume.
- `strategy_baselines.py`: classical strategy weights for trend, mean-reversion and breakout families.
- `strategy_detime.py`: decomposition-aware trend, residual mean-reversion and breakout recipes.
- `strategy_pairs.py`: pair spread decomposition, residual-stat-arb and pair diagnostics.
- `strategy_rotation.py`: cross-sectional rotation, DeTime factor scores and portfolio construction.
- `validation.py`: common backtest comparison, turnover reporting, and run manifest helpers.
- `backtest.py`: transparent vectorized research backtester.

## Smoke tests

```bash
python -m pip install -e .
export PYTHONPATH="$PWD/src:$PWD/examples:$PYTHONPATH"
make smoke
```

Run only the latest batch:

```bash
make smoke-05-06
make quant-columns-05-06
```

Run all implemented columns:

```bash
make quant-columns-01-06
```

Tutorials 01-04 smoke tests use the bundled historical GOOG OHLCV sample. Tutorials 05-06 smoke tests use bundled historical FX samples. They do not generate artificial prices.

## Live data usage

```bash
python examples/quant_trading/scripts/download_real_market_data.py \
  --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD \
  --start 2018-01-01

python examples/quant_trading/scripts/run_column_03_residual_mean_reversion.py \
  --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD \
  --start 2018-01-01

python examples/quant_trading/scripts/run_column_04_breakout_volume_confirmation.py \
  --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD \
  --start 2018-01-01

python examples/quant_trading/scripts/run_column_05_pairs_spread_decomposition.py \
  --tickers KO PEP XOM CVX MA V SPY QQQ \
  --pairs KO:PEP XOM:CVX MA:V SPY:QQQ \
  --start 2018-01-01

python examples/quant_trading/scripts/run_column_06_cross_sectional_rotation.py \
  --tickers XLK XLF XLE XLV XLY XLP XLI XLU XLB XLRE XLC \
  --start 2018-01-01
```

```python
from quant_trading.data import fetch_yahoo_ohlcv

ohlcv = fetch_yahoo_ohlcv("SPY", start="2016-01-01", cache_dir="examples/quant_trading/data/cache")
```

For production research, replace Yahoo Finance with licensed point-in-time data and document symbol membership, corporate actions, delistings, borrow, funding, FX, and execution assumptions.

## Concrete strategy lab

The recommended entry point is now `strategy_lab.py`.  It contains two complete decomposition-based strategy families rather than a loose collection of indicator examples:

- `decomposition_trend_following_signals`: uses `trend_slope` and `trend_strength` to enter trend-following trades, with cycle/residual/volume filters.
- `decomposition_oscillation_reversion_signals`: trades residual deviation only when the trend is weak; negative residual buys, positive residual sells or shorts.

Run:

```bash
make strategy-lab
```

Outputs are written to `examples/quant_trading/reports/strategy_lab/` and include strategy statistics, orders, round-trip trades, run manifest and buy/sell charts.

## Strategy expansion: method-specific variants and component pair trading

The strategy lab now has an additional expansion layer:

```bash
make strategy-expansion
```

This runs two English-language tutorial blocks:

1. **Method-specific decomposition strategies**: the same trend-following, residual-reversion, residual-Bollinger, trend-MACD, and trend-crossover logic is run under different decomposition methods and horizons. Each method/period/window combination is treated as a distinct strategy because it produces different trend, cycle, and residual components.
2. **Component-level pair trading**: pairs are decomposed asset-by-asset, trend/cycle similarity is measured, cointegration and stationarity diagnostics are reported, and residual gaps are traded with a full next-bar backtest.

Main files:

```text
examples/quant_trading/strategy_method_variants.py
examples/quant_trading/strategy_component_pairs.py
examples/quant_trading/scripts/run_strategy_expansion.py
docs/tutorials/quant-trading/method-specific-strategy-expansion.md
```

Main outputs:

```text
examples/quant_trading/reports/strategy_expansion/method_variant_strategy_stats.csv
examples/quant_trading/reports/strategy_expansion/component_pair_strategy_stats.csv
examples/quant_trading/reports/strategy_expansion/component_pair_diagnostics.csv
examples/quant_trading/reports/strategy_expansion/*_orders.csv
examples/quant_trading/reports/strategy_expansion/*_trades.csv
```
