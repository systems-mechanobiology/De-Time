# Installation

## Recommended install

```bash
pip install de-time
```

This is the preferred path for normal users because the package is designed to
ship prebuilt wheels where possible.

The preferred import path is `detime`. The legacy import path `tsdecomp` still
works for compatibility.

## Optional multivariate backends

Some multivariate methods use optional third-party backends. Install them with:

```bash
pip install "de-time[multivar]"
```

## Development install

```bash
cd /path/to/de-time
python3 -m pip install -U pip
python3 -m pip install -e .[multivar]
python3 -m pytest tests -q
```

## Source builds

When a wheel is not available, `pip` may build the package from source. In that
case you need:

- a C++ compiler,
- CMake,
- Python development headers,
- a standard scientific Python stack.

## Platform notes

- Linux, macOS, and Windows are first-class targets in the packaging workflow.
- Native acceleration is optional at runtime because Python fallbacks remain
  available for the native-backed methods.
- Some methods require optional upstream libraries and will fail with explicit
  installation guidance if those libraries are unavailable.
