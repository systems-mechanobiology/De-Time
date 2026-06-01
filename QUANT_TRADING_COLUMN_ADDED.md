# Quant Trading Column Integration

This integration replaces the quant trading tutorial column with the
decomposition-first 00-06 sequence, the two-family strategy lab, and the
method-specific strategy expansion.

Changed existing files:

- `mkdocs.yml`: points the Quant Trading Column navigation to the active 00-06 sequence plus strategy-lab and strategy-expansion pages.
- `docs/tutorials/quant-trading.md`: describes the revised decomposition-first path and rendered notebook pages.
- `scripts/check_doc_consistency.py`: checks the active rendered notebook paths.
- `tests/docs/test_generated_method_docs.py`: validates rendered notebook outputs and generated image assets.

Added or refreshed directories:

- `examples/quant_trading/`: reusable data, feature, strategy, validation, and runner code.
- `examples/notebooks/quant_trading/`: executed tutorial notebooks with committed outputs.
- `docs/tutorials/quant-trading/`: tutorial pages and rendered notebook transcripts.
- `docs/assets/generated/notebooks/columns/quant-trading/`: generated notebook PNG outputs.

Market data sources:

- Live OHLCV data is downloaded through `yfinance` into `examples/quant_trading/data/cache`.
- Rendered notebooks use bundled real GOOG and FX samples for deterministic rebuilds without network access.
- Strategy-lab and strategy-expansion live runs were also executed for SPY and selected equity pairs.

Local checks performed:

```bash
python examples/quant_trading/scripts/download_real_market_data.py --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD KO PEP XOM CVX MA V --start 2018-01-01 --allow-partial
python examples/quant_trading/scripts/run_columns_01_02.py --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD --start 2018-01-01
python examples/quant_trading/scripts/run_columns_03_04.py --tickers SPY QQQ AAPL MSFT NVDA XLK XLE TLT GLD --start 2018-01-01
python examples/quant_trading/scripts/run_columns_05_06.py --use-bundled-sample
python examples/quant_trading/scripts/run_strategy_lab.py --use-bundled-sample
python examples/quant_trading/scripts/run_strategy_expansion.py --use-bundled-sample
python scripts/generate_column_notebook_pages.py
python -m mkdocs build --strict
python scripts/check_doc_consistency.py
python -m pytest tests/docs/test_generated_method_docs.py -q
python examples/quant_trading/scripts/smoke_quant_columns_01_02.py
python examples/quant_trading/scripts/smoke_quant_columns_03_04.py
python examples/quant_trading/scripts/smoke_quant_columns_05_06.py
```
