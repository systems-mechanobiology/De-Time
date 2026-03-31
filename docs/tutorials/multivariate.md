# Multivariate workflows

## Supported multivariate methods

Current multivariate-capable methods are:

- `MSSA`
- `MVMD`
- `MEMD`

Channelwise methods that also accept `2D (T, C)` input:

- `STD`
- `STDR`

## Example: MSSA

```python
import numpy as np
from detime import DecompositionConfig, decompose

t = np.arange(96, dtype=float)
series = np.column_stack(
    [
        0.03 * t + np.sin(2.0 * np.pi * t / 12.0),
        -0.01 * t + 0.6 * np.sin(2.0 * np.pi * t / 12.0 + 0.4),
    ]
)

result = decompose(
    series,
    DecompositionConfig(
        method="MSSA",
        params={"window": 24, "rank": 8, "primary_period": 12},
        channel_names=["x0", "x1"],
    ),
)
```

## Example: channelwise STD

```python
result = decompose(
    series,
    DecompositionConfig(
        method="STD",
        params={"period": 12},
        channel_names=["x0", "x1"],
    ),
)
```

## CLI

```bash
detime run \
  --method MSSA \
  --series examples/data/example_multivariate.csv \
  --cols x0,x1 \
  --param window=24 \
  --param primary_period=12 \
  --out_dir out/mssa_run
```

Multivariate results are saved in wide CSV format for `2D` outputs and `.npz`
archives for `3D` components.
