# De-Time Software Evidence Snapshot

This note records the reviewer-facing software evidence for the current
revision.

## Install and release story

- Public install path in docs: GitHub source install
- Reason: a PyPI release of `de-time` is still pending, so the docs avoid a
  broken `pip install de-time` claim
- Canonical import: `detime`
- Deprecated alias: `tsdecomp`

## Package-boundary evidence

- `src/detime/` is the canonical implementation path
- `src/tsdecomp/` is retained only as a deprecated compatibility alias
- benchmark-derived methods `DR_TS_REG`, `DR_TS_AE`, and `SL_LIB` were removed
  from the main package surface
- benchmark-oriented artifact code now lives in the companion repository
  `de-time-bench`

## Current quality checks

- `pytest tests -q`
- `pytest tests --cov=detime --cov-config=.coveragerc`
- `mkdocs build --strict`
- `python -m build`
- `python -m twine check dist/*`
- wheel smoke install
- sdist smoke install

## Coverage discipline

- Coverage gate: `fail_under = 90`
- Coverage scope: canonical `detime` core-plus-flagship path
- Optional wrappers, visualization helpers, and CLI/I/O workflows are still
  tested, but they are not counted inside the gated coverage scope
- Latest gated local coverage result: `91.25%`

## Related software matrix

| Package | Deeper strength | De-Time distinction |
|---|---|---|
| `statsmodels` | mature classical decomposition and modeling | De-Time standardizes a cross-family workflow layer |
| `PyEMD` | deeper EMD-family tooling | De-Time places EMD-family methods inside the same config/result/CLI contract as other families |
| `PyWavelets` | deeper wavelet transforms and wavelet-specific APIs | De-Time treats wavelets as one workflow option rather than a wavelet-first toolkit |
| `PySDKit` | broader signal-decomposition toolkit, including optional multivariate methods | De-Time uses `PySDKit` selectively while keeping a time-series-centered package interface |
| `SSALib` | deeper SSA-only environment | De-Time offers SSA inside a broader decomposition workflow package |
| `sktime` | current maintained VMD path and broader time-series transformation ecosystem | De-Time now compares its VMD path against `sktime`, not only against the old standalone `vmdpy` identity |

## Minimal runtime evidence

These measurements come from one Windows / Python 3.11 wheel installation of
the reviewed package. They are software-validation evidence, not a universal
benchmark claim.

| Method | Python mean runtime (ms) | Native mean runtime (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 968.988 | 574.751 | 1.69x |
| `STD` | 1.449 | 0.060 | 24.30x |
| `STDR` | 1.767 | 0.064 | 27.81x |
