# Agent manifest

De-Time is a time-series decomposition package for humans and agents.

The preferred Python and CLI entrypoints are now exposed through `detime`.
Legacy `tsdecomp` imports and CLI aliases still work for compatibility.

## Good for

- split a time series into trend, seasonal, and residual components
- compare decomposition methods under one shared result model
- decompose one CSV or parquet file from an agent pipeline without writing
  custom wrappers
- profile runtime across methods, lengths, and backends
- route univariate and multivariate decomposition under one top-level API
- hand off compact component artifacts to a downstream model, report generator,
  or symbolic pipeline

## Avoid when

- the primary task is forecasting rather than decomposition
- you need a domain-specific probabilistic state-space model rather than a
  decomposition workflow
- you need the fastest possible implementation of one single upstream method
  family and do not care about unified interfaces
- your task is large-scale dashboarding or interactive analytics rather than
  decomposition artifacts

## Stable wrappers

- `decompose(series, config)` for programmatic decomposition
- `DecompositionConfig(...)` for method, backend, speed, and channel settings
- `detime run` for one input file
- `detime batch` for multiple files
- `detime profile` for runtime-oriented evaluation

## Best first methods

- `STD` or `STDR`
  - use when a clear seasonal period is known
  - good first choice for interpretable trend-season-residual output
- `SSA`
  - use for univariate series when you want a strong general baseline
  - especially useful when the period is present but not handled by a fixed
    classical seasonal smoother
- `MSSA`
  - use for multivariate arrays with shared cross-channel structure
- `EMD`, `CEEMDAN`, `VMD`
  - use when adaptive or non-stationary oscillatory structure matters more than
    classical seasonal decomposition
- `MVMD`, `MEMD`
  - use for multivariate adaptive mode decomposition when optional multivariate
    backends are available

## Returned artifacts

Programmatic calls return one `DecompResult` with:

- `trend`
- `season`
- `residual`
- `components`
- `meta`

CLI calls save:

- `<name>_components.csv`
- `<name>_meta.json`
- optional `<name>_components_3d.npz` when higher-order component stacks exist

## Shape model

- `1D` arrays are valid for univariate methods
- `2D (T, C)` arrays are valid for multivariate methods and channelwise methods
- channelwise methods such as `STD` and `STDR` can accept `2D` input but
  decompose channels independently
- if an agent sends `2D` input to a univariate-only method, the package should
  raise a clear error rather than guessing
