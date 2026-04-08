# API

## Canonical import

```python
from detime import DecompositionConfig, DecompResult, MethodRegistry, decompose
```

The preferred import is `detime`. The `tsdecomp` import path remains available
only as a deprecated alias.

## Public objects

### `DecompositionConfig`

Important fields:

- `method`
- `params`
- `backend`
- `speed_mode`
- `n_jobs`
- `profile`
- `device`
- `channel_names`

### `DecompResult`

Every result exposes:

- `trend`
- `season`
- `residual`
- `components`
- `meta`

### `MethodRegistry`

Useful entrypoints:

- `MethodRegistry.list_methods()`
- `MethodRegistry.list_catalog()`
- `MethodRegistry.get_metadata(method_name)`
- `MethodRegistry.get(method_name)`
- `MethodRegistry.register(method_name)`

## Top-level helpers

- `decompose(series, config)`
- `native_extension_available()`
- `native_capabilities()`

## Machine-facing helpers

- packaged JSON schemas under `src/detime/schema_assets/`
- `detime schema --name config|result|meta|method-registry`
- `detime recommend --length ... --channels ...`
- `python -m detime.mcp.server`

Run outputs support three serialization modes:

- `full`
- `summary`
- `meta`

## Removed surface

The main package no longer exposes:

- `bench_config`
- `leaderboard`
- benchmark-derived methods in the main package

Those now belong to the companion benchmark repository
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).

## CLI

Supported commands:

- `detime run`
- `detime batch`
- `detime profile`
- `detime version`
- `detime schema`
- `detime recommend`
