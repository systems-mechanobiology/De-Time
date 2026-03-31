# API Reference

## Public imports

The public package surface is intentionally small:

```python
from detime import (
    DecompResult,
    DecompositionConfig,
    MethodRegistry,
    decompose,
    native_capabilities,
    native_extension_available,
)
```

## `DecompositionConfig`

Main fields:

- `method`: decomposition method name
- `params`: method-specific parameter dictionary
- `backend`: `auto`, `native`, `python`, or `gpu`
- `speed_mode`: `exact` or `fast`
- `n_jobs`: concurrency hint
- `profile`: whether to record runtime metadata
- `device`: execution device hint
- `channel_names`: optional names for multivariate columns

## `decompose(series, config)`

Main entrypoint for programmatic usage.

- accepts `1D` series for univariate methods,
- accepts `2D (T, C)` arrays for multivariate methods and channelwise methods,
- returns a `DecompResult`.

## `DecompResult`

Return object fields:

- `trend`
- `season`
- `residual`
- `components`
- `meta`

For multivariate methods, the main outputs may be `2D (T, C)` arrays. Some
component payloads may be `3D`, for example mode stacks such as
`components["modes"]`.

## CLI commands

The preferred `detime` executable currently exposes:

- `run`
- `batch`
- `eval`
- `validate`
- `run_leaderboard`
- `merge_results`
- `profile`

The first-class user path today is `run`, `batch`, and `profile`.

Legacy compatibility:

- `tsdecomp` remains available as a CLI alias
- `tsdecomp` remains available as a Python import alias
