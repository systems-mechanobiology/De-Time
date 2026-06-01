# De-Time Quant Strategy Lab: Two Concrete Strategy Families

This page replaces the loose indicator-first reading of the quant notebooks with
two complete trading systems. Each system has signal generation, position
sizing, a next-bar backtest, order records, round-trip trades, and buy/sell
charts.

## 1. Trend-Following Strategy

Use this when the decomposed trend is strong.

Model:

```text
log(price) = trend + cycle + residual
```

Trading logic:

```text
long_entry =
    trend_slope > 0
    and trend_strength > entry_threshold
    and cycle_position is not already too high
    and abs(residual_z) is not overextended
    and volume participation is acceptable

long_exit =
    trend_slope turns negative
    or trend_strength falls below exit_threshold
    or abs(residual_z) becomes a stress event
```

The trend creates the signal. Cycle and residual do not replace the signal;
they control timing and overextension. Volume decomposition is used as a
participation filter, not as a raw-volume threshold.

## 2. Oscillation / Residual-Reversion Strategy

Use this when the decomposed trend is weak.

Trading logic:

```text
weak_trend = abs(trend_strength) <= max_abs_trend_strength
fair_value = exp(trend + cycle)

long_entry = weak_trend and residual_z <= -entry_z
long_exit  = residual_z >= -exit_z or not weak_trend

short_entry = weak_trend and residual_z >= entry_z
short_exit  = residual_z <= exit_z or not weak_trend
```

Here the traded object is the residual after removing the current trend and
cycle. A negative residual means price is temporarily below its current
structural value; a positive residual means price is temporarily above it.

## What the Script Writes

```text
examples/quant_trading/reports/strategy_lab/
- strategy_lab_strategy_stats.csv
- strategy_lab_orders.csv
- strategy_lab_trades.csv
- strategy_lab_feature_snapshot.csv
- strategy_lab_feature_coverage.csv
- strategy_lab_run_manifest.json
- charts/
```

## Local Run

```bash
make strategy-lab
```

or directly:

```bash
python examples/quant_trading/scripts/run_strategy_lab.py \
  --use-bundled-sample \
  --methods STL \
  --period 42 \
  --train-window 180 \
  --step 21 \
  --allow-short-reversion
```

## Live Yahoo Finance Run

```bash
make strategy-lab-live
```

or directly:

```bash
python examples/quant_trading/scripts/run_strategy_lab.py \
  --ticker SPY \
  --start 2018-01-01 \
  --methods STL SSA \
  --period 63 \
  --train-window 252 \
  --step 21
```

## User CSV Run

A user CSV must contain at least:

```text
Open, High, Low, Close, Volume
```

Example:

```bash
python examples/quant_trading/scripts/run_strategy_lab.py \
  --csv path/to/BUSD_30m.csv \
  --ticker BUSD \
  --period 48 \
  --periods-per-year 17520 \
  --methods STL SSA \
  --allow-short-reversion
```

For 30-minute crypto data, `periods-per-year` depends on whether the dataset is
24/7. A 24/7 30-minute series has roughly `365 * 48 = 17520` bars per year.

## Notebooks

The two clearest notebooks are:

```text
examples/notebooks/quant_trading/01_detime_trend_following_strategy_lab.ipynb
examples/notebooks/quant_trading/02_detime_oscillation_reversion_strategy_lab.ipynb
```

They are intentionally narrower than the earlier six notebooks. They show the
same structure from signal to trade ledger to performance table.
