# De-Time

Workflow-oriented research software for reproducible time-series decomposition.

[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-0f172a.svg)](LICENSE)
![Status: Beta](https://img.shields.io/badge/status-beta-1d4ed8.svg)
[![Docs: GitHub Pages](https://img.shields.io/badge/docs-GitHub_Pages-0b5fff.svg)](https://systems-mechanobiology.github.io/De-Time/)
![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-0f766e.svg)

<p align="center">
  <img src="docs/assets/brand/detime-logo.svg" alt="De-Time logo" width="640">
</p>

De-Time provides one stable software surface for decomposition workflows that
would otherwise be split across notebooks, method-specific wrappers, and
one-off scripts. The product name is **De-Time**, the distribution is
`de-time`, the canonical import is `detime`, and the legacy top-level
`tsdecomp` import and CLI remain compatibility-only through `0.1.x`, with
earliest removal planned for `0.2.0`.

The current branch targets release `0.1.1`. PyPI publication is planned after
the reviewed release is cut; until then, install from GitHub or use the
editable contributor path below.

Fast entry points:

- [Documentation site](https://systems-mechanobiology.github.io/De-Time/)
- [Beginner notebook method gallery](examples/notebooks/de_time_method_gallery.ipynb)
- [Cross-package comparison](docs/comparisons.md)
- [Method comparison matrix](docs/method-matrix.md)

## Scope

De-Time is for:

- one `decompose()` entrypoint,
- one `DecompositionConfig` model for Python and CLI usage,
- one `DecompResult` contract for `trend`, `season`, `residual`, `components`,
  and `meta`,
- native acceleration where it materially improves throughput,
- multivariate decomposition workflows where shared structure matters,
- machine-facing workflows that need schemas, recommendations, and low-token
  result views.

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
`STL`, `MSTL`, `ROBUST_STL`, `EMD`, `CEEMDAN`, `VMD`, `WAVELET`,
`MA_BASELINE`, `MVMD`, `MEMD`, and `GABOR_CLUSTER`.

Benchmark-derived methods `DR_TS_REG`, `DR_TS_AE`, and `SL_LIB` do not ship in
the main package. They belong to the companion benchmark repository
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).

## Cross-package comparison

De-Time is positioned as a workflow and machine-contract layer beside
specialist packages, not as a replacement for all of them.

| Axis | De-Time | [statsmodels](https://www.statsmodels.org/) | [PyEMD](https://github.com/laszukdawid/PyEMD) | [PyWavelets](https://pywavelets.readthedocs.io/en/latest/) | [PySDKit](https://pysdkit.readthedocs.io/en/latest/) | [SSALib](https://github.com/ADSCIAN/ssalib) | [sktime](https://www.sktime.net/en/stable/) |
|---|---|---|---|---|---|---|---|
| Primary role | unified decomposition workflow | classical decomposition/statistics | EMD family | wavelet transforms | broad decomposition toolkit | SSA specialist | broad time-series ecosystem |
| Common config/result contract | yes | partial | no | no | partial | SSA-specific | no |
| CLI, batch, profiling | yes | no | no | no | limited | no | partial |
| Machine-readable catalog/schemas | yes | no | no | no | no | no | no |
| Multivariate under one surface | yes | limited | family-specific | transform-specific | yes | no | partial |
| Where it is deeper | workflow reproducibility | statistical modeling | EMD variants | wavelet tooling | decomposition breadth | SSA workflows | ecosystem breadth |

Full reviewer-facing comparison evidence is in
[docs/comparisons.md](docs/comparisons.md) and
[docs/comparison-evidence.md](docs/comparison-evidence.md).

## Install

```bash
python -m pip install "git+https://github.com/systems-mechanobiology/De-Time.git"
```

Editable install for contributors and release-prep work:

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev,docs]
```

Notebook tooling:

```bash
python -m pip install -e .[dev,docs,notebook]
```

Optional multivariate backend extras from GitHub:

```bash
python -m pip install "de-time[multivar] @ git+https://github.com/systems-mechanobiology/De-Time.git"
```

Do not install the unrelated `detime` package from PyPI when you want this
project. Planned PyPI install after the release is `pip install de-time`.

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
  --out_dir out/std_run \
  --output-mode summary
```

## CLI surface

The supported commands are:

- `detime run`
- `detime batch`
- `detime profile`
- `detime version`
- `detime schema`
- `detime recommend`

The legacy `tsdecomp` executable calls the same code path but emits a
deprecation notice.

## Agent-native surface

De-Time now includes:

- packaged JSON schemas for `config`, `result`, `meta`, and `method-registry`,
- low-token result export modes: `full`, `summary`, and `meta`,
- machine-readable method metadata for registry, docs, and recommendation,
- `detime schema` and `detime recommend`,
- a local-first MCP server at `python -m detime.mcp.server`.

## Package boundary

This repository ships the reusable decomposition software package, docs, tests,
and examples needed for `detime` itself. Benchmark orchestration, leaderboard
artifacts, benchmark scenario galleries, and benchmark-derived methods are
split into the companion repository
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).

Only the top-level `tsdecomp` import and CLI alias remain packaged for
compatibility.

## Quality and evidence

- Release smoke checks live in `scripts/release_smoke_matrix.py`.
- Reviewer-facing documentation consistency checks live in
  `scripts/check_doc_consistency.py`.
- The current performance snapshot is generated by
  `scripts/generate_performance_snapshot.py` and stored under
  `docs/assets/generated/evidence/`.
- Comparison matrices are generated by
  `benchmarks/software_comparison/generate_comparison_evidence.py`.
- Token benchmarks are generated with `tiktoken` by
  `benchmarks/token_benchmarks/generate_token_benchmarks.py`.
- Deterministic agent workflow checks are generated by
  `evals/agent/run_agent_evals.py`.
- The coverage story is intentionally split into core-surface coverage and
  package-wide coverage so the denominator stays explicit.

## Documentation

Core docs:
- Homepage: <https://systems-mechanobiology.github.io/De-Time/>
- Install: <https://systems-mechanobiology.github.io/De-Time/install/>
- Quickstart: <https://systems-mechanobiology.github.io/De-Time/quickstart/>
- Methods overview: <https://systems-mechanobiology.github.io/De-Time/methods/>
- Notebook gallery: <https://systems-mechanobiology.github.io/De-Time/notebook-gallery/>
- Tutorials: <https://systems-mechanobiology.github.io/De-Time/tutorials/univariate/>
- API: <https://systems-mechanobiology.github.io/De-Time/api/>

Reference and review:
- Method cards: <https://systems-mechanobiology.github.io/De-Time/method-cards/>
- Method matrix: <https://systems-mechanobiology.github.io/De-Time/method-matrix/>
- Config reference: <https://systems-mechanobiology.github.io/De-Time/config-reference/>
- Method references: <https://systems-mechanobiology.github.io/De-Time/method-references/>
- Machine API: <https://systems-mechanobiology.github.io/De-Time/machine-api/>
- Comparisons: <https://systems-mechanobiology.github.io/De-Time/comparisons/>
- Comparison evidence: <https://systems-mechanobiology.github.io/De-Time/comparison-evidence/>
- Reproducibility: <https://systems-mechanobiology.github.io/De-Time/reproducibility/>

## Project files

- Citation metadata: [`CITATION.cff`](CITATION.cff)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
- Contributing guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Publishing notes: [`PUBLISHING.md`](PUBLISHING.md)
