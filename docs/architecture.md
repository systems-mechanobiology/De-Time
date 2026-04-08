# Architecture

## Package layout

The canonical implementation lives under `src/detime`.

- `core.py`: public data models.
- `registry.py`: method registration, metadata catalog, and `decompose()` dispatch.
- `io.py`: loading series and saving decomposition outputs.
- `serialization.py`: `full`, `summary`, and `meta` result views.
- `recommend.py`: method recommendation logic.
- `schemas.py`: packaged JSON schema generation and loading.
- `profile.py`: runtime profiling helpers.
- `viz.py`: plotting helpers.
- `methods/`: flagship methods and retained wrappers.
- `mcp/server.py`: minimal MCP server for tool-based access.
- `_native.py`: native extension discovery and capability checks.

## Compatibility layer

`src/tsdecomp` is now a thin compatibility package. It re-exports the package-
level De-Time surface and emits deprecation warnings for imports and CLI usage.
Only the top-level import path and CLI alias remain packaged; transition-era
submodules are intentionally not shipped in install artifacts.

## Machine-facing boundary

Machine-oriented workflows use:

- packaged JSON schemas under `src/detime/schema_assets`,
- machine-readable method metadata from `MethodRegistry.list_catalog()`,
- `detime schema` and `detime recommend`,
- the minimal MCP server at `python -m detime.mcp.server`,
- low-token result exports via `summary` and `meta` modes.

## Native boundary

Native kernels are built and loaded under the De-Time naming path first. The
main package exposes native support only for the retained flagship methods.
Benchmark-derived native code is no longer part of the main package boundary.
