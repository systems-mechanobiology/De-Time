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
- `pytest tests/optional/test_multivar_optional_backends.py -q`
- `pytest tests --cov=detime --cov-config=.coveragerc`
- `pytest tests --cov=detime --cov-config=.coveragerc.package`
- `python scripts/generate_schema_assets.py --check`
- `python scripts/generate_schema_assets.py`
- `python scripts/generate_tutorial_assets.py`
- `mkdocs build --strict`
- `python -m build`
- `python scripts/check_dist_contents.py dist/*.tar.gz dist/*.whl`
- `python scripts/check_doc_consistency.py`
- `python scripts/release_smoke_matrix.py`
- `python scripts/generate_performance_snapshot.py`
- `python scripts/generate_method_cards.py`
- `python benchmarks/software_comparison/generate_comparison_evidence.py`
- `python examples/workflow_comparisons/compare_specialist_glue_vs_detime.py`
- `python benchmarks/token_benchmarks/generate_token_benchmarks.py`
- `python evals/agent/run_agent_evals.py`
- `python scripts/generate_reviewer_bundle.py`
- `python -m twine check dist/*`

## Coverage boundary

The repository now publishes two coverage views so the denominator is explicit:

- **core-surface coverage**
  - the gated `detime` core-plus-flagship contract
- **package-wide coverage**
  - the broader installable `detime` package, including CLI, I/O,
    visualization, wrappers, and machine-facing helpers

The core gate is applied to the canonical `detime` core-plus-flagship surface.

The core-surface denominator intentionally omits:

- the deprecated `tsdecomp` compatibility layer,
- CLI wrappers,
- I/O helpers,
- visualization helpers,
- optional wrappers and non-flagship integrations that remain tested but are
  not part of the gated coverage surface.

The latest local `0.1.1` release-candidate run reached `93.73%`
core-surface coverage and `84.00%` package-wide coverage.

Package-wide coverage is emitted separately in CI and uploaded as a second
artifact so reviewer-facing reports can show both the narrow safety gate and
the broader installable surface.

Optional `.[multivar]` integrations are validated separately in a dedicated
smoke path so `MVMD` / `MEMD` execution evidence is published without
broadening the flagship-method coverage gate.

## Native agreement checks

Native-backed methods are not treated as correctness shortcuts. The test suite
includes numeric agreement checks between native and Python implementations for:

- `SSA`
- `STD`
- `STDR`

The documented tolerances are:

- `SSA`: `atol=1e-6`
- `STD` / `STDR`: `atol=1e-9`

## Evidence artifacts

- Performance snapshot: `docs/assets/generated/evidence/performance_snapshot.json`
- Performance summary CSV: `docs/assets/generated/evidence/performance_snapshot.csv`
- Comparison evidence: `docs/assets/generated/evidence/comparison_evidence.json`
- Workflow comparison demo: `docs/assets/generated/evidence/workflow_comparison.json`
- Token benchmark summary: `docs/assets/generated/evidence/token_benchmarks.json`
- Agent eval summary: `docs/assets/generated/evidence/agent_eval_summary.json`
- JSON schemas: `src/detime/schema_assets/*.json`

The performance snapshot is reproducible from
`scripts/generate_performance_snapshot.py`. Tutorial outputs are reproducible
from `scripts/generate_tutorial_assets.py`. Schema assets are reproducible from
`scripts/generate_schema_assets.py`. The release smoke report is reproducible
from `scripts/release_smoke_matrix.py`.
