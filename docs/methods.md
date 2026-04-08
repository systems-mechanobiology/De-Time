# Methods

## Flagship methods

| Method | Input | Maturity | Backend story | Why start here |
|---|---|---|---|---|
| `SSA` | `1D` | flagship | native C++ plus Python fallback | strong first choice for interpretable single-series decomposition |
| `STD` | `1D` and channelwise `2D` | flagship | native C++ plus Python fallback | simple seasonal-trend separation with stable defaults |
| `STDR` | `1D` and channelwise `2D` | flagship | native C++ plus Python fallback | robust seasonal-trend decomposition with shared seasonal-shape estimation |
| `MSSA` | `2D` | flagship | Python implementation | joint multichannel decomposition when channels share structure |

## Retained wrappers and specialist paths

| Method | Input | Maturity | Dependency tier | Notes |
|---|---|---|---|---|
| `STL` | univariate | stable | core-upstream | good baseline when the primary period is known |
| `MSTL` | univariate | stable | core-upstream | multiple seasonal periods |
| `EMD` | univariate | stable | core | adaptive decomposition |
| `CEEMDAN` | univariate | stable | core | ensemble adaptive decomposition |
| `VMD` | univariate | stable | core | variational mode decomposition |
| `WAVELET` | univariate | stable | core-upstream | multi-scale decomposition |
| `MA_BASELINE` | univariate | stable | core | lightweight sanity check |
| `MVMD` | multivariate | optional-backend | optional-backend | install with the `multivar` extra |
| `MEMD` | multivariate | optional-backend | optional-backend | install with the `multivar` extra |
| `GABOR_CLUSTER` | univariate | experimental | core | use after you already trust a baseline |

## Moved out of the main package

Benchmark-derived methods are not part of `detime`. Companion benchmark work
now lives in
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).

## How to read this surface

- Start with `SSA`, `STD`, `STDR`, or `MSSA` unless a specialist method is
  clearly required.
- Treat upstream wrappers as integration convenience, not as evidence that
  De-Time replaces the upstream package.
- Treat optional multivariate backends as opt-in extras.
- Use `detime recommend` when you want a machine-readable shortlist instead of
  choosing manually.
