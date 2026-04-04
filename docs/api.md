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
- `MethodRegistry.get(method_name)`
- `MethodRegistry.register(method_name)`

## Top-level helpers

- `decompose(series, config)`
- `native_extension_available()`
- `native_capabilities()`

## Removed surface

The main package no longer exposes:

- `bench_config`
- `leaderboard`
- `DR_TS_REG`
- `DR_TS_AE`
- `SL_LIB`

Those now belong to the companion benchmark repository `de-time-bench`.

## CLI

Supported commands:

- `detime run`
- `detime batch`
- `detime profile`
- `detime version`
