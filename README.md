# De-Time

Research software for reproducible time-series decomposition.

[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-0f172a.svg)](LICENSE)
![Status: Beta](https://img.shields.io/badge/status-beta-1d4ed8.svg)
[![Docs: GitHub Pages](https://img.shields.io/badge/docs-GitHub_Pages-0b5fff.svg)](https://systems-mechanobiology.github.io/De-Time/)
![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-0f766e.svg)

![De-Time title card](docs/assets/brand/detime-title-card.svg)

De-Time provides one stable software surface for decomposition workflows that
would otherwise be spread across notebooks, method-specific wrappers, and
one-off scripts. The canonical package is `detime`. The distribution name is
`de-time`. The legacy `tsdecomp` import and CLI remain available for one
deprecation cycle.

## Scope

De-Time is for:

- a consistent `decompose()` entrypoint,
- one `DecompositionConfig` model for Python and CLI usage,
- one `DecompResult` contract for `trend`, `season`, `residual`, `components`,
  and `meta`,
- native acceleration where it materially improves throughput,
- multivariate decomposition workflows where shared structure matters.

De-Time is not:

- a new decomposition algorithm,
- a benchmark leaderboard package,
- a replacement for every specialized upstream library,
- a claim that every bundled wrapper has equal maturity.

## Flagship methods

The main package is centered on four methods:

- `SSA`
- `STD`
- `STDR`
- `MSSA`

Other retained methods are wrappers or optional-backend integrations such as
`STL`, `MSTL`, `EMD`, `CEEMDAN`, `VMD`, `WAVELET`, `MVMD`, `MEMD`, and
`GABOR_CLUSTER`.

Benchmark-derived methods `DR_TS_REG`, `DR_TS_AE`, and `SL_LIB` no longer ship
in the main package. They moved to the companion benchmark repository
`de-time-bench`.

## Install

```bash
pip install "de-time @ git+https://github.com/systems-mechanobiology/De-Time.git"
```

Optional multivariate backend extras:

```bash
pip install "de-time[multivar] @ git+https://github.com/systems-mechanobiology/De-Time.git"
```

The product name is `De-Time`, the distribution name is `de-time`, and the
canonical import is `detime`. Until the first PyPI release of De-Time exists,
install from GitHub rather than from the unrelated `detime` package on PyPI.

## Quickstart

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

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run
```

## CLI surface

The supported commands are:

- `detime run`
- `detime batch`
- `detime profile`
- `detime version`

The legacy `tsdecomp` executable calls the same code path but emits a
deprecation notice.

## Package boundary

This repository now ships only the software package, documentation, tests, and
examples needed for `detime` itself. Benchmark orchestration, leaderboard
artifacts, and benchmark-derived methods have been split into the companion
repository `de-time-bench`.

## Documentation

- Homepage: <https://systems-mechanobiology.github.io/De-Time/>
- Quickstart: <https://systems-mechanobiology.github.io/De-Time/quickstart/>
- Methods: <https://systems-mechanobiology.github.io/De-Time/methods/>
- API: <https://systems-mechanobiology.github.io/De-Time/api/>
- Migration guide: <https://systems-mechanobiology.github.io/De-Time/migration/>

## Project files

- Citation metadata: [`CITATION.cff`](CITATION.cff)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
- Contributing guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Publishing notes: [`PUBLISHING.md`](PUBLISHING.md)
