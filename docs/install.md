# Install

## Current install path

Install the latest released package from PyPI:

```bash
python -m pip install de-time
```

Optional multivariate backends for `MVMD` and `MEMD` install with:

```bash
python -m pip install "de-time[multivar]"
```

Optional EMD-family wrappers for `EMD` and `CEEMDAN` install with:

```bash
python -m pip install "de-time[emd]"
```

Optional torch-backed neural block support for `NBEATS_INTERPRETABLE` installs with:

```bash
python -m pip install "de-time[neural]"
```

Notebook tooling for the method gallery installs with:

```bash
python -m pip install "de-time[notebook]"
```

Names used by this project:

| Context | Name |
|---|---|
| Project/product | `DeTime` |
| Python distribution | `de-time` |
| Python import | `detime` |
| Deprecated compatibility alias | `tsdecomp` |

Do not install the unrelated [`detime`](https://pypi.org/project/detime/)
package from PyPI when you want this project; that package is not DeTime.

To install the unreleased `main` branch directly from GitHub:

```bash
python -m pip install "git+https://github.com/systems-mechanobiology/DeTime.git"
```

## Editable install

Use an editable install for local development, release preparation, or when
you need the unreleased `main` branch directly from the repository.

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev,docs]
```

For optional multivariate wrappers during development:

```bash
python -m pip install -e .[dev,docs,multivar]
```

For the EMD and torch-backed neural extras during development:

```bash
python -m pip install -e .[dev,docs,emd,neural]
```

## Platform Prerequisites

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

DeTime ships native kernels for selected flagship methods:

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

## Optional EMD and neural backends

`EMD` and `CEEMDAN` require the `emd` extra because they import PyEMD from the
`EMD-signal` distribution at runtime. `WAVELET`, `WAVEFORM_BLOCK`, and
`WAVELETMIXER_BLOCK` use PyWavelets, which is part of the default DeTime
dependency set.

Most neural block methods are lightweight NumPy implementations. The exception
is `NBEATS_INTERPRETABLE`, which requires torch and is installed through the
`neural` extra.

## Compatibility alias

The preferred import is `detime`. The compatibility scope retained through
`0.1.x` is limited to:

- top-level `import tsdecomp`
- the `tsdecomp` executable
- `python -m tsdecomp`

Transition-era submodules such as `tsdecomp.backends`,
`tsdecomp.leaderboard`, and `tsdecomp.methods.*` are intentionally excluded
from install artifacts.

## Troubleshooting FAQ

<div class="compact-faq">

<details>
<summary>Wrong package installed</summary>

Symptom: `import detime` imports an unrelated package.

Fix: uninstall the unrelated `detime` package, then install `de-time`.

```bash
python -m pip uninstall -y detime
python -m pip install de-time
```

</details>

<details>
<summary>Native build failed during install</summary>

Symptom: pip attempts a source build and fails in the CMake or compiler stage.

Fix: ensure your platform toolchain is installed, upgrade pip, and retry the
install.

```bash
python -m pip install --upgrade pip
python -m pip install --no-cache-dir de-time
```

</details>

<details>
<summary>Native backend unavailable at runtime</summary>

Symptom: `backend="native"` raises that the native implementation is
unavailable.

Fix: reinstall from a wheel when available, rebuild locally with a working
compiler toolchain, or use `backend="auto"` / `backend="python"` until the
native path is present.

</details>

<details>
<summary>Optional backend import error</summary>

Symptom: `MVMD`, `MEMD`, `EMD`, `CEEMDAN`, or `NBEATS_INTERPRETABLE` raises an
`ImportError`.

Fix: install the matching extra.

```bash
python -m pip install "de-time[multivar]"
python -m pip install "de-time[emd]"
python -m pip install "de-time[neural]"
```

</details>

<details>
<summary>Editable install looks stale</summary>

Symptom: schema assets, docs, or native behavior do not match the current
checkout.

Fix: reinstall the editable package after source changes that affect package
data or the native extension.

```bash
python -m pip install -e .[dev,docs]
```

</details>

</div>
