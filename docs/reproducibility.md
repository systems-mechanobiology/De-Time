# Reproducibility

This repository is now focused on the `detime` software package itself.

## Included here

- canonical `detime` source code,
- deprecated `tsdecomp` compatibility alias,
- tests for the retained public surface,
- examples and tutorials for package workflows,
- documentation for installation, APIs, methods, and migration.

## Moved out

Benchmark orchestration, synthetic benchmark generators, leaderboard helpers,
and benchmark-derived methods now belong to the companion repository
`de-time-bench`.

That split keeps the main package installable and reviewable as software rather
than as a mixed library-plus-benchmark artifact.
