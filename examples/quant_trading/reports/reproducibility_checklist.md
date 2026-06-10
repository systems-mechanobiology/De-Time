# Reproducibility Checklist: DeTime Quant Trading Columns

- [x] Real market data loader: `fetch_yahoo_ohlcv`, `fetch_yahoo_prices`.
- [x] Offline real-data fallback for smoke tests: bundled historical GOOG OHLCV CSV.
- [x] No synthetic price fallback in production loaders.
- [x] Classical baseline implementations separated from DeTime strategies.
- [x] Walk-forward feature factory emits only the last row of each training window.
- [x] Backtest positions are shifted by one bar.
- [x] Fee and slippage assumptions are explicit.
- [x] Dataset, metric, baseline, experiment, and strategy passports are present.
- [x] Hardware probe script is present.
- [x] Smoke script for columns 01-02 is present.
- [ ] Live yfinance download was not executed in this offline environment.
- [ ] Full multi-asset benchmark for columns 03-06 remains unimplemented.
- [ ] Production-grade broker/execution model is not included.
