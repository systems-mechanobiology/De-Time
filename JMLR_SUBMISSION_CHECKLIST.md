# JMLR MLOSS submission checklist for De-Time

This file is a practical checklist for preparing a JMLR MLOSS submission from the current package state.

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

## Still manual before submission

- [ ] Confirm the final public repository URL that will be cited in the paper
- [ ] Confirm the final package distribution URL if publishing to PyPI before submission
- [ ] Collect evidence of active users or community activity for the cover letter
- [ ] Write the short MLOSS paper itself
- [ ] Prepare the source archive exactly as it will be submitted
- [ ] Double-check that every advertised method is mature enough to defend in peer review

## Recommended cover-letter evidence

JMLR MLOSS asks for evidence that the project has an active user community. Good evidence includes:

- public issue activity
- external users or labs using the package
- stars, forks, or watchers
- package download counts if published
- citations, talks, or teaching use
- contributors beyond the initial author

## Recommended positioning

The strongest framing for De-Time is:

- a unified time-series decomposition library
- with both univariate and multivariate methods
- optional native acceleration for high-cost paths
- reproducible CLI and benchmarking support

The weakest framing would be to present it as a fully mature replacement for every existing decomposition package. Reviewers will notice that some methods are wrappers or benchmark-oriented utilities.
