# Quant trading decomposition-first rewrite

This pass replaces the earlier indicator-first quant column with a
decomposition-first teaching path.

Implemented notebooks:

1. `00_decomposition_first_quant_trading_roadmap.ipynb`
2. `01_market_data_and_decomposition_feature_factory.ipynb`
3. `02_decomposition_aware_moving_average_macd.ipynb`
4. `03_residual_mean_reversion_rsi_bollinger.ipynb`
5. `04_turtle_donchian_breakout_volume_confirmation.ipynb`
6. `05_pairs_spread_decomposition_stat_arb.ipynb`
7. `06_cross_sectional_rotation_portfolio.ipynb`

Main implementation files:

- `examples/quant_trading/data.py`
- `examples/quant_trading/decomposition_features.py`
- `examples/quant_trading/features.py`
- `examples/quant_trading/classic_indicators.py`
- `examples/quant_trading/strategy_baselines.py`
- `examples/quant_trading/strategy_detime.py`
- `examples/quant_trading/strategy_pairs.py`
- `examples/quant_trading/strategy_rotation.py`
- `examples/quant_trading/validation.py`
- `examples/quant_trading/scripts/download_real_market_data.py`
- `examples/quant_trading/scripts/run_columns_01_02.py`
- `examples/quant_trading/scripts/run_columns_03_04.py`
- `examples/quant_trading/scripts/run_columns_05_06.py`

Real-data execution command:

```bash
python examples/quant_trading/scripts/download_real_market_data.py \
  --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD \
  --start 2018-01-01
python examples/quant_trading/scripts/run_columns_01_02.py
python examples/quant_trading/scripts/run_columns_03_04.py
python examples/quant_trading/scripts/run_columns_05_06.py
```
