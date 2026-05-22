# De-Time Quant Trading Column

This directory contains the example code behind the documentation page
`docs/tutorials/quant-trading.md`.

The column is designed for international quant readers. It downloads market
data through `yfinance` by default, validates returned tables, and records the
ticker universe, date window, and data source used by each notebook.

## Quick start

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/quant_trading/requirements.txt
jupyter lab examples/notebooks/quant_trading
```

## What is included

- `data.py`: real-market data loading and audit helpers.
- `features.py`: walk-forward De-Time feature factory.
- `signals.py`: timing, pairs, rotation, and risk-filter signal recipes.
- `backtest.py`: transparent vectorized research backtester.
- `frameworks.py`: optional adapters for vectorbt, backtesting.py, bt, Backtrader, Zipline-Reloaded, and QuantStats.
- `reports/`: strategy maps, framework matrix, and data/metric passports.
