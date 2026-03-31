# Start here

If you only have one minute, use one of these paths.

## 1. One Python call

Use this when you already have an array in memory.

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

Use this when your agent already has a CSV path.

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run
```

This writes:

- `out/std_run/example_series_components.csv`
- `out/std_run/example_series_meta.json`

## 3. First method choice

- start with `STD` or `STDR` if you know the seasonal period
- start with `SSA` if you want a strong general univariate baseline
- start with `MSSA` if you have multiple aligned channels
- move to `EMD`, `CEEMDAN`, `VMD`, `MVMD`, or `MEMD` when adaptive or
  non-stationary oscillations matter more than classical seasonal structure

## 4. First backend choice

- start with `backend="auto"`
- use `backend="native"` when you want to force a native-backed method and
  fail fast if it is unavailable
- use `backend="python"` when reproducibility against the pure Python path
  matters more than speed

## 5. First docs to open

- `ENTRYPOINTS.md`
- `AGENT_MANIFEST.md`
- `AGENT_INPUT_CONTRACT.md`
- `docs/quickstart.md`
- `docs/api.md`

Legacy compatibility note:

- `from tsdecomp import ...` still works
- `tsdecomp run` and `python -m tsdecomp` still work
