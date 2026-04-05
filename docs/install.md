# Install

## Current public install path

The current reviewer-facing install path is a GitHub source install. This keeps
the public docs honest until the first PyPI release of `de-time` exists.

```bash
pip install "de-time @ git+https://github.com/systems-mechanobiology/De-Time.git"
```

For a pinned review snapshot, add a branch, tag, or commit after the URL, for
example `@main` or `@<commit>`.

## Optional extras

Use the multivariate extra when you want optional backends such as `MVMD` and
`MEMD`.

```bash
pip install "de-time[multivar] @ git+https://github.com/systems-mechanobiology/De-Time.git"
```

## Naming notes

- Product name: `De-Time`
- Distribution name: `de-time`
- Canonical import: `detime`

Do not install the unrelated `detime` package from PyPI when you want this
project.

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

## Future release path

Once a PyPI release of `de-time` exists, the install command can be shortened
to `pip install de-time`. Until then, the GitHub install path above is the
public command that should be tested in clean environments.
