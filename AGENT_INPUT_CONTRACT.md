# Agent input contract

This page explains the minimum useful contract for agent-driven decomposition
tasks in De-Time.

## Accepted input families

- inline numeric arrays
- `numpy`-like `1D` or `2D` arrays
- caller-managed CSV or parquet file paths
- pandas DataFrame-like tables
- one named column via `col`
- multiple named columns via `cols`

## Minimal routing rules

- If the input is `1D`, prefer a univariate method such as `STD`, `STDR`,
  `SSA`, `STL`, or `EMD`.
- If the input is `2D (T, C)`, use either:
  - a multivariate method such as `MSSA`, `MVMD`, or `MEMD`
  - a channelwise-capable method such as `STD` or `STDR`
- If the caller knows the main seasonal period, pass it explicitly in
  `params.period` or the method-specific equivalent.
- If the caller wants a safe default, use `backend="auto"` and
  `speed_mode="exact"`.
- If the task is exploratory or shortlist-oriented, consider
  `speed_mode="fast"` before a final exact rerun.

## Minimal examples

### Decompose one in-memory series

```json
{
  "series_ref": [0.0, 0.1, 0.4, 0.8, 0.5, 0.2],
  "input_kind": "array",
  "method": "SSA",
  "params": {
    "window": 4,
    "rank": 2
  },
  "backend": "auto",
  "speed_mode": "exact"
}
```

### Decompose one file by a single named column

```json
{
  "series_ref": "examples/data/example_series.csv",
  "input_kind": "file",
  "method": "STD",
  "col": "value",
  "params": {
    "period": 12
  }
}
```

### Decompose a multivariate file

```json
{
  "series_ref": "examples/data/example_multivariate.csv",
  "input_kind": "file",
  "method": "MSSA",
  "cols": ["north_load", "south_load"],
  "params": {
    "window": 24,
    "rank": 8,
    "primary_period": 12
  },
  "backend": "auto",
  "speed_mode": "fast"
}
```

### Batch a folder

```json
{
  "task": "decompose many files with the same method",
  "glob": "data/*.csv",
  "method": "STD",
  "params": {
    "period": 24
  },
  "backend": "auto",
  "speed_mode": "exact"
}
```

### Profile one method

```json
{
  "task": "profile one method on representative lengths",
  "method": "SSA",
  "lengths": [128, 512, 2048],
  "backend": "native",
  "speed_mode": "exact"
}
```

## Field meanings

- `series_ref`
  - inline array, file path, or caller-managed table object
- `method`
  - decomposition method name such as `STD`, `SSA`, or `MSSA`
- `params`
  - method-specific parameters
- `col`
  - one named input column for univariate file-based runs
- `cols`
  - multiple named input columns for multivariate file-based runs
- `backend`
  - `auto`, `native`, `python`, or `gpu`
- `speed_mode`
  - `exact` or `fast`
- `channel_names`
  - optional names for `2D` inputs when the caller already knows them

## Expected output contract

Programmatic outputs should be normalized to a `DecompResult`-like shape:

- `trend`
- `season`
- `residual`
- `components`
- `meta`

CLI-friendly persisted outputs should be interpreted as:

- `*_components.csv`
  - primary 1D or 2D outputs flattened into columns
- `*_meta.json`
  - runtime metadata, input layout, backend used, component shapes, channel
    names
- `*_components_3d.npz`
  - optional storage for mode or IMF stacks

## Handoff hints for downstream agents

- Prefer `meta.result_layout`, `meta.n_channels`, and `meta.channel_names`
  instead of inferring shape from file naming.
- Check `meta.backend_used` before claiming native acceleration was actually
  used.
- Treat `components` as optional and method-specific.
- Do not assume every method returns interpretable mode stacks.
