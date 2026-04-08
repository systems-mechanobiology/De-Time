# Comparisons

De-Time is meant to sit beside specialist libraries, not erase them. The
package is strongest when the user needs one workflow surface across several
decomposition families, one saved-output contract, and one place to switch
between Python, CLI, and selected native-backed runs.

## Where specialist packages are deeper

| Package | Where it is deeper | How De-Time positions itself |
|---|---|---|
| `statsmodels` | mature classical decomposition and statistical modeling | De-Time wraps `STL` and `MSTL` rather than replacing `statsmodels` |
| `PyEMD` | deeper EMD-family tooling | De-Time exposes `EMD` and `CEEMDAN` through the same workflow contract used for other families |
| `PyWavelets` | deeper wavelet transforms and transform-specific APIs | De-Time uses wavelet decomposition as one workflow option, not as a claim of wavelet leadership |
| `PySDKit` | broader signal-decomposition toolkit, including optional multivariate backends | De-Time uses `PySDKit` selectively for `MVMD` and `MEMD` while keeping a time-series-centered config/result layer |
| `SSALib` | deeper SSA-only environment and SSA-specific tooling | De-Time offers `SSA` inside a broader cross-family package, not as a deeper SSA-only library |
| `sktime` | current maintained VMD reality plus a larger time-series transformation ecosystem | De-Time treats VMD as one integrated workflow option and compares against the maintained `sktime` path rather than the old standalone `vmdpy` story |

## Software-level comparison axes

| Axis | De-Time claim |
|---|---|
| Workflow orientation | one public package centered on decomposition workflows rather than on a single method family |
| Common contract | `DecompositionConfig`, `DecompResult`, and `decompose()` across retained methods |
| Batch and profiling path | `detime run`, `detime batch`, and `detime profile` are part of the public surface |
| Multivariate story | `MSSA` is a built-in flagship path; `MVMD` and `MEMD` are clearly marked optional backends |
| Native story | selected flagship methods (`SSA`, `STD`, `STDR`) have native-backed acceleration when available |
| Wrapper transparency | methods are documented as flagship, wrapper, optional backend, or experimental rather than being presented as equally mature |

## Why `sktime` appears in the VMD row

For VMD-related comparisons, De-Time now points to the maintained `sktime`
ecosystem rather than treating the old standalone `vmdpy` package as the
current baseline. That keeps the related-software story aligned with the
current maintenance reality instead of comparing only against a stale package
identity.

## Minimal software evidence from the current reviewed snapshot

The table below is not a universal benchmark claim. It is a small software
validation snapshot from one Windows / Python 3.11 wheel install of the
reviewed package, included to show that the native-backed path is materially
different from the Python fallback on retained flagship methods.

| Method | Python mean runtime (ms) | Native mean runtime (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 968.988 | 574.751 | 1.69x |
| `STD` | 1.449 | 0.060 | 24.30x |
| `STDR` | 1.767 | 0.064 | 27.81x |

## Packaging and quality evidence

- The current public install path is a GitHub source install, not a broken
  placeholder PyPI command.
- The canonical coverage gate applies to the `detime` core and flagship path,
  with `fail_under = 90`.
- The current reviewed snapshot reached `91.40%` on that gated surface in a
  local coverage run.
- Wheel and sdist smoke installs, `mkdocs build --strict`, and `twine check`
  are part of the review-time validation story.

## What De-Time does not claim

- It does not claim to outperform specialist packages across every task.
- It does not use benchmark leaderboards as the main evidence for the package.
- It does not claim that every wrapped method is equally mature.
