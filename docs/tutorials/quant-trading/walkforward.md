# Validation First: Walk-Forward Audit Protocol

The most important research rule in this column is that decomposition must be
computed walk-forward. Decomposing the full price history before creating
signals leaks future structure into the past.

## Timeline

| Timestamp | What exists | What may use it |
|---|---|---|
| Feature timestamp | historical prices inside the training window | De-Time component row |
| Signal date | last available feature row plus current rule parameters | target weight or entry/exit flag |
| Execution date | next tradable bar after the signal date | filled position |
| Return date | price change after the position is held | performance calculation |

The chart or table should make this ordering visible when a result is discussed.

## Correct workflow

1. Choose a training window, for example 252 trading days.
2. Decompose only the current training window.
3. Keep only the last feature row from that window.
4. Forward-fill that feature until the next recomputation date.
5. Shift positions by one bar before calculating returns.
6. Charge turnover-based costs.
7. Compare with baselines over the same dates and costs.
8. Report missing and failed experiments.

```python
features = walkforward_decompose(
    prices,
    method="ROBUST_STL",
    period=63,
    train_window=252,
    step=21,
)
```

## Common failure modes

| Failure mode | Why it matters | Mitigation |
|---|---|---|
| Full-sample decomposition | leaks future trend and seasonal structure | use `walkforward_decompose` |
| Same-bar execution | enters using information not available at fill time | shift positions by one bar |
| Ignoring costs | overstates high-turnover strategies | report fees, slippage, borrow, FX |
| Unstable universe | selected assets may be hindsight-biased | record membership rules |
| Vendor gaps | missing data can distort residuals | run `data_audit_report` |
| Parameter mining | many settings can overfit | use train/validation/test or walk-forward splits |
| Silent failures | omitted bad runs bias the story | keep failed-run logs visible |

## Failure boundaries

The audit fails when any of these conditions is true:

| Boundary | Failure condition |
|---|---|
| Baseline | strategy underperforms the agreed baseline after costs |
| Costs | small fee or slippage changes erase the result |
| Folds | performance depends on one fold or one market regime |
| Turnover | average turnover is too high for the assumed execution model |
| Data coverage | missing-data thresholds or stale-ticker checks fail |
| Universe | membership was chosen after seeing the result |
| Leakage | full-sample decomposition, same-bar fills, or final-test tuning is present |
| Failed runs | failed or dominated parameter settings are omitted |

A failed audit is still useful. It tells the reader which assumption broke and
what must change before the strategy can be discussed as a candidate.

Rendered notebook transcript with code and output:
[09 walk-forward validation and audit](notebooks/09_walkforward_validation_and_audit.md)
