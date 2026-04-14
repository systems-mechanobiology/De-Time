# Install

## Public install path

Public releases install as the `de-time` distribution:

```bash
pip install de-time
```

Optional multivariate backends for `MVMD` and `MEMD` install with:

```bash
pip install "de-time[multivar]"
```

Naming summary:

- Product name: `De-Time`
- Distribution name: `de-time`
- Canonical import: `detime`
- Compatibility alias: `tsdecomp`

Do not install the unrelated `detime` package from PyPI when you want this
project.

## Editable install

Use an editable install for local development, release preparation, or when
you need the unreleased `0.1.1` review target directly from the repository.

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev,docs]
```

For optional multivariate wrappers during development:

```bash
python -m pip install -e .[dev,docs,multivar]
```

## Platform prerequisites

Most users will install from wheels and do not need a local compiler. If a
wheel is unavailable and pip falls back to building from source, you need:

- Python `3.10+`
- a working C/C++ toolchain
- CMake compatible with the `scikit-build-core` build

Typical source-build prerequisites by platform:

- Windows
  - Visual Studio Build Tools with MSVC and CMake on `PATH`
- macOS
  - Xcode Command Line Tools and a working C++17 compiler
- Linux
  - GCC or Clang, Python headers, and CMake

## Native extension behavior

De-Time ships native kernels for selected flagship methods:

- `SSA`
- `STD`
- `STDR`

Backend behavior:

- `backend="auto"`
  - use native when available, otherwise fall back to Python
- `backend="python"`
  - force the Python implementation
- `backend="native"`
  - require the native kernel and raise if it is unavailable

For `SSA`:

- `speed_mode="exact"` uses the deterministic exact decomposition contract
- `speed_mode="fast"` uses the approximate iterative path

You can inspect the available native exports with:

```python
from detime import native_capabilities

print(native_capabilities())
```

## Optional multivariate backends

`MVMD` and `MEMD` are optional-backend methods, not core bundled
implementations. They require the `multivar` extra and currently depend on the
installed [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/) backend. The
full method literature and upstream package links live in
[Method References](method-references.md).

If you want reviewer-grade evidence that those wrappers work in your
environment, run:

```bash
python examples/optional_multivariate_backends.py
```

## Compatibility alias

The preferred import is `detime`. The compatibility scope retained through
`0.1.x` is limited to:

- top-level `import tsdecomp`
- the `tsdecomp` executable
- `python -m tsdecomp`

Transition-era submodules such as `tsdecomp.backends`,
`tsdecomp.leaderboard`, and `tsdecomp.methods.*` are intentionally excluded
from install artifacts.

## Troubleshooting

### Wrong package installed

Symptom:

- `import detime` imports an unrelated package

Fix:

- uninstall the unrelated `detime` package
- install `de-time`

```bash
python -m pip uninstall -y detime
python -m pip install --upgrade de-time
```

### Native build failed during install

Symptom:

- pip attempts a source build and fails in the CMake or compiler stage

Fix:

- ensure your platform toolchain is installed
- upgrade pip
- retry the install

```bash
python -m pip install --upgrade pip
python -m pip install --no-cache-dir de-time
```

### Native backend unavailable at runtime

Symptom:

- `backend="native"` raises that the native implementation is unavailable

Fix:

- reinstall from a wheel when available, or
- rebuild locally with a working compiler toolchain, or
- use `backend="auto"` or `backend="python"` until the native path is present

### Optional multivariate backend import error

Symptom:

- `MVMD` or `MEMD` raises an `ImportError`

Fix:

- install the multivariate extra

```bash
python -m pip install "de-time[multivar]"
```

### Editable install looks stale

Symptom:

- schema assets, docs, or native behavior do not match the current checkout

Fix:

- reinstall the editable package after source changes that affect package data
  or the native extension

```bash
python -m pip install -e .[dev,docs]
```
