# Roadmap

This roadmap describes the intended direction for De-Time as a standalone
open-source decomposition library. It is a planning document, not a promise
that every item will land on a fixed date.

## Current position

De-Time is in a standalone-package transition phase:

- unified Python API and CLI are in place,
- selected methods already support native acceleration,
- multivariate workflows have first-class package support,
- documentation, tests, and release packaging are now treated as product
  features rather than benchmark-side artifacts.

The project should be read as a research library with an improving production
surface, not as a frozen enterprise platform.

## Near-term priorities

### 1. Stable standalone identity

- finish the De-Time naming transition across package metadata, docs, and
  public entrypoints,
- preserve compatibility for legacy `tsdecomp` users during the migration,
- keep install and import paths explicit so users do not need to guess.

### 2. Method maturity clarity

- keep a clear distinction between core methods, optional-backend methods, and
  benchmark-derived compatibility wrappers,
- improve per-method parameter docs and backend notes,
- make default method selection easier for new users and agents.

### 3. Better agent and automation handoff

- maintain compact machine-readable manifests and input contracts,
- make CLI artifacts predictable for downstream tools,
- improve “start here” and shortest-path documentation for scripted use.

### 4. Release quality

- keep wheel builds healthy across major desktop platforms,
- tighten smoke tests around native backends and multivariate paths,
- reduce environment friction for mixed scientific Python stacks.

## Medium-term priorities

### 1. Stronger native acceleration

- expand native coverage where profiling shows clear benefit,
- keep Python fallback behavior correct and documented,
- avoid native rewrites that do not materially improve the user path.

### 2. Evaluation and benchmarking separation

- keep the standalone library cleanly separated from paper-specific benchmark
  artifacts,
- preserve reproducibility hooks without forcing users into the benchmark
  repository layout,
- support profiling and comparison workflows without turning the package back
  into a monolithic paper artifact.

### 3. Documentation and examples

- grow task-oriented tutorials for univariate, multivariate, and CLI-driven
  workflows,
- add more example datasets and “choose this method first” guidance,
- improve docs for optional backends and failure modes.

## Longer-term directions

- more complete multivariate evaluation support,
- richer report export and visualization paths,
- additional native or GPU-backed acceleration where the maintenance cost is
  justified,
- cleaner packaging for ecosystem integrations and hosted docs.

## Non-goals for now

The project is **not** currently trying to become:

- an end-to-end forecasting framework,
- a general dashboarding platform,
- a web application first and a library second,
- a complete reimplementation of every upstream decomposition package.

## Contribution signal

The most valuable contributions in the next phase are:

- improving method documentation and examples,
- strengthening tests and reproducibility,
- reducing installation friction,
- clarifying method maturity and backend behavior,
- targeted performance work with evidence from profiling.
