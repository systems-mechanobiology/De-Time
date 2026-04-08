# De-Time: Workflow-Oriented Research Software for Reproducible Time-Series Decomposition

## Abstract

De-Time is open-source research software for reproducible time-series
decomposition. The package does not introduce a new decomposition algorithm.
Instead, it provides a coherent software surface for configuring, running,
profiling, and saving decomposition workflows across several retained method
families. The canonical package namespace is `detime`, while `tsdecomp`
remains only as a deprecated top-level import and CLI alias. The reviewed
software surface centers on four flagship workflows, `SSA`, `STD`, `STDR`, and
`MSSA`, and retains additional wrapper-based integrations with explicit
maturity labels. Benchmark-oriented artifact code was separated into a
companion repository so that the main package is a clean software submission
rather than a mixed library-plus-benchmark artifact. The current review
snapshot is installable from GitHub, includes strict documentation builds,
wheel and source-distribution checks, artifact-layout validation, a coverage
gate on the canonical core-plus-flagship path, and selected native-backed
acceleration for retained flagship methods.

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
- selected native acceleration where it materially improves throughput.

This workflow layer is also relevant to machine learning practice. In typical
ML pipelines, decomposition is used for denoising, feature extraction,
representation shaping, and preprocessing ahead of downstream estimators.
De-Time targets that workflow friction directly by standardizing configuration,
results, profiling, and saved outputs across retained decomposition families.

## 2. Public Software Surface

The canonical public interface is built around:

- `DecompositionConfig` for method and runtime configuration,
- `DecompResult` for standardized outputs,
- `decompose()` for dispatch,
- a CLI with `run`, `batch`, `profile`, and `version`,
- native capability helpers for the retained flagship methods.

The canonical package identity is now `detime`. The older `tsdecomp` namespace
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

## 3. Package Boundary and Relation to Earlier Artifacts

Earlier repository states mixed software-package concerns with benchmark
artifacts, synthetic generators, leaderboard helpers, and benchmark-derived
methods. In the reviewed revision, those components were moved out of the main
package boundary into the companion repository `de-time-bench`.

The main De-Time package no longer ships:

- leaderboard orchestration as part of the public surface,
- benchmark configuration helpers as public package features,
- benchmark-derived methods `DR_TS_REG`, `DR_TS_AE`, and `SL_LIB`,
- transition-era `tsdecomp` submodules outside the top-level import and CLI
  compatibility path,
- benchmark-only synthetic artifact code inside the installable package.

That split is central to the present submission. The software submission is now
the installable decomposition package itself, not a repackaged benchmark stack.

## 4. Quality Discipline and Release Story

The current public installation story is intentionally conservative. Because a
PyPI release of `de-time` is still pending, the reviewed documentation uses a
GitHub source install rather than claiming a `pip install de-time` route that
does not yet exist.

The current `0.1.0` version string therefore identifies the reviewed snapshot
rather than a completed public release. The corresponding Git tag, GitHub
release, and PyPI publication are intentionally deferred until the final
release gate.

The reviewed package includes:

- tests for the retained public interface,
- strict documentation builds,
- wheel and source-distribution validation,
- artifact-layout checks that verify removed benchmark stubs and legacy
  transition modules do not re-enter wheel or sdist payloads,
- `twine check` for release artifacts,
- a coverage gate of `fail_under = 90` on the canonical core-plus-flagship
  coverage scope,
- native fallback handling where native kernels are unavailable.

In the latest local review run, the gated `detime` coverage report reached
`91.40%`.

## 5. Relationship to Related Software

De-Time is designed to complement specialist libraries rather than replace
them.

| Package | Where it is deeper | De-Time position |
|---|---|---|
| `statsmodels` | mature classical decomposition and modeling | De-Time wraps selected classical methods while standardizing the workflow layer |
| `PyEMD` | deeper EMD-family tooling | De-Time uses EMD-family methods as one family inside a broader workflow contract |
| `PyWavelets` | deeper wavelet transforms and transform-specific APIs | De-Time exposes wavelet decomposition for workflow consistency, not wavelet leadership |
| `PySDKit` | broader signal-decomposition toolkit and optional multivariate backends | De-Time uses `PySDKit` selectively for `MVMD` and `MEMD` while maintaining its own config/result layer |
| `SSALib` | deeper SSA-only environment | De-Time offers SSA as one flagship path inside a cross-family package |
| `sktime` | current maintained VMD reality plus a broader time-series transform ecosystem | De-Time now treats the maintained `sktime` VMD path as the relevant comparison rather than relying on the older standalone `vmdpy` identity |

The main software claim is therefore not method-count breadth alone. It is the
combination of:

- a common `DecompositionConfig`,
- a common `DecompResult`,
- one CLI workflow surface,
- one package-level story for native support, profiling, and saved outputs.

## 6. Minimal Software Evidence

To keep the paper grounded in software behavior rather than in benchmark-score
storytelling, we report a small runtime snapshot from one Windows / Python
3.11 wheel installation of the reviewed package:

| Method | Python mean runtime (ms) | Native mean runtime (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 968.988 | 574.751 | 1.69x |
| `STD` | 1.449 | 0.060 | 24.30x |
| `STDR` | 1.767 | 0.064 | 27.81x |

These numbers are not presented as universal performance claims. They are
included to show that the native-backed path is a real software capability in
the retained flagship package.

## 7. Limitations and Non-Goals

De-Time does not claim:

- to replace specialist libraries in their deepest method-specific domains,
- to make every wrapper as mature as the flagship methods,
- to turn optional backend integrations into fully independent in-house
  implementations,
- to present a large external user community at the current stage.

Adoption is still early. The present submission therefore focuses on software
boundary, installability, documented workflow design, and package-level
maintainability rather than on claims of large-scale community uptake.

## 8. Conclusion

De-Time contributes workflow-oriented research software for reproducible
time-series decomposition. The reviewed revision emphasizes a canonical
`detime` package identity, a narrower and cleaner public software surface, a
separation from benchmark artifacts, explicit positioning relative to
specialist libraries such as `PySDKit`, `SSALib`, and `sktime`, and a quality
story grounded in install validation, documentation builds, coverage gates, and
selected native-backed acceleration.
