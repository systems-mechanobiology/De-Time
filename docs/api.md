# API

## Canonical import

```python
from detime import DecompositionConfig, DecompResult, MethodRegistry, decompose
```

The preferred import is `detime`. The `tsdecomp` import path remains available
only as a deprecated alias through `0.1.x`, with earliest removal planned for
`0.2.0`.

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

Every catalog entry is expected to expose at least:

- `family`
- `maturity`
- `implementation`
- `dependency_tier`
- `multivariate_support`
- `native_backed`
- `min_length`
- `summary`
- `recommended_for`
- `typical_failure_modes`

## Top-level helpers

- `decompose(series, config)`
- `native_extension_available()`
- `native_capabilities()`

## Machine-facing helpers

- packaged JSON schemas under `src/detime/schema_assets/`
- `detime schema --name config|result|meta|method-registry`
- `detime recommend --length ... --channels ...`
- `python -m detime.mcp.server`

The machine contract is local-first in the current `0.1.x` line. Tool names,
schema payloads, and the method catalog are intended to stay stable within the
`0.1` machine-contract series.

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
