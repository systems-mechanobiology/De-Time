# API

## Canonical import

```python
from detime import DecompositionConfig, DecompResult, MethodRegistry, decompose
```

The canonical package import is `detime`. The top-level `tsdecomp` import and
CLI remain compatibility aliases only through `0.1.x`.

## `DecompositionConfig`

`DecompositionConfig` is the validated runtime contract for Python calls and
mirrors the CLI surface.

- `method: str`
  Required method name such as `SSA`, `STD`, `STDR`, `MSSA`, `MVMD`, or
  `MEMD`.
- `params: dict[str, Any] = {}`
  Method-specific parameters. Examples include `period` for `STD`, `window`
  and `rank` for `SSA`, and `primary_period` for automatic grouping.
- `return_components: list[str] | None = None`
  Reserved compatibility field. Current decomposition entrypoints return the
  full `DecompResult`; methods may ignore this field.
- `backend: "auto" | "native" | "python" | "gpu" = "auto"`
  Backend preference. `auto` uses a native kernel when one exists, `python`
  forces the Python implementation, `native` requires the native path, and
  `gpu` raises unless a method explicitly supports it.
- `speed_mode: "exact" | "fast" = "exact"`
  Runtime accuracy policy. For native `SSA`, `exact` follows the deterministic
  SVD-backed path and `fast` uses the approximate iterative kernel.
- `profile: bool = False`
  When `True`, attach runtime metadata such as `runtime_ms` to result metadata
  or profile reports.
- `device: str | None = "cpu"`
  Reserved execution device selector. Current retained methods are CPU
  workflows unless a wrapper says otherwise.
- `n_jobs: int = 1`
  Requested parallelism hint for methods or wrappers that support it.
- `seed: int | None = 42`
  Random seed used by fast or approximate backends where relevant.
- `channel_names: list[str] | None = None`
  Optional channel labels for multivariate inputs. These are copied into result
  metadata and saved artifacts.

Validation errors come from Pydantic. Invalid backend names, negative
`n_jobs`, or malformed parameter payloads fail before decomposition starts.

## `DecompResult`

`DecompResult` is the normalized output object returned by `decompose(...)`.

- `trend: np.ndarray`
  Trend component. Shape matches the input layout.
- `season: np.ndarray`
  Seasonal or oscillatory component. Shape matches the input layout.
- `residual: np.ndarray`
  Remaining unexplained component. Shape matches the input layout.
- `components: dict[str, np.ndarray]`
  Method-specific extra outputs such as `modes`, `imfs`, `dispersion`, or
  `seasonal_shape`.
- `meta: dict[str, Any]`
  Runtime and provenance metadata. Common keys include `method`,
  `backend_requested`, `backend_used`, `speed_mode`, `result_layout`,
  `n_channels`, `channel_names`, and `runtime_ms` when profiling is enabled.

The core reconstruction contract is:

```python
result.trend + result.season + result.residual
```

which should match the original input up to the documented method tolerance.

## `decompose(series, config)`

`decompose(series, config)` is the public execution entrypoint.

- Accepted input shapes:
  - 1D arrays for univariate methods.
  - 2D arrays of shape `(time, channels)` for multivariate or channelwise
    methods.
- Return value:
  - One `DecompResult`.
- Common errors:
  - `ValueError` for unsupported shapes or missing required parameters.
  - `RuntimeError` when `backend="native"` is forced but no native kernel is
    available.
  - `ImportError` for optional-backend methods such as `MVMD` and `MEMD`
    without `de-time[multivar]`.

Backend resolution is method-specific:

- `SSA`, `STD`, and `STDR` can use native kernels.
- `MSSA` is Python-only.
- `MVMD` and `MEMD` are optional-backend wrappers and require the `multivar`
  extra.

## `MethodRegistry`

`MethodRegistry` is the machine-readable source of truth for the installed
method catalog.

- `MethodRegistry.list_methods()`
  Return registered public method names.
- `MethodRegistry.list_catalog()`
  Return the full catalog used by docs generation, recommendation, and MCP.
- `MethodRegistry.get_metadata(method_name)`
  Return one catalog entry as a dictionary.
- `MethodRegistry.get(method_name)`
  Return the callable decomposition implementation.
- `MethodRegistry.register(method_name)`
  Decorator used by method modules to register implementations.

Every catalog payload now includes:

- `package`
- `version`
- `contract_version`
- `methods`

Every method entry exposes at least:

- `family`
- `input_mode`
- `maturity`
- `implementation`
- `dependency_tier`
- `multivariate_support`
- `native_backed`
- `min_length`
- `summary`
- `recommended_for`
- `typical_failure_modes`
- `assumptions`
- `not_recommended_for`
- `optional_dependencies`
- `references`
- `package_links`

## Serialization and machine-facing APIs

De-Time publishes three result views for bounded-context workflows:

- `full`
  Full arrays plus metadata and diagnostics.
- `summary`
  Array shapes and summary statistics plus metadata and diagnostics.
- `meta`
  Metadata and diagnostics only.

Machine-facing entrypoints:

- `detime schema --name config|result|meta|method-registry`
- `detime recommend --length ... --channels ...`
- `python -m detime.mcp.server`

The `method-registry` schema and payload are versioned within the current
machine-contract series `0.1`. Consumers should prefer `contract_version` over
guessing schema compatibility from the package version alone.

## CLI summary

Supported top-level commands:

- `detime run`
- `detime batch`
- `detime profile`
- `detime version`
- `detime schema`
- `detime recommend`

CLI profile reports support both `json` and `text` output, and `detime profile
--format text` now affects stdout as well as `--output` files.
