# DeTime Method-Specific Strategy Expansion

This tutorial layer extends the two core strategy families already implemented in the strategy lab:

1. **Trend following**: trade when the decomposed trend is strong enough to define a directional regime.
2. **Oscillation reversion**: trade when the decomposed trend is weak and the residual becomes the tradable deviation.

The new point is that the decomposition method and decomposition horizon are not neutral implementation details. They create different trend, cycle, and residual estimates, and therefore create different strategies.

## 1. Why different decomposition methods create different strategies

A raw moving-average strategy changes when the moving-average length changes. A decomposition strategy changes when any of these choices change:

- the decomposition method: STL, SSA, STD, Wavelet, EMD, VMD, etc.;
- the decomposition period: short cycle, medium cycle, long cycle;
- the walk-forward training window;
- the recomputation step;
- the residual z-score window;
- volume decomposition and liquidity filters.

The same trading rule can be held fixed:

```text
enter long if trend_slope > 0 and trend_strength is high
enter reversion if residual_z is too negative in a weak-trend regime
```

but if STL and SSA extract different trends and cycles, then the entry dates, exits, position sizes, and backtest results are different. The tutorial therefore treats each method-horizon combination as a separate strategy variant.

## 2. Method selection guide

| Method | Trading interpretation | Useful default | Main risk |
|---|---|---|---|
| STL | fixed-period seasonal-trend split | stable daily/weekly/monthly rhythm | phase errors when the cycle drifts |
| SSA | low-rank Hankel subspace split | smoother quasi-periodic financial cycles | leakage under abrupt breaks |
| STD | seasonal-trend-dispersion split | when volatility/dispersion matters | may be conservative on entry signals |
| Wavelet | multi-scale local split | local regime changes and multi-scale cycles | requires PyWavelets and scale tuning |
| EMD/CEEMDAN | adaptive intrinsic oscillatory modes | non-stationary amplitude/frequency cycles | mode mixing |
| VMD | narrow-band spectral modes | compact frequency bands | sensitive to K and alpha |

## 3. Parameter tuning logic

The tutorial avoids blind optimization first. It uses interpretable grids:

| Market idea | DeTime parameter | Example |
|---|---|---|
| short trading rhythm | period | 21 bars |
| medium swing rhythm | period | 42 or 63 bars |
| long trend structure | train_window | 252 bars |
| fast adaptation | step | 5 or 21 bars |
| low turnover | step | 63 or 126 bars |
| residual band sensitivity | z_window | 42, 63, 126 bars |

A practical workflow is:

1. Start with `STL`, `SSA`, and `STD` on periods `21`, `42`, and `63`.
2. Compare strategy families, not only decomposition plots.
3. Check orders, round-trip trades, drawdown, turnover, and exposure.
4. Add Wavelet only after installing PyWavelets.
5. Treat the best variant as a hypothesis, not as proof of alpha.

## 4. Strategy variants now implemented

The module `examples/quant_trading/strategy_method_variants.py` implements:

- `decomposition_trend_following_signals`
- `decomposition_oscillation_reversion_signals`
- `decomposition_residual_bollinger_signals`
- `decomposition_macd_trend_signals`
- `decomposition_trend_crossover_signals`
- `run_method_variant_grid`

The residual Bollinger strategy replaces raw-price bands with residual bands around `trend + cycle` fair value. The trend MACD strategy computes MACD on the decomposed trend instead of raw price. The trend crossover strategy computes fast/slow EMAs on the decomposed trend.

## 5. Component-level pair trading

The module `examples/quant_trading/strategy_component_pairs.py` implements decomposition-first pair trading.

The logic is:

```text
1. Decompose both assets.
2. Check whether their trends are similar.
3. Check whether their cycles are similar.
4. Use Engle-Granger and ADF diagnostics on raw price, fair value, and spread residuals.
5. Trade the residual gap or the deviation from the trend+cycle relationship.
```

Implemented pair strategies:

- `classic_pair_spread_zscore`
- `detime_<method>_component_residual_gap`
- `detime_<method>_fair_spread_deviation`
- `detime_<method>_cointegration_filtered_residual_gap`

The pair-trading tutorial is not only about whether two raw prices are cointegrated. It also asks whether the decomposed components support the pair hypothesis:

```text
trend_left ~ trend_right
cycle_left ~ cycle_right
residual_left - residual_right is the traded gap
```

## 6. Commands

Offline real-data smoke run:

```bash
make strategy-expansion
```

Live Yahoo Finance run:

```bash
make strategy-expansion-live
```

Direct custom run:

```bash
python examples/quant_trading/scripts/run_strategy_expansion.py \
  --use-bundled-sample \
  --variant-grid custom \
  --methods STL SSA STD \
  --periods 21 42 63 \
  --train-window 180 \
  --step 21 \
  --pair-method STL \
  --pair-period 42
```

## 7. Output files

The script writes:

```text
examples/quant_trading/reports/strategy_expansion/method_variant_strategy_stats.csv
examples/quant_trading/reports/strategy_expansion/method_variant_orders.csv
examples/quant_trading/reports/strategy_expansion/method_variant_trades.csv
examples/quant_trading/reports/strategy_expansion/method_variant_spec_grid.csv
examples/quant_trading/reports/strategy_expansion/method_variant_feature_coverage.csv
examples/quant_trading/reports/strategy_expansion/method_variant_failed_methods.csv
examples/quant_trading/reports/strategy_expansion/component_pair_strategy_stats.csv
examples/quant_trading/reports/strategy_expansion/component_pair_diagnostics.csv
examples/quant_trading/reports/strategy_expansion/component_pair_orders.csv
examples/quant_trading/reports/strategy_expansion/component_pair_trades.csv
examples/quant_trading/reports/strategy_expansion/strategy_expansion_run_manifest.json
```

Smoke outputs are tutorial evidence that the pipeline runs. They are not production trading claims.
