# Tutorial 01: Real Data and DeTime Feature Factory

Tutorial 01 builds the reusable data and feature layer for the series.

## Live data path

```python
from quant_trading.data import fetch_yahoo_ohlcv

ohlcv = fetch_yahoo_ohlcv("SPY", start="2016-01-01")
```

## Offline real-data smoke path

```python
from quant_trading.data import load_sample_goog_ohlcv

ohlcv = load_sample_goog_ohlcv(trim_start="2010-01-01")
```

The bundled fallback is real historical GOOG OHLCV data from the uploaded Learn
Algorithmic Trading archive.  It is included so the notebooks and smoke tests run
without network access.  It is not a substitute for a licensed research data
vendor.

## Feature factory

```python
from quant_trading.decomposition_features import walkforward_price_volume_features

prices = ohlcv[["Close"]].rename(columns={"Close": "SPY"})
volumes = ohlcv[["Volume"]].rename(columns={"Volume": "SPY"})

features = walkforward_price_volume_features(
    prices,
    volumes,
    method="STL",
    period=63,
    train_window=252,
    step=21,
)
```

Returned feature names include:

| Feature | Meaning |
|---|---|
| `trend`, `trend_slope`, `trend_strength` | price direction and persistence |
| `cycle`, `cycle_slope`, `cycle_z`, `cycle_amplitude` | oscillatory timing and amplitude |
| `residual_z`, `residual_abs_z`, `residual_vol` | structural deviation and stress |
| `volume_trend_slope`, `volume_residual_z`, `volume_participation` | participation and abnormal activity |
| `component_stability`, `reconstruction_error` | reliability screens |

Executable notebook:
`examples/notebooks/quant_trading/01_market_data_and_decomposition_feature_factory.ipynb`.
