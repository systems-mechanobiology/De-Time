# De-Time: Workflow-Oriented Research Software for Reproducible Time-Series Decomposition

## Abstract

De-Time is an open-source software package for reproducible time-series
decomposition. The package does not introduce a new decomposition algorithm.
Instead, it provides a coherent software surface for applying, comparing, and
profiling decomposition workflows across univariate, channelwise multivariate,
and joint multivariate settings. De-Time standardizes configuration,
result-return conventions, CLI behavior, saved outputs, and native capability
reporting. The canonical package namespace is `detime`, while the older
`tsdecomp` namespace is retained only as a deprecated compatibility alias. The
main package is centered on four flagship workflows, `SSA`, `STD`, `STDR`, and
`MSSA`, and exposes additional wrapper-based integrations for specialist
methods. Benchmark orchestration and benchmark-derived methods were separated
into a companion repository so that the core software package remains a clean,
installable, and reviewable research software artifact.

## 1. Introduction

Time-series decomposition remains important across scientific computing,
signal-processing, and data-analysis workflows. In practice, however,
decomposition software is fragmented. Researchers often combine specialist
libraries, notebook utilities, and local scripts to obtain a full workflow for
configuration, decomposition, visualization, and result export. This makes it
harder to compare methods, preserve metadata, and hand a workflow to another
researcher in a reproducible form.

De-Time addresses that software problem. Its primary goal is to provide one
consistent package surface for decomposition workflows. The software contribution
is therefore architectural and workflow-oriented rather than algorithmic.

## 2. Software Overview

De-Time exposes one public interface built around:

- `DecompositionConfig` for method and runtime configuration,
- `DecompResult` for standardized outputs,
- `decompose()` for dispatching decomposition runs,
- a CLI with `run`, `batch`, `profile`, and `version`,
- native capability helpers for selected flagship methods.

The canonical import path is `detime`. A deprecated `tsdecomp` compatibility
package re-exports the same public surface and warns on use.

The package currently centers on four flagship workflows:

- `SSA` for interpretable single-series decomposition,
- `STD` for seasonal-trend decomposition with stable defaults,
- `STDR` for the same decomposition family with shared seasonal-shape handling,
- `MSSA` for joint multichannel decomposition.

Additional integrations are retained for specialist use cases, including `STL`,
`MSTL`, `EMD`, `CEEMDAN`, `VMD`, `WAVELET`, `MVMD`, `MEMD`, `MA_BASELINE`, and
`GABOR_CLUSTER`. These are documented as wrappers or optional paths rather than
as co-equal flagship methods.

## 3. Package Boundary

An important revision in the current submission is the separation of the core
software package from benchmark-oriented artifacts. Earlier repository layouts
mixed library code with synthetic benchmark generators, leaderboard helpers,
and benchmark-derived methods. For the present submission, those components were
moved into a companion repository, `de-time-bench`.

This means the main De-Time package no longer ships:

- leaderboard orchestration,
- benchmark configuration helpers,
- benchmark-derived methods `DR_TS_REG`, `DR_TS_AE`, and `SL_LIB`,
- benchmark visualizations as part of the public package surface.

That split is central to the software positioning of this submission. The main
repository is now a software package first, with clear install, import, test,
and documentation boundaries.

## 4. Quality and Maintainability

The repository includes:

- automated tests for the retained public interface,
- CI for package builds, documentation builds, and distribution validation,
- strict documentation builds with MkDocs,
- source and wheel packaging checks,
- native-extension fallbacks where native kernels are unavailable.

Coverage targets are applied to the canonical `detime` package rather than to
the deprecated compatibility alias.

## 5. Relationship to Related Software

De-Time is designed to complement, not replace, specialist libraries.

- `statsmodels` remains the upstream reference for classical STL-style methods.
- `PyEMD` remains the upstream reference for EMD-family methods.
- `PyWavelets` remains the upstream reference for wavelet transforms.
- `PySDKit` provides optional multivariate backends for selected workflows.
- SSA-focused packages remain valuable when an SSA-only environment is desired.

De-Time adds a workflow layer across these tools by standardizing configuration,
results, and package-level ergonomics.

## 6. Conclusion

De-Time contributes reusable research software for time-series decomposition by
providing a coherent software interface, clear package boundary, and documented
workflow surface. The current revision emphasizes the canonical `detime`
namespace, the deprecated status of `tsdecomp`, the flagship-method focus on
`SSA`, `STD`, `STDR`, and `MSSA`, and the separation of benchmark artifacts into
the companion `de-time-bench` repository.
