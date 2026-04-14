# Install

## Tagged release path

Public De-Time releases install as the `de-time` distribution.

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

## Editable branch install

Use this when you are working from an unreleased branch, validating the release
target before the `de-time-v0.1.1` tag is published from `main`, or developing
the package locally.

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
in install artifacts. The top-level alias is supported through `0.1.x` and may
be removed as early as `0.2.0`.

## Release record

The repository already has a `0.1.0` GitHub release record. This branch is
prepared for `0.1.1`, which will publish from `main` through the release
workflow, verify `pip install de-time`, and then update the public docs site.
Release notes live in the GitHub release/tag record and in `CHANGELOG.md`.
