# De-Time Quant Trading Notebooks

These notebooks are the executable companion for `docs/tutorials/quant-trading.md`.
They use real market data downloaded at runtime through `yfinance`. No artificial
price series is generated. If the data source is unavailable, the notebooks stop
with a `MarketDataError`.

Install optional dependencies:

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/quant_trading/requirements.txt
```

Open the notebooks:

```bash
jupyter lab examples/notebooks/quant_trading
```
