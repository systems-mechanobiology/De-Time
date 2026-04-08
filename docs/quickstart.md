# Quickstart

## Python

```python
import numpy as np

from detime import DecompositionConfig, decompose

t = np.arange(120, dtype=float)
series = 0.03 * t + np.sin(2.0 * np.pi * t / 12.0)

result = decompose(
    series,
    DecompositionConfig(
        method="SSA",
        params={"window": 24, "rank": 6, "primary_period": 12},
    ),
)

print(result.trend.shape)
print(result.meta["backend_used"])
```

## CLI

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run \
  --output-mode summary
```

## Multivariate

```python
import numpy as np

from detime import DecompositionConfig, decompose

t = np.arange(96, dtype=float)
panel = np.column_stack(
    [
        0.03 * t + np.sin(2.0 * np.pi * t / 12.0),
        -0.01 * t + 0.6 * np.sin(2.0 * np.pi * t / 12.0 + 0.4),
    ]
)

result = decompose(
    panel,
    DecompositionConfig(
        method="MSSA",
        params={"window": 24, "rank": 8, "primary_period": 12},
        channel_names=["x0", "x1"],
    ),
)

print(result.components["modes"].shape)
```

## Next steps

- Use [Choose a Method](choose-a-method.md) to decide whether to stay on the
  flagship path or move to a wrapper.
- Use `detime recommend --length ... --channels ...` when you want a
  machine-readable shortlist.
- Use `detime schema --name config` when you want the packaged config schema.
- Use [Tutorials](tutorials/univariate.md) for step-by-step workflows.
- Use [Migration from `tsdecomp`](migration.md) if you are updating older code.
