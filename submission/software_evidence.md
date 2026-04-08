# De-Time Software Evidence Snapshot

This note records the reviewer-facing software evidence for the current
release.

## Install and release story

- Public install path in docs: `pip install de-time`
- Public release tag: `de-time-v0.1.0`
- Release date: April 8, 2026
- Canonical import: `detime`
- Deprecated compatibility scope: top-level `tsdecomp` import and CLI only

## Package-boundary evidence

- `src/detime/` is the canonical implementation path
- `src/tsdecomp/` is retained only for the top-level compatibility entrypoints
- benchmark-derived methods are not part of the main package surface
- benchmark-oriented artifact code now lives in the companion repository
  `systems-mechanobiology/de-time-bench`
- wheel and sdist payloads exclude transition-era `tsdecomp` submodules and
  removed benchmark stubs such as `detime.leaderboard`

## Current quality checks

- `pytest tests -q`
- `pytest tests --cov=detime --cov-config=.coveragerc`
- `mkdocs build --strict`
- `python -m build`
- `python scripts/check_dist_contents.py dist/*.tar.gz dist/*.whl`
- `python scripts/check_doc_consistency.py`
- `python scripts/release_smoke_matrix.py`
- `python scripts/generate_performance_snapshot.py`
- `python -m twine check dist/*`

## Coverage discipline

- Coverage gate: `fail_under = 90`
- Coverage scope: canonical `detime` core-plus-flagship path
- CLI, I/O, visualization helpers, and optional wrappers remain tested, but
  they are not counted inside the gated coverage denominator
- Latest gated local coverage result: `93.20%`

## Related software matrix

| Package | Deeper strength | De-Time distinction |
|---|---|---|
| `statsmodels` | mature classical decomposition and modeling | De-Time standardizes a cross-family workflow layer |
| `PyEMD` | deeper EMD-family tooling | De-Time places EMD-family methods inside the same config/result/CLI contract as other families |
| `PyWavelets` | deeper wavelet transforms and wavelet-specific APIs | De-Time treats wavelets as one workflow option rather than a wavelet-first toolkit |
| `PySDKit` | broader signal-decomposition toolkit, including optional multivariate methods | De-Time uses `PySDKit` selectively while keeping a time-series-centered package interface |
| `SSALib` | deeper SSA-only environment | De-Time offers SSA inside a broader decomposition workflow package |
| `sktime` | current maintained VMD path and broader time-series transformation ecosystem | De-Time compares its VMD path against `sktime`, not only against the old standalone `vmdpy` identity |

## Minimal runtime evidence

These measurements come from one Windows / Python 3.11.9 release environment of
the package. They are software-validation evidence, not a universal benchmark
claim.

| Method | Python mean runtime (ms) | Native mean runtime (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 13.815 | 1.910 | 7.232x |
| `STD` | 0.178 | 0.036 | 4.962x |
| `STDR` | 0.183 | 0.019 | 9.599x |

## Early adoption surface

- public repository with contributor guide, issue templates, and GitHub Discussions,
- public release notes at `https://github.com/systems-mechanobiology/De-Time/releases/tag/de-time-v0.1.0`,
- public PyPI distribution record,
- public GitHub Pages documentation site.
