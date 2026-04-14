# Comparison Evidence

This page complements [Comparisons](comparisons.md) with the generated evidence
files that back the reviewer-grade matrices.

Primary method citations and official upstream package links are collected in
[Method References](method-references.md).

## Generated evidence files

- `docs/assets/generated/evidence/comparison_evidence.json`
- `docs/assets/generated/evidence/comparison_capability_matrix.csv`
- `docs/assets/generated/evidence/comparison_install_matrix.csv`
- `docs/assets/generated/evidence/comparison_family_fairness.csv`
- `docs/assets/generated/evidence/comparison_agent_matrix.csv`
- `docs/assets/generated/evidence/workflow_comparison.json`

Regenerate them with:

```bash
python benchmarks/software_comparison/generate_comparison_evidence.py
python examples/workflow_comparisons/compare_specialist_glue_vs_detime.py
```

## Capability emphasis

The matrices are designed to support one narrow claim:

> De-Time is not the deepest specialist package in every family; it is the
> most workflow- and machine-contract-oriented decomposition layer among the
> compared packages.

This is why the generated comparison tables prioritize:

- unified config and result objects
- machine-readable catalog fields
- compact serialization modes
- CLI and profiling support
- MCP / tool surface
- explicit maturity labeling

## Workflow-level comparison

The workflow comparison artifact contrasts two paths:

- a multi-package specialist glue workflow that mixes multiple result objects
  and package-specific APIs
- a De-Time workflow that keeps the result contract, routing surface, and
  serialization story under one import path

This is the software abstraction argument behind the package, not a benchmark
leaderboard claim.
