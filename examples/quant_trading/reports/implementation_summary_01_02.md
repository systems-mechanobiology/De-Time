# Implementation summary: decomposition-first quant columns 01-02

## Scope

This implementation replaces the early quant-trading tutorial material with the first two decomposition-first columns:

1. Column 01: real-market data loading, data audit, period selection, price-volume decomposition, and feature factory.
2. Column 02: classical SMA, multi-MA, MACD, and momentum baselines rewritten as decomposition-aware trend/cycle/residual/volume strategies.

## Main code assets

- `examples/quant_trading/data.py`
- `examples/quant_trading/classic_indicators.py`
- `examples/quant_trading/decomposition_features.py`
- `examples/quant_trading/features.py`
- `examples/quant_trading/strategy_baselines.py`
- `examples/quant_trading/strategy_detime.py`
- `examples/quant_trading/validation.py`
- `examples/quant_trading/scripts/run_columns_01_02.py`
- `examples/quant_trading/scripts/smoke_quant_columns_01_02.py`

## Tutorial notebooks

- `examples/notebooks/quant_trading/01_market_data_and_decomposition_feature_factory.ipynb`
- `examples/notebooks/quant_trading/02_decomposition_aware_moving_average_macd.ipynb`

## Offline real-data sample

The offline smoke-test data are archived real GOOG OHLCV bars and FX Yahoo Finance exports copied from the uploaded `Learn-Algorithmic-Trading-master.zip` material. The tutorials do not use synthetic market prices as fallback evidence.

## Executed validation

- `python examples/quant_trading/scripts/smoke_quant_columns_01_02.py`
- `examples/quant_trading/scripts/local/run_columns_01_02_smoke.sh`
- `python examples/quant_trading/scripts/run_columns_01_02.py --use-bundled-sample`
- `pytest -q tests/cli/test_cli.py tests/core/test_machine_interfaces.py tests/wrappers/test_wrappers.py`

The notebooks' code cells were also executed directly through a Python runner in this environment. Full Jupyter `nbclient` execution was not used as the sandbox's Jupyter/ZMQ kernel timed out.

## Boundary

The included reports are tutorial/smoke evidence, not production trading evidence. Full benchmark claims require live or licensed point-in-time data, multi-asset runs, cost sensitivity, seed-free deterministic configuration logs, and the full audit protocol.
