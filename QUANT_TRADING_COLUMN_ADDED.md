# Quant Trading Column Integration

This integration replaces the earlier quant trading tutorial column with the
decomposition-first 00-06 sequence.

Changed existing files:

- `mkdocs.yml`: points the Quant Trading Column navigation to the active 00-06 sequence.
- `docs/tutorials/quant-trading.md`: describes the revised decomposition-first path.
- `scripts/check_doc_consistency.py`: checks the active rendered notebook paths.

Added directories:

- `docs/tutorials/quant-trading.md`
- `docs/tutorials/quant-trading/`
- `examples/notebooks/quant_trading/`
- `examples/quant_trading/`

Market data sources:

- The scripts download live OHLCV data at runtime through `yfinance`.
- The rendered notebooks use bundled real Yahoo Finance exports for deterministic rebuilds.
- Returned tables are validated before feature and signal examples are computed.
- Data-source failures are reported as `MarketDataError`.

Local checks performed:

```bash
$env:PYTHONPATH='src;examples'
python examples/quant_trading/scripts/download_real_market_data.py --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD --start 2018-01-01
python examples/quant_trading/scripts/run_columns_01_02.py
python examples/quant_trading/scripts/run_columns_03_04.py
python examples/quant_trading/scripts/run_columns_05_06.py
python examples/quant_trading/scripts/smoke_quant_columns_01_02.py
python examples/quant_trading/scripts/smoke_quant_columns_03_04.py
python examples/quant_trading/scripts/smoke_quant_columns_05_06.py
python scripts/generate_column_notebook_pages.py
python scripts/check_doc_consistency.py
python -m pytest tests/docs/test_generated_method_docs.py -q
python -m mkdocs build --strict
```
