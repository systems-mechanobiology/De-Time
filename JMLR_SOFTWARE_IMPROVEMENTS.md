# Software improvements relative to the earlier research artifact

This document summarizes the main software-facing improvements that were made
while extracting and hardening the De-Time package from the earlier
benchmark-oriented repository layout.

## 1. Standalone package extraction

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

This makes the software reviewable as a package rather than only as an
artifact.

## 2. Stable public API and CLI

The package exposes a small public API centered around:

- `DecompositionConfig`
- `DecompResult`
- `decompose()`
- native capability helpers

The CLI provides a stable surface for:

- `run`
- `batch`
- `profile`
- `version`
- `schema`
- `recommend`

## 3. Retained flagship native acceleration

Selected retained flagship methods have native C++ implementations with Python
fallbacks:

- `SSA`
- `STD`
- `STDR`

This improves the practicality of the library as a reusable workflow tool
rather than only a prototype.

## 4. Multivariate support

The package includes multivariate workflows and method registration rules for:

- `MSSA`
- `MVMD`
- `MEMD`
- channelwise multivariate `STD` / `STDR`

The result object, CLI I/O, and serialized summary/meta views make multivariate
outputs easier to save, profile, and hand off downstream.

## 5. Packaging and release engineering

The package now includes:

- standalone build metadata,
- wheel-building workflow support,
- tag-triggered release smoke checks,
- source-distribution inclusion rules,
- contributor-facing documents,
- an explicit open-source license,
- PyPI release metadata and release notes.

## 6. Machine-facing interfaces

The package now includes:

- packaged JSON schemas,
- machine-readable method metadata,
- low-token result serialization modes (`summary` / `meta`),
- CLI recommendation and schema commands,
- a minimal MCP server for tool-based access.

## 7. Documentation, examples, and CI

The earlier artifact form focused on experiments and paper reproduction. The
software package now includes:

- installation guidance,
- quickstart material,
- API documentation,
- workflow tutorials,
- runnable examples,
- documentation consistency checks,
- reproducible performance snapshot generation.

These additions are aimed at software reviewers and new users rather than only
the original benchmark author.

## Remaining limitations

The package remains honest about methods that depend on optional upstream
libraries or internal research scaffolding. It is not presented as a fully
independent reimplementation of every referenced decomposition method, and
community adoption is still early.
