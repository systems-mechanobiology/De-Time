# Testing and Coverage

- Core-surface coverage: gated via `.coveragerc` and `fail_under = 90`.
- Package-wide coverage: emitted as a second CI artifact with the broader denominator.
- Runtime snapshot file: `docs/assets/generated/evidence/performance_snapshot.json`.
- Runtime snapshot methods: SSA, STD, STDR.
- Token benchmark file: `docs/assets/generated/evidence/token_benchmarks.json`.
- Agent eval summary: passed `5` / `5` deterministic checks.
