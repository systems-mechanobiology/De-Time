# Comparison Evidence Appendix

This appendix stores the generated files behind
[Compare Alternatives](comparisons.md). It is kept out of the primary
navigation because most users only need the summarized matrix.

## Files

- [comparison_evidence.json](assets/generated/evidence/comparison_evidence.json)
- [comparison_capability_matrix.csv](assets/generated/evidence/comparison_capability_matrix.csv)
- [comparison_install_matrix.csv](assets/generated/evidence/comparison_install_matrix.csv)
- [comparison_family_fairness.csv](assets/generated/evidence/comparison_family_fairness.csv)
- [comparison_agent_matrix.csv](assets/generated/evidence/comparison_agent_matrix.csv)
- [workflow_comparison.json](assets/generated/evidence/workflow_comparison.json)

## Regenerate

```bash
python benchmarks/software_comparison/generate_comparison_evidence.py
python examples/workflow_comparisons/compare_specialist_glue_vs_detime.py
```

The comparison focuses on software workflow properties: shared config/result
objects, CLI and artifact behavior, method metadata, schemas, and automation
support. It is not a leaderboard.
