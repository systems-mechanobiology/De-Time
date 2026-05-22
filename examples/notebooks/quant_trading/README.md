# De-Time Quant Trading Notebooks

These notebooks are the executable companion for `docs/tutorials/quant-trading.md`.
They download market data at runtime through `yfinance`, validate returned
tables, and report data-source failures as `MarketDataError`.

Install optional dependencies:

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/quant_trading/requirements.txt
```

Open the notebooks:

```bash
jupyter lab examples/notebooks/quant_trading
```
