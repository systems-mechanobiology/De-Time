# Strategy Map: Where Trend, Cycle, and Residual Help

De-Time is not a trading strategy by itself. It is a feature layer. The column
shows how decomposition outputs can be routed into common quantitative strategy
families.

| Strategy family | Classical version | De-Time feature use | Tutorial |
|---|---|---|---|
| Single-asset timing | moving-average crossover | trend direction and residual pullback | [02 single-asset timing](notebooks/02_single_asset_timing_vectorbt.md) |
| Turtle / Donchian | breakout above prior high | require positive `trend_slope` before breakout entries | [03 Turtle Donchian trend filter](notebooks/03_turtle_donchian_trend_filter.md) |
| Residual mean reversion | price z-score | z-score of `residual`, not raw price | [02 single-asset timing](notebooks/02_single_asset_timing_vectorbt.md) |
| Pairs trading | spread z-score | decompose spread; avoid trades when spread trend drifts | [04 pairs trading residual cycle](notebooks/04_pairs_trading_residual_cycle.md) |
| Cross-sectional factors | momentum rank | rank trend strength, negative residual z-score, and cycle slope | [05 cross-sectional factor selection](notebooks/05_cross_sectional_factor_selection.md) |
| Style / sector rotation | ETF momentum | top-N decomposition score plus volatility target | [06 style and sector rotation](notebooks/06_style_sector_asset_rotation_bt.md) |
| Crypto regime | volatility and moving average filter | 24/7 trend and residual-stress gate | [07 Korea, US, and crypto](notebooks/07_korea_us_crypto_multimarket.md) |
| Risk overlay | stop loss | reduce exposure when residual stress is extreme | all strategy notebooks |

## Signal principles

1. Trend sets direction.
2. Cycle sets timing.
3. Residual measures deviation from the modeled structure.
4. Residual spikes and reconstruction error are reliability warnings.
5. Every signal must be computed walk-forward before it is backtested.

## Example: trend pullback

```python
features = walkforward_decompose(prices, method="STL", period=63)
entries, exits = trend_pullback_signals(
    prices,
    features,
    residual_entry_z=-1.0,
    residual_exit_z=0.25,
    min_trend_slope=0.0,
)
```

## Example: pair spread residual

```python
weights = pair_trading_weights(
    prices["KO"],
    prices["PEP"],
    lookback=120,
    entry_z=1.5,
    exit_z=0.25,
)
```

Before using this in research, decompose the spread walk-forward and use the
spread residual only when the spread trend is not drifting strongly.
