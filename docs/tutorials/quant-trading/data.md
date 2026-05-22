# Quant Trading Data: Sources and Validation

The quant trading column downloads market data at runtime and validates the
returned tables before feature and signal examples are computed.

## Default source

The default source is Yahoo Finance through `yfinance`:

```python
from examples.quant_trading.data import fetch_yahoo_prices

prices = fetch_yahoo_prices(
    ["AAPL", "MSFT", "NVDA", "005930.KS", "000660.KS", "BTC-USD", "ETH-USD"],
    start="2018-01-01",
    interval="1d",
    cache_dir="examples/quant_trading/data/cache",
)
```

The loader validates that the returned panel is non-empty, contains requested
tickers, has enough observations, and does not consist of all-missing columns.

## Example universes

| Universe | Examples | Use |
|---|---|---|
| US large cap | `AAPL`, `MSFT`, `NVDA`, `AMZN`, `META` | stock timing and cross-sectional ranking |
| US style ETFs | `SPY`, `QQQ`, `IWM`, `MTUM`, `QUAL`, `VLUE` | style rotation |
| US sector ETFs | `XLK`, `XLF`, `XLE`, `XLV`, `XLY` | sector rotation |
| Korea equities | `005930.KS`, `000660.KS`, `035420.KS` | Korea market examples |
| Crypto pairs | `BTC-USD`, `ETH-USD`, `SOL-USD` | 24/7 regime examples |

## Data audit

```python
from examples.quant_trading.data import data_audit_report

audit = data_audit_report(prices)
print(audit)
```

The audit report records the first and last timestamps, observation count,
missing ratio, and price range for each asset.

Rendered notebook transcript with code and output:
[01 real market data and De-Time features](notebooks/01_real_market_data_and_detime_features.md)

## Production replacement

For production research, replace the tutorial source with a licensed data vendor
and document:

- adjusted versus unadjusted prices;
- split and dividend policy;
- point-in-time symbol membership;
- trading calendar and timezone;
- delisting handling;
- FX conversion;
- borrow, funding, and execution assumptions.
