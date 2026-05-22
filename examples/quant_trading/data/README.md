# Quant trading data directory

The notebooks download real market data at runtime through `yfinance` and can
cache CSV files here if `cache_dir="examples/quant_trading/data/cache"` is
passed to the loader.

No generated price series is stored in this tutorial. If the vendor request
fails, the tutorial should stop with an explicit `MarketDataError`.

For production research, replace Yahoo Finance with a licensed data source and
record the vendor, timestamp, adjustment policy, calendar, corporate-action
logic, and data-quality checks in the dataset passport.
