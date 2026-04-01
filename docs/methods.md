# Methods Atlas

This page groups methods by family, maturity, and backend story so users can
choose a credible starting point before they scale up to batches or papers.

## Stable starting points

These methods represent the clearest current De-Time story.

| Method | Input | Backend story | Notes |
|---|---|---|---|
| `STD` | `1D` or `2D` channelwise | native C++ + Python fallback | good seasonal-trend default when period is known |
| `STDR` | `1D` or `2D` channelwise | native C++ + Python fallback | same core idea with average seasonal shape |
| `SSA` | `1D` | native C++ + Python fallback | strong univariate baseline |
| `MSSA` | `2D (T, C)` | self-contained Python implementation | first multivariate method to try |
| `DR_TS_REG` | `1D` | native C++ + Python fallback | useful when the benchmark-derived regression path fits your setting |

## Seasonal-trend methods

| Method | Input mode | Backend story | Maturity |
|---|---|---|---|
| `STL` | univariate | `statsmodels` | stable wrapper |
| `MSTL` | univariate | `statsmodels` | stable wrapper |
| `ROBUST_STL` | univariate | `statsmodels` | stable wrapper |
| `STD` | channelwise | native-backed | flagship |
| `STDR` | channelwise | native-backed | flagship |

## Subspace methods

| Method | Input mode | Backend story | Maturity |
|---|---|---|---|
| `SSA` | univariate | native-backed | flagship |
| `MSSA` | multivariate | built-in | flagship |

## Adaptive mode decomposition

| Method | Input mode | Backend story | Maturity |
|---|---|---|---|
| `EMD` | univariate | `PyEMD` wrapper | wrapper |
| `CEEMDAN` | univariate | `PyEMD` wrapper | wrapper |
| `VMD` | univariate | `vmdpy` wrapper | wrapper |
| `MVMD` | multivariate | optional `multivar` extra | experimental wrapper |
| `MEMD` | multivariate | optional `multivar` extra | experimental wrapper |

## Other workflows

| Method | Input mode | Backend story | Notes |
|---|---|---|---|
| `WAVELET` | univariate | `PyWavelets` wrapper | multi-scale baseline |
| `MA_BASELINE` | univariate | NumPy implementation | simple sanity baseline |
| `GABOR_CLUSTER` | univariate | FAISS + helper functions | clustering-oriented workflow |
| `DR_TS_AE` | univariate | benchmark-support wrapper | backend-dependent |
| `SL_LIB` | univariate | benchmark-support wrapper | backend-dependent |

## How to choose

| Situation | First method |
|---|---|
| known seasonal period, interpretable decomposition | `STD` or `STDR` |
| strong univariate baseline | `SSA` |
| shared multivariate structure across channels | `MSSA` |
| adaptive or non-stationary oscillatory structure | `EMD`, `CEEMDAN`, or `VMD` |
| multivariate adaptive mode decomposition | `MVMD` or `MEMD` |

## Why the atlas calls out backend story

De-Time does not flatten every method into the same maturity claim. Some
methods are deeply integrated and native-backed. Others are intentionally
unified wrappers over upstream scientific libraries. That distinction matters
for performance expectations, packaging expectations, and citation honesty.
