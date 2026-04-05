# Methods

## Flagship methods

| Method | Input | Backend story | Why start here |
|---|---|---|---|
| `SSA` | `1D` | native C++ plus Python fallback | strong first choice for interpretable single-series decomposition |
| `STD` | `1D` and channelwise `2D` | native C++ plus Python fallback | simple seasonal-trend separation with stable defaults |
| `STDR` | `1D` and channelwise `2D` | native C++ plus Python fallback | same interface as `STD` with shared seasonal-shape estimation |
| `MSSA` | `2D` | Python implementation | joint multichannel decomposition when channels share structure |

## Retained wrappers and specialist paths

| Method | Input | Type | Notes |
|---|---|---|---|
| `STL` | univariate | `statsmodels` wrapper | good baseline when the primary period is known |
| `MSTL` | univariate | `statsmodels` wrapper | multiple seasonal periods |
| `EMD` | univariate | `PyEMD` wrapper | adaptive decomposition |
| `CEEMDAN` | univariate | `PyEMD` wrapper | ensemble adaptive decomposition |
| `VMD` | univariate | optional backend wrapper | variational mode decomposition |
| `WAVELET` | univariate | `PyWavelets` wrapper | multi-scale decomposition |
| `MA_BASELINE` | univariate | internal baseline | lightweight sanity check |
| `MVMD` | multivariate | optional `PySDKit` backend | reinstall De-Time with the `multivar` extra |
| `MEMD` | multivariate | optional `PySDKit` backend | reinstall De-Time with the `multivar` extra |
| `GABOR_CLUSTER` | univariate | experimental internal method | use after you already trust a baseline |

## Moved out of the main package

The following methods are no longer part of `detime`:

- `DR_TS_REG`
- `DR_TS_AE`
- `SL_LIB`

These benchmark-derived methods moved to the companion repository
`de-time-bench`.

## How to read this surface

- Start with `SSA`, `STD`, `STDR`, or `MSSA` unless a specialist method is
  clearly required.
- Treat upstream wrappers as integration convenience, not as evidence that
  De-Time replaces the upstream package.
- Treat optional multivariate backends as opt-in extras.
