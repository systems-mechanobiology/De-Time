# Agent manifest

De-Time is a time-series decomposition package for humans and agents.

The preferred Python and CLI entrypoints are exposed through `detime`. Legacy
`tsdecomp` imports and CLI aliases still work for compatibility through
`0.1.x`, with earliest removal planned for `0.2.0`.

## Good for

- split a time series into trend, seasonal, and residual components
- compare decomposition methods under one shared result model
- decompose one CSV or parquet file from an agent pipeline without writing
  custom wrappers
- profile runtime across methods, lengths, and backends
- route univariate and multivariate decomposition under one top-level API
- hand off compact component artifacts, summaries, or metadata to downstream
  model, report, benchmark, or symbolic pipelines

## Stable wrappers

- `decompose(series, config)` for programmatic decomposition
- `DecompositionConfig(...)` for method, backend, speed, and channel settings
- `detime run` for one input file
- `detime batch` for multiple files
- `detime profile` for runtime-oriented evaluation
- `detime schema` for packaged JSON schemas
- `detime recommend` for method shortlisting

## Machine-facing interfaces

- `MethodRegistry.list_catalog()` for method metadata
- `summary` and `meta` result modes for low-token handoff
- packaged JSON schemas under `src/detime/schema_assets/`
- `python -m detime.mcp.server` for local-first tool-based access

## MCP guidance

Stable tool names in the current machine-contract series:

- `list_methods`
- `get_schema`
- `recommend_method`
- `run_decomposition`
- `summarize_result`

Recommended subsets:

- routing only
  - `list_methods`, `get_schema`, `recommend_method`
- bounded-context execution
  - add `run_decomposition` and `summarize_result`

## Best first methods

- `STD` or `STDR`
  - use when a clear seasonal period is known
- `SSA`
  - use for univariate series when you want a strong general baseline
- `MSSA`
  - use for multivariate arrays with shared cross-channel structure
- `EMD`, `CEEMDAN`, `VMD`
  - use when adaptive or non-stationary oscillatory structure matters more than
    classical seasonal decomposition

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
- optional `<name>_components_3d.npz`
- `<name>_summary.json` or `<name>_meta.json` when low-token modes are used
