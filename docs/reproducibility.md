# Reproducibility

This repository is now focused on the `detime` software package itself.

## Current public install story

The current reviewer-facing install path is a GitHub source install. Until the
first PyPI release of `de-time` exists, the public docs intentionally avoid
claiming a `pip install de-time` path that is not yet available.

## Included here

- canonical `detime` source code,
- deprecated `tsdecomp` top-level import and CLI alias,
- tests for the retained public surface,
- examples and tutorials for package workflows,
- documentation for installation, APIs, methods, and migration.

## Moved out

Benchmark orchestration, synthetic benchmark generators, leaderboard helpers,
and benchmark-derived methods now belong to the companion repository
`de-time-bench`.

That split keeps the main package installable and reviewable as software rather
than as a mixed library-plus-benchmark artifact.

The reviewed install artifacts also exclude transition-era compatibility
submodules such as `tsdecomp.methods.*`, `tsdecomp.leaderboard`, and
`tsdecomp.bench_config`.

## Current validation snapshot

The current reviewed snapshot has been checked with:

- `pytest` on the retained public surface,
- a coverage gate of `fail_under = 90` on the canonical core-plus-flagship
  coverage scope,
- `mkdocs build --strict`,
- wheel and sdist smoke installs in clean environments,
- `twine check dist/*`.

In the latest local review run, the gated `detime` coverage report reached
`91.40%`. The current `0.1.0` version string identifies this reviewed snapshot;
formal Git tag, GitHub release, and PyPI publication are intentionally still
pending.
