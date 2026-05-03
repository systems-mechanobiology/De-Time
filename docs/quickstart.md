# Quickstart

Before you start, install the current repository:

```bash
python -m pip install "git+https://github.com/systems-mechanobiology/De-Time.git"
```

Contributor checkout:

```bash
python -m pip install -e .[dev,docs]
```

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

Expected output on a native-enabled build:

```text
(120,)
native
```

The result object carries the same shape contract for every method:

```python
print(result.season.shape)
print(result.residual.shape)
print(sorted(result.meta))
```

```text
(120,)
(120,)
['backend_requested', 'backend_used', 'input_shape', 'method', 'n_channels', ...]
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

Expected stdout:

```text
Running STD on examples/data/example_series.csv...
Done. Results saved to out/std_run
```

This writes `out/std_run/example_series_summary.json`. The same command with
`--plot` also writes decomposition and residual figures.

For a published plot-backed run, see the
[Univariate Tutorial](tutorials/univariate.md#saving-output-with-the-cli).

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

Expected output:

```text
(8, 96, 2)
```

## Next steps

- Use [Methods & Chooser](methods.md) to decide whether to stay on the flagship
  path or move to a wrapper.
- Use `detime recommend --length ... --channels ...` when you want a
  machine-readable shortlist.
- Use `detime schema --name config` when you want the packaged config schema.
- Use [Tutorials](tutorials/univariate.md) for step-by-step workflows.
- Use [Migration from `tsdecomp`](migration.md) if you are updating older code.
