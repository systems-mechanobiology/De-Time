# Method Cards

This page is generated from `MethodRegistry.list_catalog()` so the human-facing
method cards stay aligned with the machine-facing catalog contract.

Current package version target: `0.1.1`.

Source citations and official upstream package links are collected in
[Method References](method-references.md).

The `tsdecomp` top-level alias remains compatibility-only through `0.1.x` and is
not the canonical surface for any method listed below.

## Flagship methods

### `MSSA`

- Family: `SSA`
- Input mode: `multivariate`
- Maturity: `flagship`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `shared-model`
- Native-backed: `False`
- Minimum length hint: `24`
- Optional dependencies: none
- Summary: Multivariate SSA for shared-structure decomposition across channels.

Assumptions:
- expects a 2D array with at least two aligned channels
- works best when window and rank reflect the dominant temporal structure
- MSSA should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- multivariate component recovery
- shared seasonal structure across channels
- accuracy-first multivariate workflows

Typical failure modes:
- too few channels for MSSA
- window or rank too small for the shared structure

Not recommended for:
- single-series workflows where a univariate flagship method is sufficient
- very short series that cannot support a sensible window length

Method references:
- [Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series](https://link.springer.com/book/10.1007/978-3-662-62436-4) - Primary SSA/MSSA reference used for the multivariate extension.

Related package links:
- [SSALib](https://github.com/ADSCIAN/ssalib) - SSA-focused package; useful comparison point for SSA-family workflows.

### `SSA`

- Family: `SSA`
- Input mode: `univariate`
- Maturity: `flagship`
- Implementation: `native-backed`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `True`
- Minimum length hint: `24`
- Optional dependencies: none
- Summary: Singular spectrum analysis for structured univariate decomposition.

Assumptions:
- expects one decomposed series at a time
- works best when window and rank reflect the dominant temporal structure
- SSA should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- accuracy-first univariate decomposition
- component recovery
- season-trend separation with structured signals

Typical failure modes:
- window too small for the dominant period
- rank or grouping chosen inconsistently with the signal structure

Not recommended for:
- shared-model multivariate decomposition problems
- very short series that cannot support a sensible window length

Method references:
- [Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series](https://link.springer.com/book/10.1007/978-3-662-62436-4) - Primary SSA reference; the second edition also covers multivariate SSA (MSSA).

Related package links:
- [SSALib](https://github.com/ADSCIAN/ssalib) - Specialist SSA package used as an external comparison point.

### `STD`

- Family: `SeasonalTrend`
- Input mode: `channelwise`
- Maturity: `flagship`
- Implementation: `native-backed`
- Dependency tier: `core`
- Multivariate support: `channelwise`
- Native-backed: `True`
- Minimum length hint: `8`
- Optional dependencies: none
- Summary: Fast seasonal-trend decomposition with dispersion-aware diagnostics.

Assumptions:
- treats each channel independently under one shared method surface
- works best when one seasonal period or block structure is reasonably stable
- STD should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- fast seasonal-trend baselines
- channelwise multivariate workflows
- native-backed production paths

Typical failure modes:
- period omitted or mis-specified
- shared seasonal structure changing too quickly across cycles

Not recommended for:
- problems that require one shared latent model across channels
- series where the dominant period is unknown and cannot be inferred reliably

Method references:
- [Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series](https://doi.org/10.48550/arXiv.2204.10398) - Primary reference for STD and the robust seasonal-trend-dispersion family.

Related package links:
- none declared

### `STDR`

- Family: `SeasonalTrend`
- Input mode: `channelwise`
- Maturity: `flagship`
- Implementation: `native-backed`
- Dependency tier: `core`
- Multivariate support: `channelwise`
- Native-backed: `True`
- Minimum length hint: `8`
- Optional dependencies: none
- Summary: Robust seasonal-trend decomposition for noisier periodic signals.

Assumptions:
- treats each channel independently under one shared method surface
- works best when one seasonal period or block structure is reasonably stable
- STDR should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- robust seasonal-trend decomposition
- channelwise multivariate workflows
- native-backed seasonal structure recovery

Typical failure modes:
- period omitted or mis-specified
- heavy structural breaks that violate shared seasonal assumptions

Not recommended for:
- problems that require one shared latent model across channels
- series where the dominant period is unknown and cannot be inferred reliably

Method references:
- [Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series](https://doi.org/10.48550/arXiv.2204.10398) - Primary reference for STD and the robust seasonal-trend-dispersion family.

Related package links:
- none declared

## Stable wrappers and retained methods

### `CEEMDAN`

- Family: `EMD`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `24`
- Optional dependencies: PyEMD
- Summary: Noise-assisted EMD variant for more stable IMF extraction.

Assumptions:
- expects one decomposed series at a time
- assumes oscillatory modes are meaningful enough to separate adaptively
- CEEMDAN should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- noise-assisted EMD workflows
- adaptive decomposition with improved IMF stability

Typical failure modes:
- high runtime on long series
- parameter choices that over-fragment signal modes

Not recommended for:
- shared-model multivariate decomposition problems

Method references:
- [Torres et al. (2011), A complete ensemble empirical mode decomposition with adaptive noise](https://pyemd.readthedocs.io/en/latest/ceemdan.html) - PyEMD CEEMDAN docs cite the original ICASSP 2011 paper.
- [Colominas, Schlotthauer, and Torres (2014), Improved complete ensemble EMD: A suitable tool for biomedical signal processing](https://pyemd.readthedocs.io/en/latest/ceemdan.html) - Improved CEEMDAN variant adopted by the PyEMD implementation used by De-Time.

Related package links:
- [PyEMD](https://github.com/laszukdawid/PyEMD) - Upstream Python package wrapped by De-Time for EMD-family methods.

### `EMD`

- Family: `EMD`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `16`
- Optional dependencies: PyEMD
- Summary: Empirical mode decomposition under the De-Time result contract.

Assumptions:
- expects one decomposed series at a time
- assumes oscillatory modes are meaningful enough to separate adaptively
- EMD should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- adaptive decomposition of nonlinear signals
- IMF-oriented exploratory analysis

Typical failure modes:
- mode mixing
- short or heavily noisy series that destabilize IMF extraction

Not recommended for:
- shared-model multivariate decomposition problems

Method references:
- [Huang et al. (1998), The empirical mode decomposition and the Hilbert spectrum for nonlinear and non-stationary time series analysis](https://doi.org/10.1098/rspa.1998.0193) - Primary empirical mode decomposition reference.

Related package links:
- [PyEMD](https://github.com/laszukdawid/PyEMD) - Upstream Python package wrapped by De-Time for EMD-family methods.

### `MA_BASELINE`

- Family: `Baseline`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `4`
- Optional dependencies: none
- Summary: Simple moving-average baseline for smoke tests and lightweight workflows.

Assumptions:
- expects one decomposed series at a time
- assumes a coarse baseline is acceptable as a sanity check
- MA_BASELINE should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- sanity checks
- lightweight baseline decomposition

Typical failure modes:
- window too large for the series length
- oversmoothing when fine seasonal structure matters

Not recommended for:
- shared-model multivariate decomposition problems

Method references:
- none declared

Related package links:
- none declared

### `MSTL`

- Family: `SeasonalTrend`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `wrapper`
- Dependency tier: `core-upstream`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `24`
- Optional dependencies: statsmodels
- Summary: Statsmodels MSTL wrapped into the De-Time workflow surface.

Assumptions:
- expects one decomposed series at a time
- works best when one seasonal period or block structure is reasonably stable
- MSTL should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- multiple seasonalities in univariate data
- classical decomposition baselines

Typical failure modes:
- seasonal periods not provided
- nonstationary structure beyond classical assumptions

Not recommended for:
- shared-model multivariate decomposition problems
- series where the dominant period is unknown and cannot be inferred reliably

Method references:
- [Bandara, Hyndman, and Bergmeir (2021), MSTL: A Seasonal-Trend Decomposition Algorithm for Time Series with Multiple Seasonal Patterns](https://arxiv.org/abs/2107.13462) - Primary MSTL reference used by the statsmodels implementation.

Related package links:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream MSTL implementation.

### `ROBUST_STL`

- Family: `SeasonalTrend`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `wrapper`
- Dependency tier: `core-upstream`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `12`
- Optional dependencies: statsmodels
- Summary: Robust STL-style decomposition wrapped for reproducible workflows.

Assumptions:
- expects one decomposed series at a time
- works best when one seasonal period or block structure is reasonably stable
- ROBUST_STL should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- outlier-prone seasonal-trend baselines
- classical robust decomposition

Typical failure modes:
- period omitted or mis-specified
- multiple strong seasonalities beyond the model assumptions

Not recommended for:
- shared-model multivariate decomposition problems
- series where the dominant period is unknown and cannot be inferred reliably

Method references:
- [Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html) - Robust STL in De-Time builds on the same STL literature and upstream implementation family.

Related package links:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream STL implementation family.

### `STL`

- Family: `SeasonalTrend`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `wrapper`
- Dependency tier: `core-upstream`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `12`
- Optional dependencies: statsmodels
- Summary: Classical STL wrapped into the De-Time workflow contract.

Assumptions:
- expects one decomposed series at a time
- works best when one seasonal period or block structure is reasonably stable
- STL should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- classical seasonal-trend baselines
- statsmodels-compatible workflows

Typical failure modes:
- period omitted or mis-specified
- multiple seasonalities outside STL's basic assumptions

Not recommended for:
- shared-model multivariate decomposition problems
- series where the dominant period is unknown and cannot be inferred reliably

Method references:
- [Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on LOESS](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html) - Statsmodels STL docs cite the original Journal of Official Statistics paper.

Related package links:
- [statsmodels](https://www.statsmodels.org/) - Official project site for the upstream STL implementation.

### `VMD`

- Family: `Variational`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `24`
- Optional dependencies: vmdpy, sktime
- Summary: Variational mode decomposition integrated into the common workflow layer.

Assumptions:
- expects one decomposed series at a time
- assumes the number of modes and bandwidth penalties can be tuned to the signal family
- VMD should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- band-limited mode separation
- frequency-structured univariate workflows

Typical failure modes:
- number of modes chosen poorly
- penalty parameters not aligned with the signal bandwidth

Not recommended for:
- shared-model multivariate decomposition problems

Method references:
- [Dragomiretskiy and Zosso (2014), Variational Mode Decomposition](https://doi.org/10.1109/TSP.2013.2288675) - Primary variational mode decomposition reference.

Related package links:
- [sktime](https://www.sktime.net/en/stable/) - Current maintained ecosystem for `vmdpy`, which the archived project directs users toward.
- [vmdpy](https://github.com/vrcarva/vmdpy) - Archived Python VMD package used by the current De-Time wrapper.

### `WAVELET`

- Family: `Wavelet`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `wrapper`
- Dependency tier: `core-upstream`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `8`
- Optional dependencies: PyWavelets
- Summary: Wavelet-based decomposition exposed through the common output contract.

Assumptions:
- expects one decomposed series at a time
- assumes a wavelet family and decomposition depth can be chosen sensibly
- WAVELET should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- multiscale exploratory analysis
- wavelet-style trend and detail separation

Typical failure modes:
- wavelet family mismatch
- boundary artifacts on short series

Not recommended for:
- shared-model multivariate decomposition problems

Method references:
- [Mallat (1989), A theory for multiresolution signal decomposition: the wavelet representation](https://ieeexplore.ieee.org/document/192463) - Foundational wavelet multiresolution reference.
- [Lee et al. (2019), PyWavelets: A Python package for wavelet analysis](https://doi.org/10.21105/joss.01237) - Package citation for the upstream wavelet implementation used by De-Time.

Related package links:
- [PyWavelets](https://pywavelets.readthedocs.io/en/latest/) - Official documentation for the upstream wavelet package.

## Optional backend methods

### `MEMD`

- Family: `EMD`
- Input mode: `multivariate`
- Maturity: `optional-backend`
- Implementation: `optional-backend`
- Dependency tier: `optional-backend`
- Multivariate support: `shared-model`
- Native-backed: `False`
- Minimum length hint: `24`
- Optional dependencies: PySDKit
- Summary: Optional multivariate EMD backend for shared oscillatory structure.

Assumptions:
- expects a 2D array with at least two aligned channels
- assumes oscillatory modes are meaningful enough to separate adaptively
- MEMD should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- multivariate adaptive decomposition
- shared oscillatory modes across channels

Typical failure modes:
- optional backend unavailable
- high runtime or unstable mode alignment across channels

Not recommended for:
- single-series workflows where a univariate flagship method is sufficient
- environments where optional backend dependencies cannot be installed

Method references:
- [Rehman and Mandic (2010), Multivariate empirical mode decomposition](https://doi.org/10.1098/rspa.2009.0502) - Primary MEMD reference for the multivariate EMD extension.

Related package links:
- [PySDKit](https://pysdkit.readthedocs.io/en/latest/) - Optional multivariate backend used by De-Time for MEMD.

### `MVMD`

- Family: `Variational`
- Input mode: `multivariate`
- Maturity: `optional-backend`
- Implementation: `optional-backend`
- Dependency tier: `optional-backend`
- Multivariate support: `shared-model`
- Native-backed: `False`
- Minimum length hint: `24`
- Optional dependencies: PySDKit
- Summary: Optional multivariate VMD backend for shared frequency structure.

Assumptions:
- expects a 2D array with at least two aligned channels
- assumes the number of modes and bandwidth penalties can be tuned to the signal family
- MVMD should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- multivariate variational decomposition
- shared frequency structure across channels

Typical failure modes:
- optional backend unavailable
- mode count or penalties not tuned to the signal family

Not recommended for:
- single-series workflows where a univariate flagship method is sufficient
- environments where optional backend dependencies cannot be installed

Method references:
- [Rehman and Aftab (2019), Multivariate Variational Mode Decomposition](https://arxiv.org/abs/1907.04509) - Primary MVMD reference for the multivariate VMD extension.

Related package links:
- [PySDKit](https://pysdkit.readthedocs.io/en/latest/) - Optional multivariate backend used by De-Time for MVMD.

## Experimental methods

### `GABOR_CLUSTER`

- Family: `Experimental`
- Input mode: `univariate`
- Maturity: `experimental`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `16`
- Optional dependencies: faiss
- Summary: Experimental clustering-based decomposition path.

Assumptions:
- expects one decomposed series at a time
- assumes exploratory use is acceptable and output should be validated against a stable baseline
- GABOR_CLUSTER should be evaluated against residual diagnostics rather than used as a black box

Recommended for:
- research prototypes
- exploratory clustering-style decomposition

Typical failure modes:
- unstable clustering assignments
- parameter sensitivity on short series

Not recommended for:
- shared-model multivariate decomposition problems
- first-pass baselines or high-trust production workflows

Method references:
- [Gabor (1946), Theory of Communication](https://www.rctn.org/w/images/b/b6/Gabor.pdf) - Historical reference for the Gabor time-frequency representation family.
- [Douze et al. (2024), The Faiss library](https://arxiv.org/abs/2401.08281) - Reference for the similarity-search backend used by the experimental clustering path.

Related package links:
- [Faiss](https://github.com/facebookresearch/faiss) - Vector similarity search library required by the experimental clustering backend.
