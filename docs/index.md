# De-Time

**De-Time** is the product face of `de-time`: a decomposition library for
turning raw time series into operational components with a consistent interface.

It is built for a common failure mode in scientific software: strong methods
trapped behind inconsistent APIs, unclear outputs, or benchmark-only packaging.
De-Time takes the opposite route. One package. One decomposition contract. One
surface for Python, CLI, and automated workflows.

## What it is

De-Time is a time-series decomposition platform for:

- classical seasonal-trend decomposition,
- subspace decomposition,
- adaptive mode decomposition,
- selected multivariate workflows,
- reproducible batch and profiling pipelines.

Core package promises:

- one `decompose()` entrypoint,
- one `DecompositionConfig` setup surface,
- one `DecompResult` result contract,
- optional native acceleration where it changes throughput in practice,
- explicit metadata for downstream agent or pipeline handoff.

## What it is not

De-Time is not:

- a forecasting framework,
- a universal time-series toolkit,
- a hidden benchmark artifact,
- a claim that all bundled methods have equal production maturity.

Some methods are native-backed and deeply integrated. Others intentionally wrap
well-known upstream implementations. The docs call that out instead of flattening
everything into one vague maturity level.

## Quickstart

Install the package:

```bash
pip install de-time
```

Run a first decomposition:

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
```

Or from the CLI:

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run
```

## Project snapshot

| Snapshot | Value |
|---|---|
| Brand | `De-Time` |
| Distribution name | `de-time` |
| Preferred import | `detime` |
| Legacy import | `tsdecomp` |
| Best current starting points | `SSA`, `STD`, `STDR`, `DR_TS_REG`, `MSSA` |
| Native-backed methods | `SSA`, `STD`, `STDR`, `DR_TS_REG` |
| Multivariate methods | `STD`, `STDR`, `MSSA`, `MVMD`, `MEMD` |
| Core commands | `run`, `batch`, `profile` |
| Primary outputs | `trend`, `season`, `residual`, `components`, `meta` |

## Method landscape

### Seasonal-trend

- `STL`
- `MSTL`
- `ROBUST_STL`
- `STD`
- `STDR`

### Subspace

- `SSA`
- `MSSA`

### Adaptive mode decomposition

- `EMD`
- `CEEMDAN`
- `VMD`
- `MVMD`
- `MEMD`

### Other workflows

- `WAVELET`
- `MA_BASELINE`
- `GABOR_CLUSTER`
- `DR_TS_REG`
- `DR_TS_AE`
- `SL_LIB`

## Agent-friendly handoff

If you are onboarding this project into another repo, agent, or automation
pipeline, preserve these assumptions:

- preferred import path is `detime`,
- legacy import path `tsdecomp` still works,
- brand-facing name is `De-Time`,
- `DecompResult.meta` is part of the public handoff contract,
- `backend="auto"` is the normal runtime choice,
- multivariate workflows should prefer true joint methods such as `MSSA`,
  `MVMD`, and `MEMD` when cross-channel structure matters.

Useful next stops:

- [Install](install.md)
- [Quickstart](quickstart.md)
- [Methods](methods.md)
- [API](api.md)
- [Examples](examples.md)
- [Project Status and Release Files](project-status.md)
- [Agent-Friendly Guide](agent-friendly.md)
- [JMLR Improvements](jmlr-improvements.md)
