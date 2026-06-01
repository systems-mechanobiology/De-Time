# Quant Trading Decomposition-First Rewrite

This pass extends the earlier columns 01-02 rewrite into the current
decomposition-first quant trading column.

Implemented notebooks:

1. `00_decomposition_first_quant_trading_roadmap.ipynb`
2. `01_market_data_and_decomposition_feature_factory.ipynb`
3. `02_decomposition_aware_moving_average_macd.ipynb`
4. `03_residual_mean_reversion_rsi_bollinger.ipynb`
5. `04_turtle_donchian_breakout_volume_confirmation.ipynb`
6. `05_pairs_spread_decomposition_stat_arb.ipynb`
7. `06_cross_sectional_rotation_portfolio.ipynb`

Additional strategy-lab notebooks:

- `01_detime_trend_following_strategy_lab.ipynb`
- `02_detime_oscillation_reversion_strategy_lab.ipynb`
- `03_detime_method_specific_strategy_variants.ipynb`
- `04_detime_component_pair_trading_cointegration.ipynb`

Main implementation files:

- `examples/quant_trading/data.py`
- `examples/quant_trading/decomposition_features.py`
- `examples/quant_trading/features.py`
- `examples/quant_trading/classic_indicators.py`
- `examples/quant_trading/strategy_baselines.py`
- `examples/quant_trading/strategy_detime.py`
- `examples/quant_trading/strategy_lab.py`
- `examples/quant_trading/strategy_method_variants.py`
- `examples/quant_trading/strategy_component_pairs.py`
- `examples/quant_trading/strategy_pairs.py`
- `examples/quant_trading/strategy_rotation.py`
- `examples/quant_trading/validation.py`

Runner scripts:

- `examples/quant_trading/scripts/download_real_market_data.py`
- `examples/quant_trading/scripts/run_columns_01_02.py`
- `examples/quant_trading/scripts/run_columns_03_04.py`
- `examples/quant_trading/scripts/run_columns_05_06.py`
- `examples/quant_trading/scripts/run_strategy_lab.py`
- `examples/quant_trading/scripts/run_strategy_expansion.py`

Real-data execution summary:

- Yahoo Finance OHLCV cache was downloaded for SPY, QQQ, AAPL, MSFT, NVDA, XLK, XLE, TLT, GLD, KO, PEP, XOM, CVX, MA and V.
- Columns 01-04 were rerun on the downloaded live data panel.
- Columns 05-06 were rerun on bundled real FX samples.
- Strategy lab and strategy expansion were rerun on bundled real samples and live SPY/equity-pair data.
- All quant notebooks were executed and rendered into documentation pages with 31 generated PNG outputs.
