# Quickstart

## Python API

```python
import numpy as np

from detime import DecompositionConfig, decompose

t = np.arange(120, dtype=float)
series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)

cfg = DecompositionConfig(
    method="SSA",
    params={"window": 24, "rank": 6, "primary_period": 12},
)
result = decompose(series, cfg)
```

`result` is a `DecompResult` with:

- `trend`
- `season`
- `residual`
- `components`
- `meta`

## CLI

Create a CSV with a numeric column called `value`, then run:

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run
```

To profile a method:

```bash
detime profile \
  --method MSSA \
  --series examples/data/example_multivariate.csv \
  --cols x0,x1 \
  --param window=24 \
  --param primary_period=12
```

## Multivariate workflow

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

cfg = DecompositionConfig(
    method="MSSA",
    params={"window": 24, "rank": 8, "primary_period": 12},
    channel_names=["x0", "x1"],
)
result = decompose(series, cfg)
```

For more complete workflows, see the tutorial pages and `examples/`.

Legacy compatibility note:

- `from tsdecomp import ...` still works
- `tsdecomp run` and `python -m tsdecomp` still work
