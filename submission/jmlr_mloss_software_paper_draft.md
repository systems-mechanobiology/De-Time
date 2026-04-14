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
rather than a mixed library-plus-benchmark artifact. Version `0.1.1` freezes
packaged JSON schemas with explicit `contract_version` metadata, low-token
result views, a method recommender, a minimal MCP server, deterministic exact
native `SSA`, and selected native-backed acceleration alongside tests,
documentation, and release automation.

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
methods. In the `0.1.1` candidate, those components were moved out of the main
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

The current submission is frozen against version `0.1.1`. Repository metadata,
citation metadata, docs, and reviewer-facing evidence are aligned to that
candidate, and the public GitHub / PyPI release should be cut from the same
commit as `de-time-v0.1.1`. The package includes:

- tests for the retained public interface,
- strict documentation builds,
- wheel and source-distribution validation,
- artifact-layout checks that verify removed benchmark stubs and legacy
  transition modules do not re-enter wheel or sdist payloads,
- `twine check` for release artifacts,
- a coverage gate of `fail_under = 90` on the canonical core-plus-flagship
  coverage scope,
- schema freshness checks for packaged JSON schemas,
- native fallback handling where native kernels are unavailable,
- deterministic exact native `SSA` agreement checks alongside the fast
  approximation path,
- documentation consistency checks,
- release smoke automation,
- optional `.[multivar]` smoke coverage for `MVMD` / `MEMD`,
- reproducible performance snapshot generation.

In the latest local release review run, the gated `detime` core-surface
coverage report reached `93.73%`, while the separate package-wide report
reached `84.00%`.

## 5. Relationship to related software

De-Time is designed to complement specialist libraries rather than replace
them.

| Package | Where it is deeper | De-Time position |
|---|---|---|
| [`statsmodels`](https://www.statsmodels.org/) | mature classical decomposition and modeling | De-Time wraps selected classical methods while standardizing the workflow layer |
| [`PyEMD`](https://github.com/laszukdawid/PyEMD) | deeper EMD-family tooling | De-Time uses EMD-family methods as one family inside a broader workflow contract |
| [`PyWavelets`](https://pywavelets.readthedocs.io/en/latest/) | deeper wavelet transforms and transform-specific APIs | De-Time exposes wavelet decomposition for workflow consistency, not wavelet leadership |
| [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/) | broader signal-decomposition toolkit and optional multivariate backends | De-Time uses `PySDKit` selectively for `MVMD` and `MEMD` while maintaining its own config/result layer |
| [`SSALib`](https://github.com/ADSCIAN/ssalib) | deeper SSA-only environment | De-Time offers SSA as one flagship path inside a cross-family package |
| [`sktime`](https://www.sktime.net/en/stable/) | current maintained VMD reality plus a broader time-series transform ecosystem | De-Time treats the maintained `sktime` VMD path as the relevant comparison rather than relying on the older standalone `vmdpy` identity |

The main software claim is therefore not method-count breadth alone. It is the
combination of:

- a common `DecompositionConfig`,
- a common `DecompResult`,
- one CLI workflow surface,
- one package-level story for native support, profiling, and saved outputs,
- one machine-facing story for schemas, recommendation, and tool-based access.

## 5.1 Method literature and upstream packages

The retained methods in De-Time are attached to explicit literature references
and, where applicable, to the official upstream packages they wrap or compare
against:

- `SSA` / `MSSA`: Golyandina and Zhigljavsky, *Singular Spectrum Analysis for Time Series* ([Springer](https://link.springer.com/book/10.1007/978-3-662-62436-4)); specialist comparison package: [`SSALib`](https://github.com/ADSCIAN/ssalib)
- `STD` / `STDR`: Dudek (2022), *STD: A Seasonal-Trend-Dispersion Decomposition of Time Series* ([arXiv](https://doi.org/10.48550/arXiv.2204.10398))
- `STL` / `ROBUST_STL`: Cleveland et al. (1990), *STL: A Seasonal-Trend Decomposition Procedure Based on LOESS* as exposed through [`statsmodels`](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html)
- `MSTL`: Bandara, Hyndman, and Bergmeir (2021), *MSTL* ([arXiv](https://arxiv.org/abs/2107.13462)); upstream package: [`statsmodels`](https://www.statsmodels.org/)
- `EMD` / `CEEMDAN`: Huang et al. (1998) ([DOI](https://doi.org/10.1098/rspa.1998.0193)) plus the CEEMDAN references exposed in [`PyEMD`](https://pyemd.readthedocs.io/en/latest/ceemdan.html)
- `VMD`: Dragomiretskiy and Zosso (2014) ([DOI](https://doi.org/10.1109/TSP.2013.2288675)); package context: [`vmdpy`](https://github.com/vrcarva/vmdpy) and the maintained [`sktime`](https://www.sktime.net/en/stable/) ecosystem
- `WAVELET`: Mallat (1989) ([IEEE Xplore](https://ieeexplore.ieee.org/document/192463)); upstream package: [`PyWavelets`](https://pywavelets.readthedocs.io/en/latest/)
- `MVMD` / `MEMD`: Rehman and Aftab (2019) ([arXiv](https://arxiv.org/abs/1907.04509)) and Rehman and Mandic (2010) ([DOI](https://doi.org/10.1098/rspa.2009.0502)); optional backend package: [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/)
- `GABOR_CLUSTER`: De-Time-specific experimental path supported by classical Gabor time-frequency ideas ([Gabor 1946 PDF](https://www.rctn.org/w/images/b/b6/Gabor.pdf)) and the [`Faiss`](https://github.com/facebookresearch/faiss) similarity-search library rather than by one canonical decomposition package

## 6. Minimal software evidence

To keep the paper grounded in software behavior rather than in benchmark-score
storytelling, we report a small runtime snapshot from one Windows / Python
3.11.9 release environment of the package:

| Method | Python mean runtime (ms) | Native mean runtime (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 14.239 | 1.833 | 7.770x |
| `STD` | 0.181 | 0.031 | 5.825x |
| `STDR` | 0.192 | 0.021 | 9.319x |

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
time-series decomposition. Version `0.1.1` emphasizes a canonical `detime`
package identity, a narrower and cleaner public software surface, a separation
from benchmark artifacts, explicit positioning relative to specialist libraries
such as `PySDKit`, `SSALib`, and `sktime`, and a quality story grounded in
install validation, documentation builds, schema freshness, dual-scope
coverage reporting, reproducible evidence artifacts, and selected
native-backed acceleration.
