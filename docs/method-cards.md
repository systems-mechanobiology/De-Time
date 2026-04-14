# Method Cards

This page is generated from `MethodRegistry.list_catalog()` so the human-facing
method cards stay aligned with the machine-facing catalog contract.

Current package version target: `0.1.1`.

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
- Optional dependencies: none
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

### `EMD`

- Family: `EMD`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `16`
- Optional dependencies: none
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

### `VMD`

- Family: `Variational`
- Input mode: `univariate`
- Maturity: `stable`
- Implementation: `python`
- Dependency tier: `core`
- Multivariate support: `univariate`
- Native-backed: `False`
- Minimum length hint: `24`
- Optional dependencies: none
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
- Optional dependencies: none
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
