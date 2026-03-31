# Changelog

All notable changes to De-Time are documented in this file.

The project brand is **De-Time**, the PyPI distribution is `de-time`, the
preferred Python import path is `detime`, and the legacy `tsdecomp` import/CLI
aliases remain available for compatibility.

## [0.1.0] - 2026-03-31

Initial standalone package release.

### Added

- standalone `de-time` package metadata and `detime` import surface
- legacy-compatible `tsdecomp` import and CLI aliases
- unified decomposition API centered on `DecompositionConfig`, `DecompResult`,
  and `decompose(...)`
- CLI workflows for `run`, `batch`, `profile`, `eval`, `validate`,
  `run_leaderboard`, and `merge_results`
- native acceleration for `SSA`, `STD`, `STDR`, and `DR_TS_REG`
- multivariate workflows for `MSSA`, `MVMD`, `MEMD`, and channelwise
  `STD` / `STDR`
- agent-friendly package metadata and handoff docs
- standalone repository scaffolding for CI, wheel publishing, docs deployment,
  and release publishing

### Included method surface

- seasonal-trend methods: `STL`, `MSTL`, `ROBUST_STL`, `STD`, `STDR`
- subspace methods: `SSA`, `MSSA`
- adaptive/modal methods: `EMD`, `CEEMDAN`, `VMD`, `MVMD`, `MEMD`
- additional workflows: `WAVELET`, `MA_BASELINE`, `GABOR_CLUSTER`,
  `DR_TS_REG`, `DR_TS_AE`, `SL_LIB`

### Packaging and quality

- wheel-first packaging via `scikit-build-core`, `pybind11`, and `cibuildwheel`
- package-level test suite, docs tree, examples, and GitHub Actions skeletons
- source-distribution hygiene for standalone release artifacts
