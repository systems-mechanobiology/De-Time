# De-Time Software Evidence Snapshot

This note records the reviewer-facing software evidence for the current
`0.1.1` submission target.

## Install and release story

- Public install path in docs: `pip install de-time`
- Submission target version: `0.1.1`
- Candidate freeze date: April 14, 2026
- Planned public release tag from the frozen candidate: `de-time-v0.1.1`
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
- `pytest tests/optional/test_multivar_optional_backends.py -q`
- `pytest tests --cov=detime --cov-config=.coveragerc`
- `pytest tests --cov=detime --cov-config=.coveragerc.package`
- `python scripts/generate_schema_assets.py --check`
- `python scripts/generate_schema_assets.py`
- `python scripts/generate_tutorial_assets.py`
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
- Separate reviewer-facing package-wide report: yes
- CLI, I/O, visualization helpers, and optional wrappers remain tested, but
  they are not counted inside the gated coverage denominator
- Latest gated local core-surface coverage: `93.73%`
- Latest local package-wide coverage: `84.00%`

## Related software matrix

| Package | Deeper strength | De-Time distinction |
|---|---|---|
| [`statsmodels`](https://www.statsmodels.org/) | mature classical decomposition and modeling | De-Time standardizes a cross-family workflow layer |
| [`PyEMD`](https://github.com/laszukdawid/PyEMD) | deeper EMD-family tooling | De-Time places EMD-family methods inside the same config/result/CLI contract as other families |
| [`PyWavelets`](https://pywavelets.readthedocs.io/en/latest/) | deeper wavelet transforms and wavelet-specific APIs | De-Time treats wavelets as one workflow option rather than a wavelet-first toolkit |
| [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/) | broader signal-decomposition toolkit, including optional multivariate methods | De-Time uses `PySDKit` selectively while keeping a time-series-centered package interface |
| [`SSALib`](https://github.com/ADSCIAN/ssalib) | deeper SSA-only environment | De-Time offers SSA inside a broader decomposition workflow package |
| [`sktime`](https://www.sktime.net/en/stable/) | current maintained VMD path and broader time-series transformation ecosystem | De-Time compares its VMD path against `sktime`, not only against the old standalone `vmdpy` identity |

## Method and upstream references

- `SSA` / `MSSA`: Golyandina and Zhigljavsky, *Singular Spectrum Analysis for Time Series* ([Springer](https://link.springer.com/book/10.1007/978-3-662-62436-4)); specialist comparison point: [`SSALib`](https://github.com/ADSCIAN/ssalib)
- `STD` / `STDR`: Dudek (2022), *STD: A Seasonal-Trend-Dispersion Decomposition of Time Series* ([arXiv](https://doi.org/10.48550/arXiv.2204.10398))
- `STL` / `ROBUST_STL`: Cleveland et al. (1990), *STL: A Seasonal-Trend Decomposition Procedure Based on LOESS* via [`statsmodels` STL docs](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html)
- `MSTL`: Bandara, Hyndman, and Bergmeir (2021), *MSTL* ([arXiv](https://arxiv.org/abs/2107.13462)); upstream package: [`statsmodels`](https://www.statsmodels.org/)
- `EMD`: Huang et al. (1998), empirical mode decomposition ([DOI](https://doi.org/10.1098/rspa.1998.0193)); upstream package: [`PyEMD`](https://github.com/laszukdawid/PyEMD)
- `CEEMDAN`: Torres et al. (2011) and Colominas et al. (2014) via [`PyEMD` CEEMDAN docs](https://pyemd.readthedocs.io/en/latest/ceemdan.html)
- `VMD`: Dragomiretskiy and Zosso (2014), variational mode decomposition ([DOI](https://doi.org/10.1109/TSP.2013.2288675)); implementation context: [`vmdpy`](https://github.com/vrcarva/vmdpy) and maintained [`sktime`](https://www.sktime.net/en/stable/) ecosystem
- `WAVELET`: Mallat (1989), multiresolution wavelet representation ([IEEE Xplore](https://ieeexplore.ieee.org/document/192463)); upstream package: [`PyWavelets`](https://pywavelets.readthedocs.io/en/latest/)
- `MVMD`: Rehman and Aftab (2019), multivariate VMD ([arXiv](https://arxiv.org/abs/1907.04509)); optional backend: [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/)
- `MEMD`: Rehman and Mandic (2010), multivariate EMD ([DOI](https://doi.org/10.1098/rspa.2009.0502)); optional backend: [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/)

## Minimal runtime evidence

These measurements come from one Windows / Python 3.11.9 release environment of
the package. They are software-validation evidence, not a universal benchmark
claim.

| Method | Python mean runtime (ms) | Native mean runtime (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 14.239 | 1.833 | 7.770x |
| `STD` | 0.181 | 0.031 | 5.825x |
| `STDR` | 0.192 | 0.021 | 9.319x |

## Early adoption surface

- public repository with contributor guide, issue templates, and GitHub Discussions,
- public GitHub Pages documentation site,
- explicit release and publishing documentation,
- transparent machine-contract, schema, and evidence-generation scripts.

We present this as early-adoption infrastructure and release-engineering
evidence, not as proof of a large external user community.
