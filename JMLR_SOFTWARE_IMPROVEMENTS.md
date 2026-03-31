# Software improvements relative to the earlier research artifact

This document summarizes the main software-facing improvements that were made
while extracting the De-Time package from the earlier benchmark-oriented
repository layout.

## 1. Package extraction and standalone identity

Previously, decomposition code lived inside a broader benchmark and paper
artifact repository. The main package now lives in a standalone repository root
with its own:

- `pyproject.toml`
- `README.md`
- `LICENSE`
- `tests/`
- `native/`
- `docs/`
- `examples/`

This makes the software reviewable as a package rather than only as an artifact.

## 2. Stable public API and CLI

The package now exposes a small public API centered around:

- `DecompositionConfig`
- `DecompResult`
- `decompose()`
- native capability helpers

The CLI also provides a stable surface for:

- `run`
- `batch`
- `profile`

## 3. Native acceleration

Selected high-cost methods were given native C++ implementations with Python
fallbacks:

- `SSA`
- `STD`
- `STDR`
- `DR_TS_REG`

This improves the practicality of the library as a reusable research tool rather
than only a prototype.

## 4. Multivariate support

The extracted package now includes multivariate workflows and method registration
rules for:

- `MSSA`
- `MVMD`
- `MEMD`
- channelwise multivariate `STD` / `STDR`

The result object and CLI I/O were updated so multivariate outputs can be saved
and profiled consistently.

## 5. Packaging and release engineering

The package now includes:

- standalone build metadata,
- wheel-building workflow support,
- cross-platform release intent,
- source-distribution inclusion rules,
- contributor-facing documents,
- an explicit open-source license.

## 6. Documentation and examples

The earlier artifact form focused on experiments and paper reproduction. The
software package now includes:

- installation guidance,
- quickstart material,
- API documentation,
- workflow tutorials,
- runnable examples.

These additions are aimed at software reviewers and new users rather than only
the original benchmark author.

## 7. Testing and submission readiness

The package has package-level tests, CI preparation, and cleaner packaging rules
to make the software easier to review independently of the original paper
artifact.

## Remaining limitations

The package is still honest about the methods that depend on optional upstream
libraries or internal benchmark support code. It is not presented as a fully
independent reimplementation of every referenced decomposition method.
