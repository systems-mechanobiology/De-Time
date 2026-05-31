# Decomposition-first quant column rewrite: Columns 01-02

## Column 01 — Market data and De-Time feature factory

Purpose: build the reusable data and feature layer before any strategy result.

Flow:

1. Load OHLCV from a live Yahoo Finance request or the archived GOOG sample used by the rendered documentation.
2. Write a market-data manifest and OHLCV audit table.
3. Estimate trading-period candidates from recent data instead of hard-coding a single horizon.
4. Decompose close prices into trend, cycle and residual.
5. Decompose volume into volume trend, volume cycle and volume residual.
6. Export a feature table with price, volume and reliability variables.

Main files:

- `examples/quant_trading/data.py`
- `examples/quant_trading/decomposition_features.py`
- `examples/quant_trading/features.py`
- `examples/notebooks/quant_trading/01_real_market_data_and_detime_features.ipynb`
- `examples/quant_trading/scripts/run_columns_01_02.py`

## Column 02 — Moving averages and MACD rewritten with decomposition

Purpose: show that SMA, EMA, multi-MA and MACD are trend estimators, then replace the raw-price estimator with De-Time trend states.

Flow:

1. Reproduce classical baselines: buy-and-hold, SMA 20/100 crossover, MACD, multi-MA stack, 63-day momentum.
2. Run decomposition-aware versions: trend-following, trend + cycle + volume confirmation, MACD on De-Time trend, multi-MA on De-Time trend, trend pullback.
3. Use the same data, same costs and same shifted-position backtester for both groups.
4. Export the comparison table for audit.

Main files:

- `examples/quant_trading/classic_indicators.py`
- `examples/quant_trading/strategy_baselines.py`
- `examples/quant_trading/strategy_detime.py`
- `examples/notebooks/quant_trading/02_single_asset_timing_vectorbt.ipynb`
- `examples/quant_trading/scripts/run_columns_01_02.py`

## Execution

```bash
python -m pip install -r examples/quant_trading/requirements.txt
python examples/quant_trading/scripts/download_real_market_data.py --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD --start 2018-01-01
python examples/quant_trading/scripts/run_columns_01_02.py --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD --start 2018-01-01
```

For the archived GOOG documentation path:

```bash
python examples/quant_trading/scripts/run_columns_01_02.py --use-bundled-sample
```
