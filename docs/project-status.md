# Project Files, Citation, and Release Posture

De-Time is packaged as standalone research software rather than as a benchmark-only artifact.

## Core repository files

- `CITATION.cff`: preferred software citation metadata
- `CHANGELOG.md`: release-oriented history
- `SECURITY.md`: vulnerability reporting guidance
- `ROADMAP.md`: current direction and non-goals
- `PUBLISHING.md`: wheel, docs, and release notes workflow
- `CONTRIBUTING.md`: developer setup and contribution expectations
- `CODE_OF_CONDUCT.md`: community standards

## Current public posture

| Area | State |
|---|---|
| Brand | `De-Time` |
| Distribution | `de-time` |
| Preferred import | `detime` |
| Compatibility import | `tsdecomp` |
| Installation model | wheel-first where available |
| Docs | GitHub Pages |

## What this means for users and reviewers

If you are evaluating the software for adoption, review, or citation, the
repository includes:

- Python packaging metadata,
- CI workflows for tests, wheels, and docs,
- runnable examples and visual walkthroughs,
- citation and release files,
- contributor and security guidance.

## What remains outside the public docs

Submission-facing manuscripts and review material may still live in the
repository, but they are not part of the public docs site and should not be
treated as the main user path.
