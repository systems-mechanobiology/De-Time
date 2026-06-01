# Strategy-lab refactor plan

Problem found: the previous six-column quant tutorial was too broad.  It mapped
many classical indicators to decomposition features, but the trading system was
not obvious enough.  The user requested two explicit strategy families with
real backtests and buy/sell analysis.

## Locked strategy families

### 1. Trend following

Purpose: trade when De-Time says the trend is strong.

Signal source:

```text
trend_slope
trend_strength
```

Filters:

```text
cycle_position          # avoid buying cycle peaks
residual_abs_z          # avoid structural overextension
volume_trend_slope      # participation
volume_residual_z       # abnormal participation
```

### 2. Oscillation / residual reversion

Purpose: trade when trend is weak and price deviates from the decomposed
trend+cycle fair value.

Signal source:

```text
weak_trend = abs(trend_strength) <= threshold
residual_z < -entry_z   # buy / long
residual_z >  entry_z   # sell / short if allowed
```

Exit:

```text
residual_z returns near zero
or trend becomes strong again
```

## Required artifacts

- Signal object with long/short entries and exits.
- Target weights / position sizing.
- Next-bar execution backtest.
- Order ledger.
- Round-trip trade ledger.
- Strategy metrics table.
- Buy/sell chart.
- Real-data smoke run.

## Files implemented

```text
examples/quant_trading/strategy_lab.py
examples/quant_trading/scripts/run_strategy_lab.py
examples/notebooks/quant_trading/01_detime_trend_following_strategy_lab.ipynb
examples/notebooks/quant_trading/02_detime_oscillation_reversion_strategy_lab.ipynb
docs/tutorials/quant-trading/two-strategy-families.md
```
