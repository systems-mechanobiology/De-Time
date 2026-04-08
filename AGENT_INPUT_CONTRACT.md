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
- If the task is routing rather than execution, call `detime recommend` or the
  MCP `recommend_method` tool first.
- If the caller wants a safe default, use `backend="auto"` and
  `speed_mode="exact"`.

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

### Ask for a method recommendation

```json
{
  "task": "recommend",
  "length": 192,
  "channels": 3,
  "prefer": "accuracy",
  "allow_optional_backends": false
}
```

### Request a schema

```json
{
  "task": "schema",
  "name": "method-registry"
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

Programmatic outputs are normalized to a `DecompResult`-like shape:

- `trend`
- `season`
- `residual`
- `components`
- `meta`

CLI-friendly persisted outputs can be:

- `*_components.csv`
- `*_meta.json`
- `*_components_3d.npz`
- `*_summary.json`
- `*_full.json`

## Handoff hints for downstream agents

- Prefer `meta.result_layout`, `meta.n_channels`, and `meta.channel_names`
  instead of inferring shape from file naming.
- Check `meta.backend_used` before claiming native acceleration was actually
  used.
- Use `summary` or `meta` output mode when token budget matters more than raw
  arrays.
- Treat `components` as optional and method-specific.
- Use the packaged schemas instead of inferring payload shapes from examples.
