# Install

## Public release path

De-Time `0.1.0` is published as the `de-time` distribution.

```bash
pip install de-time
```

For optional multivariate backends such as `MVMD` and `MEMD`:

```bash
pip install "de-time[multivar]"
```

## Naming notes

- Product name: `De-Time`
- Distribution name: `de-time`
- Canonical import: `detime`
- Legacy compatibility import: `tsdecomp`

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

The preferred import is `detime`. The legacy compatibility contract is limited
to:

- top-level `import tsdecomp`
- the `tsdecomp` executable
- `python -m tsdecomp`

Transition-era submodules such as `tsdecomp.backends`,
`tsdecomp.leaderboard`, and `tsdecomp.methods.*` are intentionally not shipped
in install artifacts.

## Release record

The first public release is `0.1.0`, tagged as `de-time-v0.1.0` on April 8,
2026. Release notes live in the GitHub release/tag record and in
`CHANGELOG.md`.
