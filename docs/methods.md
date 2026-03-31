# Methods

This page groups methods by maturity and implementation style so users can choose appropriate starting points.

## Stable core methods

These methods represent the clearest current library story:

| Method | Input | Notes |
|---|---|---|
| `STD` | `1D` or `2D` channelwise | Native C++ kernel available |
| `STDR` | `1D` or `2D` channelwise | Native C++ kernel available |
| `SSA` | `1D` | Native C++ kernel available |
| `MSSA` | `2D (T, C)` | Self-contained multivariate implementation |

## Classical and external-wrapper methods

These methods are exposed through the same interface but rely more heavily on upstream scientific Python implementations:

| Method | Backend story | Notes |
|---|---|---|
| `STL`, `MSTL`, `ROBUST_STL` | `statsmodels` | Good baseline classical decomposition |
| `WAVELET` | `PyWavelets` | Multi-scale decomposition |
| `EMD`, `CEEMDAN` | `PyEMD` | Empirical decomposition family |
| `VMD` | `vmdpy` | Variational mode decomposition |
| `MVMD`, `MEMD` | optional `multivar` extra | Multivariate wrappers with optional backend |

## Benchmark-oriented methods

These methods remain useful but are more benchmark-derived or backend-dependent:

| Method | Notes |
|---|---|
| `DR_TS_REG` | Native path available, Python fallback still depends on benchmark support code |
| `DR_TS_AE` | Benchmark-support wrapper |
| `SL_LIB` | Benchmark-support wrapper |
| `GABOR_CLUSTER` | FAISS-based clustering workflow with partial native helper support |

Placeholder-only research paths are intentionally not part of the supported public method surface.

## Recommendation

If you are evaluating the package as a library rather than as a benchmark artifact, start with:

1. `STD`
2. `STDR`
3. `SSA`
4. `MSSA`

Those methods best represent the current package direction.
