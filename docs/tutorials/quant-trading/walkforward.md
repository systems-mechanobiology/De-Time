# Walk-Forward Validation and Audit Protocol

The most important rule is unchanged: decomposition must be computed
walk-forward.  Decomposing the full price history before signal generation leaks
future trend and cycle structure into the past.

## Correct workflow

1. Choose a training window, for example 252 trading days.
2. Decompose only the current training window.
3. Keep only the last feature row from that window.
4. Forward-fill that feature until the next recomputation date.
5. Shift positions by one bar before calculating returns.
6. Charge turnover-based costs.
7. Record data source, command, strategy list and status in a run manifest.

```python
features = walkforward_price_volume_features(
    prices,
    volumes,
    method="STL",
    period=63,
    train_window=252,
    step=21,
)
```

## Common failure modes

| Failure mode | Why it matters | Mitigation |
|---|---|---|
| Full-sample decomposition | leaks future structure | use `walkforward_price_volume_features` |
| Same-bar execution | enters using information not available at fill time | `backtest_weights` shifts weights by one bar |
| Ignoring costs | overstates high-turnover strategies | report fee/slippage and turnover |
| Unstable universe | hindsight-biased symbol membership | record membership rules |
| Vendor gaps | residual features become distorted | run `data_audit_report` and feature coverage |
| Silent failures | bad runs disappear | use `failed_runs.csv`, `missing_runs.csv`, and manifests |

Columns 01-02 include the lightweight audit assets under
`examples/quant_trading/reports/`.
