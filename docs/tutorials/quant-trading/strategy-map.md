# Strategy Map: From Classic Indicators to Decomposition-Aware Signals

The revised column does not only improve Bollinger bands. It rewrites several
classic strategy families by asking what each indicator was trying to estimate.

| Strategy family | Classical version | De-Time rewrite | Status |
|---|---|---|---|
| Feature layer | raw close and raw volume | walk-forward price + volume decomposition | implemented in Column 01 |
| Dual moving average | fast SMA > slow SMA on price | fast/slow average on extracted trend, gated by residual and volume | implemented in Column 02 |
| MACD | fast EMA - slow EMA on price | MACD on extracted trend, gated by cycle, residual and volume | implemented in Column 02 |
| Multi-MA alignment | several raw moving averages aligned | trend state + residual stress + participation filter | implemented in Column 02 |
| Trend pullback | buy dip in an uptrend | trend intact + residual cheap + volume confirmation | implemented in Column 02 |
| RSI / Bollinger / price z-score | overbought/oversold on raw price | residual z-score, residual RSI and residual bands with cycle timing | implemented in Column 03 |
| Turtle / Donchian | breakout above prior high | breakout + trend + cycle + residual-overextension + volume confirmation | implemented in Column 04 |
| Pairs trading | spread z-score | decompose spread; trade residual only when spread trend is stable and pair volume/news state is acceptable | implemented Column 05 |
| Rotation | momentum rank | cross-sectional trend/cycle/residual/volume score with volatility targeting | implemented Column 06 |

## Implemented examples

```python
from quant_trading.strategy_baselines import make_classic_baseline_weight_grid
from quant_trading.strategy_detime import make_detime_trend_weight_grid

classic_trend = make_classic_baseline_weight_grid(prices)
detime_trend = make_detime_trend_weight_grid(prices, features)
```

```python
from quant_trading.strategy_mean_reversion import (
    make_classic_mean_reversion_weight_grid,
    make_detime_mean_reversion_weight_grid,
)

classic_reversion = make_classic_mean_reversion_weight_grid(prices)
detime_reversion = make_detime_mean_reversion_weight_grid(prices, features)
```

```python
from quant_trading.strategy_breakout import (
    make_classic_breakout_weight_grid,
    make_detime_breakout_weight_grid,
)

classic_breakout = make_classic_breakout_weight_grid(ohlcv)
detime_breakout = make_detime_breakout_weight_grid(ohlcv, features)
```

Executable notebooks:

- `examples/notebooks/quant_trading/02_decomposition_aware_moving_average_macd.ipynb`
- `examples/notebooks/quant_trading/03_residual_mean_reversion_rsi_bollinger.ipynb`
- `examples/notebooks/quant_trading/04_turtle_donchian_breakout_volume_confirmation.ipynb`


```python
from quant_trading.strategy_pairs import (
    walkforward_pair_spread_features,
    make_classic_pair_weight_grid,
    make_detime_pair_weight_grid,
)

pairs = [("KO", "PEP"), ("XOM", "CVX")]
spread_features, spread_panel, beta_panel, pair_specs = walkforward_pair_spread_features(prices, pairs)
classic_pairs = make_classic_pair_weight_grid(prices, pair_specs)
detime_pairs = make_detime_pair_weight_grid(
    prices, pair_specs, spread_features, spread_panel=spread_panel, beta_panel=beta_panel
)
```

```python
from quant_trading.strategy_rotation import (
    make_classic_rotation_weight_grid,
    make_detime_rotation_weight_grid,
)

classic_rotation = make_classic_rotation_weight_grid(prices)
detime_rotation = make_detime_rotation_weight_grid(prices, features)
```

Additional executable notebooks:

- `examples/notebooks/quant_trading/05_pairs_spread_decomposition_stat_arb.ipynb`
- `examples/notebooks/quant_trading/06_cross_sectional_rotation_portfolio.ipynb`
