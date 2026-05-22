# Backtesting Frameworks for the Quant Trading Column

The notebooks start with a transparent pandas backtester so readers can inspect
signal alignment, position shifting, transaction costs, turnover, and equity
construction. The same signals can then be routed to established Python
backtesting and reporting packages.

| Framework | Column use | Adapter |
|---|---|---|
| pandas vectorized baseline | transparent close-to-close research checks | `examples/quant_trading/backtest.py` |
| vectorbt | multi-asset signal matrices and parameter grids | `run_vectorbt_from_signals` |
| backtesting.py | single-asset strategy class tutorials | `run_backtestingpy_signal` |
| bt | target-weight ETF and portfolio rotation | `run_bt_target_weights` |
| Backtrader | event-driven data feeds and order logic | template writer |
| Zipline-Reloaded | calendar-safe factor research skeleton | template writer |
| QuantStats | HTML reports and performance tear sheets | `quantstats_html_report` |

## vectorbt

```python
from examples.quant_trading.frameworks import run_vectorbt_from_signals

portfolio = run_vectorbt_from_signals(prices, entries, exits)
print(portfolio.total_return())
```

## backtesting.py

```python
from examples.quant_trading.data import fetch_yahoo_ohlcv
from examples.quant_trading.frameworks import run_backtestingpy_signal

ohlcv = fetch_yahoo_ohlcv("SPY", start="2018-01-01")
stats = run_backtestingpy_signal(ohlcv, signal)
```

## bt

```python
from examples.quant_trading.frameworks import run_bt_target_weights

result = run_bt_target_weights(prices, target_weights)
```

## Backtrader and Zipline-Reloaded

The column writes template files rather than forcing these frameworks into every
notebook environment:

```python
from examples.quant_trading.frameworks import write_framework_templates

write_framework_templates("examples/quant_trading/templates")
```

These event-driven frameworks require careful calendar, bundle, and execution
setup. Keep De-Time feature generation outside the event loop unless you are
explicitly modeling the cost and latency of online recomputation.

Rendered notebook transcript with code and output:
[08 backtesting framework adapters](notebooks/08_backtesting_framework_adapters.md)
