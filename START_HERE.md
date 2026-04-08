# Start here

If you only have one minute, use one of these paths.

## 1. One Python call

```python
import numpy as np
from detime import DecompositionConfig, decompose

t = np.arange(120, dtype=float)
series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)

result = decompose(
    series,
    DecompositionConfig(
        method="STD",
        params={"period": 12},
        backend="auto",
    ),
)

print(result.trend.shape)
print(result.meta)
```

## 2. One file through the CLI

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run \
  --output-mode summary
```

This writes:

- `out/std_run/example_series_summary.json`

## 3. First routing tool

```bash
detime recommend --length 192 --channels 3 --prefer accuracy
```

## 4. First machine-facing tool

```bash
detime schema --name method-registry
```

## 5. First backend choice

- start with `backend="auto"`
- use `backend="native"` when you want to force a native-backed method and
  fail fast if it is unavailable
- use `backend="python"` when reproducibility against the pure Python path
  matters more than speed

Legacy compatibility note:

- `from tsdecomp import ...` still works
- `tsdecomp run` and `python -m tsdecomp` still work
