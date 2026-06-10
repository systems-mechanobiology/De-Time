# Strategy-lab implementation summary

This refactor adds a concrete DeTime trading tutorial layer focused on two
strategy families: trend following and oscillation/residual reversion.

## Implemented modules

```text
examples/quant_trading/strategy_lab.py
examples/quant_trading/scripts/run_strategy_lab.py
```

## Implemented notebooks

```text
examples/notebooks/quant_trading/01_detime_trend_following_strategy_lab.ipynb
examples/notebooks/quant_trading/02_detime_oscillation_reversion_strategy_lab.ipynb
```

## Backtest model

Signals are generated after bar `t`.  Orders are filled at the next available
open.  If Open is unavailable, Close is used as a proxy.  Transaction costs use:

```text
cost = turnover * (fee_bps + slippage_bps) / 10000
```

The implementation writes:

```text
strategy_lab_strategy_stats.csv
strategy_lab_orders.csv
strategy_lab_trades.csv
strategy_lab_feature_snapshot.csv
strategy_lab_feature_coverage.csv
strategy_lab_run_manifest.json
charts/*.png
```

## Real data

The offline smoke run uses archived real GOOG OHLCV data from the bundled
Learn Algorithmic Trading material.  Live runs are supported through yfinance,
and user CSVs are supported for private intraday crypto or equity bars.

## Privacy note

The two newly uploaded private notebooks were not copied into the package.  The
implementation uses the general trading ideas requested by the user: buy/sell
point analysis, residual reversion, trend following, and real backtesting.
