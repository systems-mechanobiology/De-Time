# Method References

This page is generated from `MethodRegistry.list_catalog()` so citations,
upstream package links, and method metadata stay aligned.

Current package version target: `0.1.1`.

These links cover the method families and upstream packages used or compared
in the public De-Time workflow surface. `MA_BASELINE` is an in-package smoke
baseline and therefore has no separate upstream citation.

## Flagship methods

### `MSSA`

- Summary: Multivariate SSA for shared-structure decomposition across channels.
- Optional/runtime dependencies: none

Primary references:
- [Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series](https://link.springer.com/book/10.1007/978-3-662-62436-4) - Primary SSA/MSSA reference used for the multivariate extension.

Related packages:
- [SSALib](https://github.com/ADSCIAN/ssalib) - SSA-focused package; useful comparison point for SSA-family workflows.

### `SSA`

- Summary: Singular spectrum analysis for structured univariate decomposition.
- Optional/runtime dependencies: none

Primary references:
- [Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series](https://link.springer.com/book/10.1007/978-3-662-62436-4) - Primary SSA reference; the second edition also covers multivariate SSA (MSSA).

Related packages:
- [SSALib](https://github.com/ADSCIAN/ssalib) - Specialist SSA package used as an external comparison point.

### `STD`

- Summary: Fast seasonal-trend decomposition with dispersion-aware diagnostics.
- Optional/runtime dependencies: none

Primary references:
- [Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series](https://doi.org/10.48550/arXiv.2204.10398) - Primary reference for STD and the robust seasonal-trend-dispersion family.

Related packages:
- none declared

### `STDR`

- Summary: Robust seasonal-trend decomposition for noisier periodic signals.
- Optional/runtime dependencies: none

Primary references:
- [Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series](https://doi.org/10.48550/arXiv.2204.10398) - Primary reference for STD and the robust seasonal-trend-dispersion family.

Related packages:
- none declared

## Stable wrappers and retained methods

### `CEEMDAN`

- Summary: Noise-assisted EMD variant for more stable IMF extraction.
- Optional/runtime dependencies: PyEMD

Primary references:
- [Torres et al. (2011), A complete ensemble empirical mode decomposition with adaptive noise](https://pyemd.readthedocs.io/en/latest/ceemdan.html) - PyEMD CEEMDAN docs cite the original ICASSP 2011 paper.
- [Colominas, Schlotthauer, and Torres (2014), Improved complete ensemble EMD: A suitable tool for biomedical signal processing](https://pyemd.readthedocs.io/en/latest/ceemdan.html) - Improved CEEMDAN variant adopted by the PyEMD implementation used by De-Time.

Related packages:
- [PyEMD](https://github.com/laszukdawid/PyEMD) - Upstream Python package wrapped by De-Time for EMD-family methods.

### `EMD`

- Summary: Empirical mode decomposition under the De-Time result contract.
- Optional/runtime dependencies: PyEMD

Primary references:
- [Huang et al. (1998), The empirical mode decomposition and the Hilbert spectrum for nonlinear and non-stationary time series analysis](https://doi.org/10.1098/rspa.1998.0193) - Primary empirical mode decomposition reference.

Related packages:
- [PyEMD](https://github.com/laszukdawid/PyEMD) - Upstream Python package wrapped by De-Time for EMD-family methods.

### `MA_BASELINE`

- Summary: Simple moving-average baseline for smoke tests and lightweight workflows.
- Optional/runtime dependencies: none

Primary references:
- none declared

Related packages:
- none declared

### `MSTL`

- Summary: Statsmodels MSTL wrapped into the De-Time workflow surface.
- Optional/runtime dependencies: statsmodels

Primary references:
- [Bandara, Hyndman, and Bergmeir (2021), MSTL: A Seasonal-Trend Decomposition Algorithm for Time Series with Multiple Seasonal Patterns](https://arxiv.org/abs/2107.13462) - Primary MSTL reference used by the statsmodels implementation.

Related packages:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream MSTL implementation.

### `ROBUST_STL`

- Summary: Robust STL-style decomposition wrapped for reproducible workflows.
- Optional/runtime dependencies: statsmodels

Primary references:
- [Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html) - Robust STL in De-Time builds on the same STL literature and upstream implementation family.

Related packages:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream STL implementation family.

### `STL`

- Summary: Classical STL wrapped into the De-Time workflow contract.
- Optional/runtime dependencies: statsmodels

Primary references:
- [Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html) - Statsmodels STL docs cite the original Journal of Official Statistics paper.

Related packages:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream STL implementation.

### `VMD`

- Summary: Variational mode decomposition integrated into the common workflow layer.
- Optional/runtime dependencies: vmdpy, sktime

Primary references:
- [Dragomiretskiy and Zosso (2014), Variational Mode Decomposition](https://doi.org/10.1109/TSP.2013.2288675) - Primary variational mode decomposition reference.

Related packages:
- [sktime](https://www.sktime.net/en/stable/) - Current maintained ecosystem for `vmdpy`, which the archived project directs users toward.
- [vmdpy](https://github.com/vrcarva/vmdpy) - Archived Python VMD package used by the current De-Time wrapper.

### `WAVELET`

- Summary: Wavelet-based decomposition exposed through the common output contract.
- Optional/runtime dependencies: PyWavelets

Primary references:
- [Mallat (1989), A theory for multiresolution signal decomposition: the wavelet representation](https://ieeexplore.ieee.org/document/192463) - Foundational wavelet multiresolution reference.
- [Lee et al. (2019), PyWavelets: A Python package for wavelet analysis](https://doi.org/10.21105/joss.01237) - Package citation for the upstream wavelet implementation used by De-Time.

Related packages:
- [PyWavelets](https://pywavelets.readthedocs.io/en/latest/) - Official documentation for the upstream wavelet package.

## Optional backend methods

### `MEMD`

- Summary: Optional multivariate EMD backend for shared oscillatory structure.
- Optional/runtime dependencies: PySDKit

Primary references:
- [Rehman and Mandic (2010), Multivariate empirical mode decomposition](https://doi.org/10.1098/rspa.2009.0502) - Primary MEMD reference for the multivariate EMD extension.

Related packages:
- [PySDKit](https://pysdkit.readthedocs.io/en/latest/) - Optional multivariate backend used by De-Time for MEMD.

### `MVMD`

- Summary: Optional multivariate VMD backend for shared frequency structure.
- Optional/runtime dependencies: PySDKit

Primary references:
- [Rehman and Aftab (2019), Multivariate Variational Mode Decomposition](https://arxiv.org/abs/1907.04509) - Primary MVMD reference for the multivariate VMD extension.

Related packages:
- [PySDKit](https://pysdkit.readthedocs.io/en/latest/) - Optional multivariate backend used by De-Time for MVMD.

## Experimental methods

### `GABOR_CLUSTER`

- Summary: Experimental clustering-based decomposition path.
- Optional/runtime dependencies: faiss

Primary references:
- [Gabor (1946), Theory of Communication](https://www.rctn.org/w/images/b/b6/Gabor.pdf) - Historical reference for the Gabor time-frequency representation family.
- [Douze et al. (2024), The Faiss library](https://arxiv.org/abs/2401.08281) - Reference for the similarity-search backend used by the experimental clustering path.

Related packages:
- [Faiss](https://github.com/facebookresearch/faiss) - Vector similarity search library required by the experimental clustering backend.
