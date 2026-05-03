# Method Comparison Matrix

This page is generated from `MethodRegistry.list_catalog()` and summarizes
method-level behavior for onboarding, review, and machine-facing routing.

Current package version target: `0.1.1`.

| Method | Input mode | Backend | Maturity | Required/common params | Optional deps | Native | Multivariate | Output components | Recommended use |
|---|---|---|---|---|---|---|---|---|---|
| `CEEMDAN` | `univariate` | `python` | `stable` | `trials` (50), `noise_width` (0.05), `primary_period` (null) | PyEMD | no | `univariate` | `trend`, `season`, `residual`, `components.imfs` | noise-assisted EMD workflows; adaptive decomposition with improved IMF stability |
| `EMD` | `univariate` | `python` | `stable` | `n_imfs` (null), `primary_period` (null) | PyEMD | no | `univariate` | `trend`, `season`, `residual`, `components.imfs` | adaptive decomposition of nonlinear signals; IMF-oriented exploratory analysis |
| `GABOR_CLUSTER` | `univariate` | `python` | `experimental` | `model` (null), `model_path` (null) | faiss | no | `univariate` | `trend`, `season`, `residual`, `components.clusters` | research prototypes; exploratory clustering-style decomposition |
| `MA_BASELINE` | `univariate` | `python` | `stable` | `trend_window` (7), `season_period` (null) | none | no | `univariate` | `trend`, `season`, `residual` | sanity checks; lightweight baseline decomposition |
| `MEMD` | `multivariate` | `optional-backend` | `optional-backend` | `primary_period` (null) | PySDKit | no | `shared-model` | `trend`, `season`, `residual`, `components.imfs` | multivariate adaptive decomposition; shared oscillatory modes across channels |
| `MSSA` | `multivariate` | `python` | `flagship` | `window` (required), `rank` (null), `primary_period` (null) | none | no | `shared-model` | `trend`, `season`, `residual`, `components.elementary` | multivariate component recovery; shared seasonal structure across channels |
| `MSTL` | `univariate` | `wrapper` | `stable` | `periods` (required) | statsmodels | no | `univariate` | `trend`, `season`, `residual`, `components.seasonal_terms` | multiple seasonalities in univariate data; classical decomposition baselines |
| `MVMD` | `multivariate` | `optional-backend` | `optional-backend` | `K` (4), `alpha` (2000.0), `primary_period` (null) | PySDKit | no | `shared-model` | `trend`, `season`, `residual`, `components.modes` | multivariate variational decomposition; shared frequency structure across channels |
| `ROBUST_STL` | `univariate` | `wrapper` | `stable` | `period` (required) | statsmodels | no | `univariate` | `trend`, `season`, `residual` | outlier-prone seasonal-trend baselines; classical robust decomposition |
| `SSA` | `univariate` | `native-backed` | `flagship` | `window` (required), `rank` (null), `primary_period` (null) | none | yes | `univariate` | `trend`, `season`, `residual`, `components.elementary` | accuracy-first univariate decomposition; component recovery |
| `STD` | `channelwise` | `native-backed` | `flagship` | `period` (required) | none | yes | `channelwise` | `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape` | fast seasonal-trend baselines; channelwise multivariate workflows |
| `STDR` | `channelwise` | `native-backed` | `flagship` | `period` (required) | none | yes | `channelwise` | `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape` | robust seasonal-trend decomposition; channelwise multivariate workflows |
| `STL` | `univariate` | `wrapper` | `stable` | `period` (required) | statsmodels | no | `univariate` | `trend`, `season`, `residual` | classical seasonal-trend baselines; statsmodels-compatible workflows |
| `VMD` | `univariate` | `python` | `stable` | `K` (4), `alpha` (2000.0), `primary_period` (null) | vmdpy, sktime | no | `univariate` | `trend`, `season`, `residual`, `components.modes` | band-limited mode separation; frequency-structured univariate workflows |
| `WAVELET` | `univariate` | `wrapper` | `stable` | `wavelet` ("db4"), `level` (null) | PyWavelets | no | `univariate` | `trend`, `season`, `residual`, `components.coefficients` | multiscale exploratory analysis; wavelet-style trend and detail separation |

Use [Config Reference](config-reference.md) for full `DecompositionConfig`
field semantics and per-method parameter descriptions.

Use [Method References](method-references.md) for primary literature and
official upstream package links.
