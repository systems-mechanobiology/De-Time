# Project Status and Release Files

De-Time is packaged as a standalone repository rather than a benchmark-only
artifact. That means release metadata, contribution guidance, and security
policy are part of the public software surface.

## Core repository files

- `CITATION.cff`: preferred software citation metadata for the project
- `CHANGELOG.md`: release-oriented change history
- `SECURITY.md`: vulnerability reporting expectations and scope
- `ROADMAP.md`: near-term, medium-term, and non-goal planning notes
- `PUBLISHING.md`: release checklist, wheel workflow, and PyPI notes
- `CONTRIBUTING.md`: developer setup and contribution expectations
- `CODE_OF_CONDUCT.md`: community standards for collaboration

## Current release posture

The current standalone package is positioned as:

- brand: `De-Time`
- distribution: `de-time`
- preferred import: `detime`
- legacy compatibility import: `tsdecomp`
- wheel-first installation for supported platforms

## What this means for users

If you are evaluating the project for adoption or review, the repository now
includes:

- package metadata suitable for Python distribution,
- CI workflows for tests, wheels, and docs,
- runnable examples and a docs tree,
- citation and release-history files,
- contributor and security guidance.

## What still remains manual

Some submission-facing materials, especially the JMLR software manuscript and
cover letter, may still need final author details, final repository URLs, and
submission metadata before external submission.
