# Changelog

All notable changes to De-Time are documented in this file.

The project brand is **De-Time**, the PyPI distribution is `de-time`, the
preferred Python import path is `detime`, and the legacy `tsdecomp` import/CLI
aliases remain available for compatibility.

## [0.1.0] - Reviewed snapshot (not yet tagged or published)

This version string currently identifies the reviewed GitHub snapshot. Formal
Git tag, GitHub release, and PyPI publication are still pending.

### Public surface

- canonical `de-time` package metadata and `detime` import surface
- deprecated top-level `tsdecomp` import and CLI aliases
- unified decomposition API centered on `DecompositionConfig`, `DecompResult`,
  and `decompose(...)`
- CLI workflows for `run`, `batch`, `profile`, and `version`
- native acceleration for `SSA`, `STD`, and `STDR`
- multivariate workflows for `MSSA`, `MVMD`, `MEMD`, and channelwise `STD`

### Included method surface

- seasonal-trend methods: `STL`, `MSTL`, `STD`, `STDR`
- subspace methods: `SSA`, `MSSA`
- adaptive/modal methods: `EMD`, `CEEMDAN`, `VMD`, `MVMD`, `MEMD`
- additional workflows: `WAVELET`, `MA_BASELINE`, `GABOR_CLUSTER`

### Packaging and quality

- wheel-first packaging via `scikit-build-core`, `pybind11`, and `cibuildwheel`
- package-level test suite, docs tree, examples, and GitHub Actions workflows
- coverage gate on the canonical core-plus-flagship surface
- artifact-layout checks for wheel and sdist outputs
- source-distribution hygiene for the reviewed standalone package boundary

### Removed from install artifacts

- benchmark configuration helpers and leaderboard stubs
- benchmark-derived methods `DR_TS_REG`, `DR_TS_AE`, and `SL_LIB`
- transition-era `tsdecomp` submodules outside the top-level import and CLI
  compatibility path
