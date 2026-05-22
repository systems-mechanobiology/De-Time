# Walk-Forward Validation and Audit Protocol

The most important research rule in this column is that decomposition must be
computed walk-forward. Decomposing the full price history before creating
signals leaks future structure into the past.

## Correct workflow

1. Choose a training window, for example 252 trading days.
2. Decompose only the current training window.
3. Keep only the last feature row from that window.
4. Forward-fill that feature until the next recomputation date.
5. Shift positions by one bar before calculating returns.
6. Charge turnover-based costs.
7. Report missing and failed experiments.

```python
features = walkforward_decompose(
    prices,
    method="STL",
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

## Reporting boundary

Notebook results are educational examples. A production-grade benchmark should
add official data sources, broker-aware execution assumptions, multiple seeds or
bootstrap intervals where relevant, and full experiment manifests.
