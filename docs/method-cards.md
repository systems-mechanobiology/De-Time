# Method Cards

This page is generated from `MethodRegistry.list_catalog()` so the human-facing
method cards stay aligned with the machine-facing catalog contract.

Current package version target: `0.1.1`.

Source citations and official upstream package links are collected in
[Method References](method-references.md).

This page intentionally keeps cards compact. Use
[Method Matrix](method-matrix.md) for table comparison and
[Config Reference](config-reference.md) for full parameter semantics.

The `tsdecomp` top-level alias remains compatibility-only through `0.1.x` and is
not the canonical surface for any method listed below.

## Flagship methods

### `MSSA`

- Summary: Multivariate SSA for shared-structure decomposition across channels.
- Use when: multivariate component recovery; shared seasonal structure across channels
- Avoid when: single-series workflows where a univariate flagship method is sufficient; very short series that cannot support a sensible window length
- Key params: `window` (required), `rank` (null), `primary_period` (null)
- Input/backend: `multivariate` input, `python` implementation, maturity `flagship`
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.elementary`
- References: [Method References](method-references.md#mssa)

See [Config Reference](config-reference.md#mssa) for the full parameter table.

### `SSA`

- Summary: Singular spectrum analysis for structured univariate decomposition.
- Use when: accuracy-first univariate decomposition; component recovery
- Avoid when: shared-model multivariate decomposition problems; very short series that cannot support a sensible window length
- Key params: `window` (required), `rank` (null), `primary_period` (null)
- Input/backend: `univariate` input, `native-backed` implementation, maturity `flagship`
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.elementary`
- References: [Method References](method-references.md#ssa)

See [Config Reference](config-reference.md#ssa) for the full parameter table.

### `STD`

- Summary: Fast seasonal-trend decomposition with dispersion-aware diagnostics.
- Use when: fast seasonal-trend baselines; channelwise multivariate workflows
- Avoid when: problems that require one shared latent model across channels; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (required)
- Input/backend: `channelwise` input, `native-backed` implementation, maturity `flagship`
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape`
- References: [Method References](method-references.md#std)

See [Config Reference](config-reference.md#std) for the full parameter table.

### `STDR`

- Summary: Robust seasonal-trend decomposition for noisier periodic signals.
- Use when: robust seasonal-trend decomposition; channelwise multivariate workflows
- Avoid when: problems that require one shared latent model across channels; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (required)
- Input/backend: `channelwise` input, `native-backed` implementation, maturity `flagship`
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape`
- References: [Method References](method-references.md#stdr)

See [Config Reference](config-reference.md#stdr) for the full parameter table.

## Stable wrappers and retained methods

### `CEEMDAN`

- Summary: Noise-assisted EMD variant for more stable IMF extraction.
- Use when: noise-assisted EMD workflows; adaptive decomposition with improved IMF stability
- Avoid when: shared-model multivariate decomposition problems
- Key params: `trials` (50), `noise_width` (0.05), `primary_period` (null)
- Input/backend: `univariate` input, `python` implementation, maturity `stable`
- Optional dependencies: PyEMD
- Output components: `trend`, `season`, `residual`, `components.imfs`
- References: [Method References](method-references.md#ceemdan)

See [Config Reference](config-reference.md#ceemdan) for the full parameter table.

### `EMD`

- Summary: Empirical mode decomposition under the De-Time result contract.
- Use when: adaptive decomposition of nonlinear signals; IMF-oriented exploratory analysis
- Avoid when: shared-model multivariate decomposition problems
- Key params: `n_imfs` (null), `primary_period` (null)
- Input/backend: `univariate` input, `python` implementation, maturity `stable`
- Optional dependencies: PyEMD
- Output components: `trend`, `season`, `residual`, `components.imfs`
- References: [Method References](method-references.md#emd)

See [Config Reference](config-reference.md#emd) for the full parameter table.

### `MA_BASELINE`

- Summary: Simple moving-average baseline for smoke tests and lightweight workflows.
- Use when: sanity checks; lightweight baseline decomposition
- Avoid when: shared-model multivariate decomposition problems
- Key params: `trend_window` (7), `season_period` (null)
- Input/backend: `univariate` input, `python` implementation, maturity `stable`
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`
- References: [Method References](method-references.md#ma_baseline)

See [Config Reference](config-reference.md#ma_baseline) for the full parameter table.

### `MSTL`

- Summary: Statsmodels MSTL wrapped into the De-Time workflow surface.
- Use when: multiple seasonalities in univariate data; classical decomposition baselines
- Avoid when: shared-model multivariate decomposition problems; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `periods` (required)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Optional dependencies: statsmodels
- Output components: `trend`, `season`, `residual`, `components.seasonal_terms`
- References: [Method References](method-references.md#mstl)

See [Config Reference](config-reference.md#mstl) for the full parameter table.

### `ROBUST_STL`

- Summary: Robust STL-style decomposition wrapped for reproducible workflows.
- Use when: outlier-prone seasonal-trend baselines; classical robust decomposition
- Avoid when: shared-model multivariate decomposition problems; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (required)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Optional dependencies: statsmodels
- Output components: `trend`, `season`, `residual`
- References: [Method References](method-references.md#robust_stl)

See [Config Reference](config-reference.md#robust_stl) for the full parameter table.

### `STL`

- Summary: Classical STL wrapped into the De-Time workflow contract.
- Use when: classical seasonal-trend baselines; statsmodels-compatible workflows
- Avoid when: shared-model multivariate decomposition problems; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (required)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Optional dependencies: statsmodels
- Output components: `trend`, `season`, `residual`
- References: [Method References](method-references.md#stl)

See [Config Reference](config-reference.md#stl) for the full parameter table.

### `VMD`

- Summary: Variational mode decomposition integrated into the common workflow layer.
- Use when: band-limited mode separation; frequency-structured univariate workflows
- Avoid when: shared-model multivariate decomposition problems
- Key params: `K` (4), `alpha` (2000.0), `primary_period` (null)
- Input/backend: `univariate` input, `python` implementation, maturity `stable`
- Optional dependencies: vmdpy, sktime
- Output components: `trend`, `season`, `residual`, `components.modes`
- References: [Method References](method-references.md#vmd)

See [Config Reference](config-reference.md#vmd) for the full parameter table.

### `WAVELET`

- Summary: Wavelet-based decomposition exposed through the common output contract.
- Use when: multiscale exploratory analysis; wavelet-style trend and detail separation
- Avoid when: shared-model multivariate decomposition problems
- Key params: `wavelet` ("db4"), `level` (null)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Optional dependencies: PyWavelets
- Output components: `trend`, `season`, `residual`, `components.coefficients`
- References: [Method References](method-references.md#wavelet)

See [Config Reference](config-reference.md#wavelet) for the full parameter table.

## Optional backend methods

### `MEMD`

- Summary: Optional multivariate EMD backend for shared oscillatory structure.
- Use when: multivariate adaptive decomposition; shared oscillatory modes across channels
- Avoid when: single-series workflows where a univariate flagship method is sufficient; environments where optional backend dependencies cannot be installed
- Key params: `primary_period` (null)
- Input/backend: `multivariate` input, `optional-backend` implementation, maturity `optional-backend`
- Optional dependencies: PySDKit
- Output components: `trend`, `season`, `residual`, `components.imfs`
- References: [Method References](method-references.md#memd)

See [Config Reference](config-reference.md#memd) for the full parameter table.

### `MVMD`

- Summary: Optional multivariate VMD backend for shared frequency structure.
- Use when: multivariate variational decomposition; shared frequency structure across channels
- Avoid when: single-series workflows where a univariate flagship method is sufficient; environments where optional backend dependencies cannot be installed
- Key params: `K` (4), `alpha` (2000.0), `primary_period` (null)
- Input/backend: `multivariate` input, `optional-backend` implementation, maturity `optional-backend`
- Optional dependencies: PySDKit
- Output components: `trend`, `season`, `residual`, `components.modes`
- References: [Method References](method-references.md#mvmd)

See [Config Reference](config-reference.md#mvmd) for the full parameter table.

## Experimental methods

### `GABOR_CLUSTER`

- Summary: Experimental clustering-based decomposition path.
- Use when: research prototypes; exploratory clustering-style decomposition
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `model` (null), `model_path` (null)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Optional dependencies: faiss
- Output components: `trend`, `season`, `residual`, `components.clusters`
- References: [Method References](method-references.md#gabor_cluster)

See [Config Reference](config-reference.md#gabor_cluster) for the full parameter table.
