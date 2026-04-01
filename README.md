# De-Time

> Research software for reproducible time-series decomposition across classical, subspace, adaptive, and multivariate workflows.

[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-0f172a.svg)](LICENSE)
![Status: Beta](https://img.shields.io/badge/status-beta-1d4ed8.svg)
[![Docs: GitHub Pages](https://img.shields.io/badge/docs-GitHub_Pages-0b5fff.svg)](https://systems-mechanobiology.github.io/De-Time/)
![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-0f766e.svg)
![Institution: The University of Birmingham](https://img.shields.io/badge/institution-The_University_of_Birmingham-7c3aed.svg)

[Homepage](https://systems-mechanobiology.github.io/De-Time/) ·
[Getting Started](https://systems-mechanobiology.github.io/De-Time/quickstart/) ·
[Tutorials](https://systems-mechanobiology.github.io/De-Time/tutorials/univariate/) ·
[Methods Atlas](https://systems-mechanobiology.github.io/De-Time/methods/) ·
[API Reference](https://systems-mechanobiology.github.io/De-Time/api/) ·
[GitHub](https://github.com/systems-mechanobiology/De-Time)

![De-Time title card](docs/assets/brand/detime-title-card.svg)

De-Time turns a fragmented decomposition landscape into one research-facing
software surface. You bring a series, a table, or a multichannel array.
De-Time gives you a consistent decomposition contract, reproducible outputs,
visual walkthroughs, and method-level metadata that can survive handoff to
other people or other agents.

De-Time is the public brand. The distribution name is `de-time`, the preferred
import is `detime`, and the legacy `tsdecomp` import and CLI aliases still work
for compatibility.

| Maintainer | Affiliation | Install |
|---|---|---|
| Zipeng Wu | The University of Birmingham | `pip install de-time` |

## What it is

De-Time is designed for research and engineering workflows that need:

- one `decompose()` entrypoint across many decomposition families,
- one `DecompositionConfig` surface for Python and CLI usage,
- one `DecompResult` contract for `trend`, `season`, `residual`, `components`,
  and `meta`,
- native acceleration where it materially changes throughput,
- multivariate workflows where joint structure matters,
- public docs with runnable examples and visual reports.

## What it is not

De-Time is not trying to be:

- a forecasting framework,
- a general feature-engineering toolkit,
- a dashboard product,
- a benchmark artifact pretending to be a library,
- a claim that every bundled method has identical maturity.

## Project snapshot

| Area | Current state |
|---|---|
| Package name | `de-time` |
| Preferred import | `detime` |
| Legacy compatibility import | `tsdecomp` |
| Strongest current methods | `SSA`, `STD`, `STDR`, `DR_TS_REG`, `MSSA` |
| Native-backed methods | `SSA`, `STD`, `STDR`, `DR_TS_REG` |
| Multivariate methods | `STD`, `STDR`, `MSSA`, `MVMD`, `MEMD` |
| Primary outputs | `trend`, `season`, `residual`, `components`, `meta` |
| First-class commands | `detime run`, `detime batch`, `detime profile` |
| Homepage and docs | <https://systems-mechanobiology.github.io/De-Time/> |

## 60-second quickstart

Install:

```bash
pip install de-time
```

Python API:

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

print(result.trend.shape, result.meta["backend_used"])
```

CLI:

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run
```

Multivariate:

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

## Use your own data

If you already have a file, start by matching it to one of these shapes:

| Your data | What De-Time expects first | First path |
|---|---|---|
| One numeric series | one array or one numeric CSV column | `decompose(series, ...)` or `detime run --col value` |
| Wide table with multiple measurements | multiple numeric columns in one aligned table | `detime run --method MSSA --cols x0,x1` |
| Batch of files or repeated experiments | a folder or manifest of repeatable runs | `detime batch ...` |

For more detailed walk-throughs, use the docs rather than stretching the README:

- [Getting Started](https://systems-mechanobiology.github.io/De-Time/quickstart/)
- [Tutorials](https://systems-mechanobiology.github.io/De-Time/tutorials/univariate/)
- [Example Gallery](https://systems-mechanobiology.github.io/De-Time/examples/)

## Why this software exists in research workflows

Time-series decomposition software is fragmented across papers, single-method
libraries, and benchmark-only artifacts. That creates avoidable friction:

- method interfaces are inconsistent,
- result objects are hard to compare across methods,
- reproducible pipelines are harder than they should be,
- moving from one-off notebooks to repeatable experiments becomes expensive.

De-Time exists to reduce that friction without hiding method differences. It
keeps one public surface while documenting which methods are native-backed,
which depend on upstream libraries, and which are best used as wrappers rather
than as flagship entrypoints.

## Documentation map

- [Homepage](https://systems-mechanobiology.github.io/De-Time/) for the short product overview
- [Getting Started](https://systems-mechanobiology.github.io/De-Time/quickstart/) for installation and first successful runs
- [Tutorials](https://systems-mechanobiology.github.io/De-Time/tutorials/univariate/) for step-by-step workflows
- [Methods Atlas](https://systems-mechanobiology.github.io/De-Time/methods/) for method families, maturity, and backend story
- [API Reference](https://systems-mechanobiology.github.io/De-Time/api/) for imports, config fields, and result structure
- [Research Positioning](https://systems-mechanobiology.github.io/De-Time/research-positioning/) for ecosystem and scope
- [Agent Tools](https://systems-mechanobiology.github.io/De-Time/agent-friendly/) for handoff-oriented routing and contracts

## Project files, citation, and software hygiene

Key repository files:

- [`CITATION.cff`](CITATION.cff)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- [`SECURITY.md`](SECURITY.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`PUBLISHING.md`](PUBLISHING.md)

These files are treated as part of the public software surface, not as afterthoughts.
