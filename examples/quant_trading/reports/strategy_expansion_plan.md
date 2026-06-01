# Strategy Expansion Plan

This expansion keeps the previous two-family design and adds two tutorial blocks.

## Block A: method-specific strategy variants

Goal: show that each decomposition method and horizon creates a distinct strategy because it produces distinct trend, cycle, and residual components.

Implemented strategy variants:

- trend following from decomposed trend
- oscillation reversion from residual z-score
- hybrid regime switch
- residual Bollinger bands around trend+cycle fair value
- MACD on decomposed trend
- dual-EMA crossover on decomposed trend

The script runs the same rule family under multiple method/period/window specifications and records stats, orders, trades, feature coverage, and failed methods.

## Block B: decomposition-first pair trading

Goal: show pair trading as component relationship trading, not just raw spread z-score trading.

Implemented steps:

- decompose both assets in each pair
- measure trend correlation and cycle correlation
- test raw-price cointegration with Engle-Granger
- test spread stationarity with ADF
- trade residual gaps or deviations from the trend+cycle fair-value relationship
- run a full next-bar backtest with orders and round-trip trades

## Execution

```bash
make strategy-expansion
```

Outputs are stored in:

```text
examples/quant_trading/reports/strategy_expansion/
```
