# De-Time Quant Trading Column

This directory contains the example code behind the documentation page
`docs/tutorials/quant-trading.md`.

The column is designed for international quant readers. It uses real market data
through `yfinance` by default and raises an explicit error if the data vendor is
unavailable. It does not create artificial price data.

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
