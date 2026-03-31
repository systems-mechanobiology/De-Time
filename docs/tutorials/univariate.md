# Univariate workflows

## When to use univariate methods

Use the univariate path when a single observed series is decomposed into trend,
seasonality, and remainder components.

Good starting methods:

- `STL` when the seasonal period is known and the data are reasonably regular,
- `SSA` when you want a flexible subspace method,
- `STD` when you want blockwise seasonal-trend-dispersion structure,
- `WAVELET` when you want a multi-scale signal-processing view.

## Example: SSA

```python
import numpy as np
from detime import DecompositionConfig, decompose

t = np.arange(120, dtype=float)
series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)

result = decompose(
    series,
    DecompositionConfig(
        method="SSA",
        params={"window": 24, "rank": 6, "primary_period": 12},
    ),
)
```

## Example: STD

```python
result = decompose(
    series,
    DecompositionConfig(
        method="STD",
        params={"period": 12},
    ),
)
```

## Saving output with the CLI

```bash
detime run \
  --method SSA \
  --series examples/data/example_series.csv \
  --col value \
  --param window=24 \
  --param primary_period=12 \
  --out_dir out/ssa_run
```
