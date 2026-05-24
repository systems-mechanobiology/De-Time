# Strategy Selection and Falsification Map

De-Time is a feature layer, not a strategy claim by itself. Each strategy starts
with a hypothesis, a baseline, and a failure mode that would make the result
unusable.

| Strategy family | Hypothesis | Minimum baseline | Failure mode | Tutorial |
|---|---|---|---|---|
| Single-asset timing | trend plus residual timing improves entry quality | buy-and-hold and moving-average timing | underperforms after costs or trades too often | [02 single-asset timing](notebooks/02_single_asset_timing_vectorbt.md) |
| Turtle / Donchian | De-Time trend filter removes weak breakouts | unfiltered Donchian breakout | filter removes winners or adds parameter fragility | [03 Turtle Donchian trend filter](notebooks/03_turtle_donchian_trend_filter.md) |
| Residual mean reversion | modeled residual is cleaner than price z-score | price z-score mean reversion | residual remains directional or cost-sensitive | [02 single-asset timing](notebooks/02_single_asset_timing_vectorbt.md) |
| Pairs trading | spread residual helps avoid trend drift | classical spread z-score pair trade | spread trend persists or hedge ratio is unstable | [04 pairs trading residual cycle](notebooks/04_pairs_trading_residual_cycle.md) |
| Cross-sectional factors | decomposition factor candidates rank assets better than simple momentum | equal-weight, benchmark ETF, momentum-only top-N, random top-N | result depends on mega-cap sample or one regime | [05 cross-sectional factor selection](notebooks/05_cross_sectional_factor_selection.md) |
| Style / sector rotation | decomposition score improves ETF rotation timing | equal-weight sector basket and momentum rotation | turnover or one sector explains the result | [06 style and sector rotation](notebooks/06_style_sector_asset_rotation_bt.md) |
| Crypto regime | 24/7 trend and residual stress identify regime changes | buy-and-hold and volatility filter | calendar mismatch or fees erase the signal | [07 Korea, US, and crypto](notebooks/07_korea_us_crypto_multimarket.md) |
| Risk overlay | residual stress identifies unreliable periods | same strategy without overlay | cuts exposure after losses rather than before them | all strategy notebooks |

## Signal principles

1. Trend sets direction.
2. Cycle sets timing.
3. Residual measures deviation from the modeled structure.
4. Residual spikes and reconstruction error are reliability warnings.
5. Every signal is computed walk-forward before it is backtested.
6. A strategy is rejected when it fails its baseline or data gate.

## Example: trend pullback

```python
features = walkforward_decompose(prices, method="ROBUST_STL", period=63)
entries, exits = trend_pullback_signals(
    prices,
    features,
    residual_entry_z=-1.0,
    residual_exit_z=0.25,
    min_trend_slope=0.0,
)
```

In the notebooks this call is routed through `ROBUST_STL`, which is the default
for market-price examples. Use plain `STL` or faster baselines for sensitivity
checks, not as the headline decomposition.

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

For research use, decompose the spread walk-forward and compare this residual
version with the classical spread z-score baseline over the same dates and
costs.
