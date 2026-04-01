# Ecosystem and Research Positioning

De-Time is research software, not a claim that one package should replace every
specialized decomposition implementation.

## Why this software exists

Time-series decomposition work often gets trapped in one of two extremes:

- one highly specialized method with its own ad hoc interface,
- one benchmark or paper artifact that is difficult to reuse as software.

De-Time exists in the middle: one reusable software surface, multiple method
families, explicit result contracts, and enough documentation to support
reproducible workflows rather than one-off figures.

## Ecosystem positioning

| Tool | Strength | How De-Time complements it |
|---|---|---|
| `statsmodels` | strong classical decomposition baselines such as `STL` and `MSTL` | keeps those methods on the same public surface as subspace and adaptive methods |
| `PyWavelets` | dedicated wavelet decomposition tools | exposes wavelet workflows through the same result contract used elsewhere |
| `PyEMD` | empirical mode decomposition family | keeps `EMD` and `CEEMDAN` available without forcing a separate interface style |
| `vmdpy` | variational mode decomposition | makes VMD part of the same decomposition comparison workflow |

The point is not to erase upstream tools. The point is to make cross-method
comparison, scripting, and handoff less painful.

## What De-Time emphasizes

- reproducible decomposition outputs,
- consistent metadata across methods,
- public examples and visual reports,
- clear separation between flagship methods and wrapper methods,
- multivariate workflows where joint structure genuinely matters.

## What De-Time does not claim

De-Time does not claim to be:

- the fastest implementation of every method,
- a full replacement for specialized upstream libraries,
- a forecasting framework,
- a complete substitute for domain-specific preprocessing.

## Relation to benchmark work

The package may share ancestry with benchmark workflows, but the public
software surface is framed as a reusable library. Users should evaluate it as
software with clear APIs, docs, examples, and release hygiene rather than only
as a benchmark artifact.
