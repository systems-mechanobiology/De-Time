# Architecture

## Package layout

The canonical implementation lives under `src/detime`.

- `core.py`: public data models.
- `registry.py`: method registration and `decompose()` dispatch.
- `io.py`: loading series and saving decomposition outputs.
- `profile.py`: runtime profiling helpers.
- `viz.py`: plotting helpers.
- `methods/`: flagship methods and retained wrappers.
- `_native.py`: native extension discovery and capability checks.

## Compatibility layer

`src/tsdecomp` is now a thin compatibility package. It re-exports the package-
level De-Time surface and emits deprecation warnings for imports and CLI usage.
Only the top-level import path and CLI alias remain packaged; transition-era
submodules are intentionally not shipped in install artifacts.

## Native boundary

Native kernels are now built and loaded under the De-Time naming path first.
The main package exposes native support only for the retained flagship methods.
Benchmark-derived native code is no longer part of the main package boundary.
