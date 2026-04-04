# Install

## PyPI

```bash
pip install de-time
```

## Optional extras

Use the multivariate extra when you want optional backends such as `MVMD` and
`MEMD`.

```bash
pip install "de-time[multivar]"
```

## Editable install

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Native extension behavior

De-Time ships native kernels for selected flagship methods. If the native
extension is unavailable, the package keeps working and falls back to the
Python implementations when a fallback exists.

## Compatibility alias

The preferred import is `detime`. The `tsdecomp` import and CLI remain
available only as a deprecated compatibility layer.
