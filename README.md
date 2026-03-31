# De-Time

**De-Time** is the product brand for `de-time`: a time-series decomposition
library that turns a fragmented method landscape into one operational surface.
You bring a series and a method name. De-Time gives you a consistent Python API,
CLI, output schema, and method-level handoff metadata across classical,
adaptive, and multivariate decomposition workflows.

`pip install` stays simple:

```bash
pip install de-time
```

The preferred import path is `detime`. The legacy import path `tsdecomp` still
works for compatibility. The brand is **De-Time**.

## What it is

De-Time is a decomposition workbench for people and agents who need to move
from "I have a signal" to "I have trend, seasonality, residual, and method
metadata I can actually use."

It provides:

- one `decompose()` entrypoint across many methods,
- one `DecompositionConfig` surface for Python and CLI usage,
- one `DecompResult` contract for trend / season / residual outputs,
- optional native C++ acceleration for selected high-cost paths,
- multivariate workflows for methods that genuinely operate on multiple
  channels,
- profiling, batch execution, and CSV/parquet-friendly pipelines.

## What it is not

De-Time is not trying to be:

- a forecasting library,
- a general feature engineering toolkit,
- a dashboard product,
- a benchmark paper disguised as a package,
- a claim that every decomposition method has identical maturity.

Some methods are deeply integrated and native-backed. Some rely on established
upstream scientific libraries. That distinction is documented explicitly rather
than hidden behind a uniform marketing layer.

## Why this package exists

Time-series decomposition tooling is scattered. A strong method in one paper may
come with an ad hoc interface, unclear output semantics, or limited support for
reproducible pipelines. A good production method may be easy to run in one
environment and painful to compare against alternatives.

De-Time exists to close that gap:

- comparable method invocation,
- reproducible result structure,
- clean transition from notebook exploration to scripted evaluation,
- agent-friendly metadata for downstream automation,
- a standalone software package rather than a monolithic research artifact.

## Quickstart

### Python

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

print(result.trend.shape, result.season.shape, result.residual.shape)
print(result.meta["backend_used"])
```

### CLI

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run
```

### Multivariate

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

print(result.trend.shape)
print(result.components["modes"].shape)
```

## Project snapshot

| Area | Current state |
|---|---|
| Distribution name | `de-time` |
| Brand | `De-Time` |
| Preferred import | `detime` |
| Legacy import | `tsdecomp` |
| Main entrypoints | `decompose()`, `DecompositionConfig`, `detime run`, `detime batch`, `detime profile` |
| Strongest production surface | unified API, CLI, `SSA`, `STD`, `STDR`, `DR_TS_REG`, `MSSA` |
| Native acceleration | `SSA`, `STD`, `STDR`, `DR_TS_REG` |
| Multivariate methods | `STD`, `STDR`, `MSSA`, `MVMD`, `MEMD` |
| Output contract | `trend`, `season`, `residual`, `components`, `meta` |
| Installation model | wheel-first; source build may require local C++ toolchain |

## Method map

Current methods include:

- seasonal-trend methods: `STL`, `MSTL`, `ROBUST_STL`, `STD`, `STDR`
- subspace methods: `SSA`, `MSSA`
- adaptive mode methods: `EMD`, `CEEMDAN`, `VMD`, `MVMD`, `MEMD`
- other supported workflows: `WAVELET`, `MA_BASELINE`, `GABOR_CLUSTER`,
  `DR_TS_REG`, `DR_TS_AE`, `SL_LIB`

The package does not pretend that all of these are equal in maturity. If you
need the most stable surface today, start with:

- `SSA`
- `STD`
- `STDR`
- `DR_TS_REG`
- `MSSA`

## Installation

Base install:

```bash
pip install de-time
```

Optional multivariate backends:

```bash
pip install "de-time[multivar]"
```

Optional documentation toolchain:

```bash
pip install "de-time[docs]"
```

For local development:

```bash
cd /path/to/de-time
python3 -m pip install -U pip
python3 -m pip install -e .[multivar,docs]
python3 -m pytest tests -q
```

Prebuilt wheels are the primary installation path for Linux, macOS, and
Windows on supported CPython versions. If a wheel is not available, `pip` may
fall back to a source build, which requires a local C++ toolchain.

## Repository files

For a standalone GitHub repository, the most important project-level files are:

- [`CITATION.cff`](CITATION.cff) for software citation metadata
- [`CHANGELOG.md`](CHANGELOG.md) for release history
- [`SECURITY.md`](SECURITY.md) for vulnerability reporting guidance
- [`ROADMAP.md`](ROADMAP.md) for project direction and non-goals
- [`PUBLISHING.md`](PUBLISHING.md) for release and PyPI workflow notes
- [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines

## Agent-friendly handoff

If another engineer or coding agent needs to take over quickly, this is the
minimum useful context:

- product/brand name: `De-Time`
- distribution name: `de-time`
- preferred Python package/import name: `detime`
- legacy Python package/import name: `tsdecomp`
- docs homepage: [`docs/index.md`](docs/index.md)
- shim import surface: `src/detime/`
- implementation root: `src/tsdecomp/`
- native backend: `native/`
- examples: `examples/`
- tests: `tests/`

Operational assumptions:

- prefer `backend="auto"` unless you are debugging parity or packaging,
- treat `DecompResult.meta` as part of the public handoff surface,
- use `MSSA`, `MVMD`, and `MEMD` for joint multivariate workflows,
- use `STD` and `STDR` in multichannel settings when channelwise decomposition
  is acceptable,
- document clearly when a method depends on an optional backend.

Fastest smoke-test commands:

```bash
python -m pip install -e .[multivar,docs]
python -m pytest tests -q
detime profile --method SSA --series examples/data/example_series.csv --col value
mkdocs serve
```

## Documentation

The docs tree lives in [`docs/`](docs/) and is organized as:

- `docs/index.md`: brand-level overview and package positioning
- `docs/install.md`: installation and platform notes
- `docs/quickstart.md`: API and CLI walkthrough
- `docs/api.md`: public API reference
- `docs/methods.md`: method families and support notes
- `docs/tutorials/`: univariate, multivariate, and profiling workflows

To build the docs locally:

```bash
mkdocs serve
```

## Submission-oriented notes

De-Time is being prepared as a standalone open-source software package rather
than only as a benchmark or paper artifact.

- [`JMLR_SOFTWARE_IMPROVEMENTS.md`](JMLR_SOFTWARE_IMPROVEMENTS.md) summarizes
  software-facing improvements.
- [`JMLR_SUBMISSION_CHECKLIST.md`](JMLR_SUBMISSION_CHECKLIST.md) tracks manual
  submission work that sits outside code changes.
- [`PUBLISHING.md`](PUBLISHING.md) documents the standalone release process for
  `de-time`.
