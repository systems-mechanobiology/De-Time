# Comparisons

De-Time is meant to sit beside specialist libraries, not erase them.

## Scope comparison

| Package | Primary focus | De-Time relationship |
|---|---|---|
| `statsmodels` | classical statistical decomposition and modeling | De-Time wraps `STL` and `MSTL` rather than replacing `statsmodels` |
| `PyEMD` | empirical mode decompositions | De-Time exposes `EMD` and `CEEMDAN` through a unified result contract |
| `PyWavelets` | wavelet transforms | De-Time wraps wavelet decomposition for workflow consistency |
| `PySDKit` | signal decomposition toolkit with optional multivariate methods | De-Time uses it as an optional backend for `MVMD` and `MEMD` |
| `SSALib` | SSA-focused tooling | De-Time offers SSA inside a broader decomposition workflow surface |

## What De-Time adds

- one canonical import and CLI,
- one configuration model across method families,
- one saved-output contract,
- one place to document native acceleration and optional backends.

## What De-Time does not claim

- It does not claim to outperform specialist packages across every task.
- It does not use benchmark leaderboards as the main evidence for the package.
- It does not claim that every wrapped method is equally mature.
