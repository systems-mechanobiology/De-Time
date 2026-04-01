# Getting Started

De-Time should feel short on the first interaction and expandable later.

## Install

```bash
pip install de-time
```

The preferred import is `detime`. The legacy `tsdecomp` import and CLI aliases
still work for compatibility.

## First successful Python call

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

## First successful CLI call

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

## Use your own data

| Your data | What De-Time expects first | First path |
|---|---|---|
| One numeric column | one array or one numeric CSV column | `detime run --col value` |
| Wide table | several numeric columns in one aligned table | `detime run --method MSSA --cols x0,x1` |
| Repeated files or folders | repeatable batch workflow | `detime batch ...` |

If your columns use different names, rename them before the first run. The
library does not try to guess arbitrary semantics from non-standard headers.

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

## Next stops

- [Installation](install.md)
- [Decision Guide](tutorials/decision-guide.md)
- [Example Gallery](examples.md)
- [Methods Atlas](methods.md)
