# De-Time: Workflow-Oriented Research Software for Reproducible Time-Series Decomposition

## Abstract

De-Time is open-source research software for reproducible time-series
decomposition. The package does not introduce a new decomposition algorithm.
Instead, it provides a coherent software surface for configuring, running,
profiling, saving, and machine-serving decomposition workflows across several
retained method families. The canonical package namespace is `detime`, while
`tsdecomp` remains only as a deprecated top-level import and CLI alias. The
software surface centers on four flagship workflows, `SSA`, `STD`, `STDR`, and
`MSSA`, and retains additional wrapper-based integrations with explicit
maturity labels. Benchmark-oriented artifact code was separated into a
companion repository so that the main package is a clean software submission
rather than a mixed library-plus-benchmark artifact. Release `0.1.0` adds
packaged JSON schemas, low-token result views, a method recommender, and a
minimal MCP server in addition to tests, documentation, release automation, and
selected native-backed acceleration.

## 1. Introduction

Time-series decomposition workflows are often assembled from method-specific
libraries, notebook snippets, and one-off local scripts. This fragmentation
creates unnecessary friction when researchers need to compare methods, preserve
runtime metadata, serialize outputs, or move an analysis from one user or
machine to another.

De-Time addresses that software problem. Its contribution is therefore not a
new algorithm and not a benchmark paper. The contribution is a workflow layer:

- one configuration contract,
- one result contract,
- one public import surface,
- one public CLI for retained package workflows,
- selected native acceleration where it materially improves throughput,
- one machine-facing surface for schemas, recommendation, and low-token
  handoff.

This workflow layer is relevant to machine learning practice. In typical ML
pipelines, decomposition is used for denoising, feature extraction,
representation shaping, and preprocessing ahead of downstream estimators.
De-Time targets that workflow friction directly by standardizing
configuration, results, profiling, and saved outputs across retained
decomposition families.

## 2. Public software surface

The canonical public interface is built around:

- `DecompositionConfig` for method and runtime configuration,
- `DecompResult` for standardized outputs,
- `decompose()` for dispatch,
- a CLI with `run`, `batch`, `profile`, `version`, `schema`, and `recommend`,
- packaged JSON schemas and a minimal MCP server for tool-based access,
- native capability helpers for the retained flagship methods.

The canonical package identity is `detime`. The older `tsdecomp` namespace
remains available only as a deprecated top-level import and CLI compatibility
layer for one deprecation cycle.

The main package centers on four flagship workflows:

- `SSA`
- `STD`
- `STDR`
- `MSSA`

Additional methods such as `STL`, `MSTL`, `EMD`, `CEEMDAN`, `VMD`, `WAVELET`,
`MVMD`, `MEMD`, and `GABOR_CLUSTER` are retained as wrappers or optional
backends rather than presented as co-equal flagship methods.

## 3. Package boundary and relation to earlier artifacts

Earlier repository states mixed software-package concerns with benchmark
artifacts, synthetic generators, leaderboard helpers, and benchmark-derived
methods. In release `0.1.0`, those components were moved out of the main
package boundary into the companion repository
`systems-mechanobiology/de-time-bench`.

The main De-Time package does not ship:

- leaderboard orchestration as part of the public surface,
- benchmark configuration helpers as public package features,
- benchmark-derived methods in the main package,
- transition-era `tsdecomp` submodules outside the top-level import and CLI
  compatibility path,
- benchmark-only synthetic artifact code inside the installable package.

That split is central to the present submission. The software submission is now
the installable decomposition package itself, not a repackaged benchmark
stack.

## 4. Quality discipline and release story

Release `0.1.0` was cut on April 8, 2026 as tag `de-time-v0.1.0` and is
published as the `de-time` PyPI distribution. The package includes:

- tests for the retained public interface,
- strict documentation builds,
- wheel and source-distribution validation,
- artifact-layout checks that verify removed benchmark stubs and legacy
  transition modules do not re-enter wheel or sdist payloads,
- `twine check` for release artifacts,
- a coverage gate of `fail_under = 90` on the canonical core-plus-flagship
  coverage scope,
- native fallback handling where native kernels are unavailable,
- documentation consistency checks,
- release smoke automation,
- reproducible performance snapshot generation.

In the latest local release review run, the gated `detime` coverage report
reached `93.20%`.

## 5. Relationship to related software

De-Time is designed to complement specialist libraries rather than replace
them.

| Package | Where it is deeper | De-Time position |
|---|---|---|
| `statsmodels` | mature classical decomposition and modeling | De-Time wraps selected classical methods while standardizing the workflow layer |
| `PyEMD` | deeper EMD-family tooling | De-Time uses EMD-family methods as one family inside a broader workflow contract |
| `PyWavelets` | deeper wavelet transforms and transform-specific APIs | De-Time exposes wavelet decomposition for workflow consistency, not wavelet leadership |
| `PySDKit` | broader signal-decomposition toolkit and optional multivariate backends | De-Time uses `PySDKit` selectively for `MVMD` and `MEMD` while maintaining its own config/result layer |
| `SSALib` | deeper SSA-only environment | De-Time offers SSA as one flagship path inside a cross-family package |
| `sktime` | current maintained VMD reality plus a broader time-series transform ecosystem | De-Time treats the maintained `sktime` VMD path as the relevant comparison rather than relying on the older standalone `vmdpy` identity |

The main software claim is therefore not method-count breadth alone. It is the
combination of:

- a common `DecompositionConfig`,
- a common `DecompResult`,
- one CLI workflow surface,
- one package-level story for native support, profiling, and saved outputs,
- one machine-facing story for schemas, recommendation, and tool-based access.

## 6. Minimal software evidence

To keep the paper grounded in software behavior rather than in benchmark-score
storytelling, we report a small runtime snapshot from one Windows / Python
3.11.9 release environment of the package:

| Method | Python mean runtime (ms) | Native mean runtime (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 13.815 | 1.910 | 7.232x |
| `STD` | 0.178 | 0.036 | 4.962x |
| `STDR` | 0.183 | 0.019 | 9.599x |

These numbers are not presented as universal performance claims. They are
included to show that the native-backed path is a real software capability in
the retained flagship package.

## 7. Limitations and non-goals

De-Time does not claim:

- to replace specialist libraries in their deepest method-specific domains,
- to make every wrapper as mature as the flagship methods,
- to turn optional backend integrations into fully independent in-house
  implementations,
- to present a large external user community at the current stage.

Adoption is still early. The present submission therefore focuses on software
boundary, installability, documented workflow design, release automation, and
package-level maintainability rather than on claims of large-scale community
uptake.

## 8. Conclusion

De-Time contributes workflow-oriented research software for reproducible
time-series decomposition. Release `0.1.0` emphasizes a canonical `detime`
package identity, a narrower and cleaner public software surface, a separation
from benchmark artifacts, explicit positioning relative to specialist libraries
such as `PySDKit`, `SSALib`, and `sktime`, and a quality story grounded in
install validation, documentation builds, coverage gates, reproducible evidence
artifacts, and selected native-backed acceleration.
