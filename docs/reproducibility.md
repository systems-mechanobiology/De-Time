# Reproducibility

This repository is focused on the `detime` software package itself.

## Included here

- canonical `detime` source code,
- deprecated `tsdecomp` top-level import and CLI alias,
- tests for the retained public surface,
- examples and tutorials for package workflows,
- documentation for installation, APIs, methods, and migration,
- packaged JSON schemas and a minimal MCP server for machine-facing workflows.

## Moved out

Benchmark orchestration, synthetic benchmark generators, leaderboard helpers,
and benchmark-derived methods belong to the companion repository
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).

That split keeps the main package installable and reviewable as software rather
than as a mixed library-plus-benchmark artifact.

The release artifacts also exclude transition-era compatibility submodules such
as `tsdecomp.methods.*`, `tsdecomp.leaderboard`, and `tsdecomp.bench_config`.

## Validation workflow

The current release and docs were checked with:

- `pytest tests -q`
- `pytest tests --cov=detime --cov-config=.coveragerc`
- `mkdocs build --strict`
- `python -m build`
- `python scripts/check_dist_contents.py dist/*.tar.gz dist/*.whl`
- `python scripts/check_doc_consistency.py`
- `python scripts/release_smoke_matrix.py`
- `python scripts/generate_performance_snapshot.py`
- `python -m twine check dist/*`

## Coverage boundary

The coverage gate is applied to the canonical `detime` core-plus-flagship
surface.

The denominator intentionally omits:

- the deprecated `tsdecomp` compatibility layer,
- CLI wrappers,
- I/O helpers,
- visualization helpers,
- optional wrappers and non-flagship integrations that remain tested but are
  not part of the gated coverage surface.

The latest gated local coverage run reached `93.20%`.

## Evidence artifacts

- Performance snapshot: `docs/assets/generated/evidence/performance_snapshot.json`
- Performance summary CSV: `docs/assets/generated/evidence/performance_snapshot.csv`
- JSON schemas: `src/detime/schema_assets/*.json`

The performance snapshot is reproducible from
`scripts/generate_performance_snapshot.py`. The release smoke report is
reproducible from `scripts/release_smoke_matrix.py`.
