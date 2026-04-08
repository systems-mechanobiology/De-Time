# JMLR MLOSS submission checklist for De-Time

This file is a practical checklist for preparing a JMLR MLOSS submission from
the current package state.

## Software package items

- [x] Standalone package root with build metadata
- [x] Open-source license file
- [x] User-facing README
- [x] Docs tree with install, quickstart, API guide, and tutorials
- [x] Runnable examples
- [x] Contributor-facing documentation
- [x] Automated tests
- [x] Coverage generation in CI
- [x] Cross-platform CI for the package
- [x] Clean package tree without `.DS_Store` or `__pycache__`
- [x] Software-improvements document
- [x] Release tag and PyPI distribution

## Still manual before submission

- [ ] Collect external evidence of active users or community activity for the cover letter
- [ ] Finalize the short MLOSS paper text
- [ ] Prepare the source archive exactly as it will be submitted
- [ ] Double-check that every advertised method is mature enough to defend in peer review

## Recommended cover-letter evidence

JMLR MLOSS asks for evidence that the project has an active user community.
Auditable evidence for the present revision can include:

- public issue activity,
- public GitHub Discussions activity,
- public release notes,
- issue templates and contribution path,
- external users or labs trying the package,
- stars, forks, or watchers,
- contributors beyond the initial author.

## Recommended positioning

The strongest framing for De-Time is:

- a workflow-oriented time-series decomposition library,
- with both univariate and multivariate methods,
- optional native acceleration for retained flagship paths,
- machine-facing schemas and low-token outputs,
- reproducible CLI and package-level validation.

The weakest framing would be to present it as a fully mature replacement for
every existing decomposition package or as a benchmark leaderboard product.
