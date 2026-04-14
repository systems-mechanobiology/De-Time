# De-Time

De-Time is workflow-oriented research software for reproducible time-series
decomposition. It gives you one public package, one decomposition contract, and
one docs surface across univariate, multivariate, native-backed, and
machine-facing workflows.

## What it is

- A canonical Python package with import path `detime`.
- A stable `decompose()` entrypoint plus `DecompositionConfig` and
  `DecompResult`.
- A documentation set centered on practical workflows rather than benchmark
  scoreboards.
- A package whose flagship methods are `SSA`, `STD`, `STDR`, and `MSSA`.
- A machine-facing surface with schemas, recommendations, and a minimal MCP
  server.

## What it is not

- Not a new decomposition algorithm.
- Not a benchmark-paper artifact disguised as a library.
- Not a replacement for every specialized upstream implementation.
- Not a promise that every wrapper has the same maturity as the flagship path.

## Start here

- [Install](install.md) for package installation and extras.
- [Quickstart](quickstart.md) for the first successful Python and CLI runs.
- [Choose a Method](choose-a-method.md) for picking a starting workflow.
- [ML Workflows](ml-workflows.md) for the package's machine-learning-facing use
  cases.
- [Methods](methods.md) for method family details.
- [Method Cards](method-cards.md) for per-method assumptions and failure modes.
- [Machine API](machine-api.md) for schemas, catalog, recommendation, and MCP use.
- [Comparison Evidence](comparison-evidence.md) for reviewer-grade matrices.
- [Token Benchmarks](token-benchmarks.md) for bounded-context payload costs.
- [Migration from `tsdecomp`](migration.md) if you are upgrading existing code.

## Package boundary

This repository ships the software package itself. Companion benchmark
artifacts live in the separate
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench)
repository. The main package no longer exposes benchmark orchestration,
leaderboard helpers, or benchmark-derived methods.

The legacy `tsdecomp` import and CLI still resolve to De-Time, but only as a
deprecated compatibility alias through `0.1.x`.

## Visual reference

![Single-series decomposition](assets/generated/home/ssa_components.png)

![Multivariate decomposition](assets/generated/home/mssa_multivariate.png)
