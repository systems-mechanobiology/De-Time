# JMLR-facing software improvements

This page summarizes the software-facing changes that turned the original benchmark-oriented codebase into a more reusable package.

The full version lives in
[`JMLR_SOFTWARE_IMPROVEMENTS.md`](https://github.com/systems-mechanobiology/De-Time/blob/main/JMLR_SOFTWARE_IMPROVEMENTS.md).

## Main changes

- extracted `tsdecomp` into a standalone package directory
- added `pyproject.toml` packaging and wheel-oriented native build support
- introduced native C++ acceleration for selected methods
- unified runtime backend selection
- introduced multivariate method support under the same public API
- expanded package tests and CLI coverage
- added user documentation, tutorials, and runnable examples

## Why this matters for MLOSS

The original repository was primarily a benchmark and paper artifact. The current package is much closer to a reusable research software library with:

- a clear installation story
- a documented API
- standalone examples
- cross-platform packaging intent
- a method registry rather than ad hoc experiment scripts
