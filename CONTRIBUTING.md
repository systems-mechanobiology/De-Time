# Contributing to De-Time

Thanks for contributing to `De-Time` (`de-time` / `detime`).

## Scope

This repository contains a standalone time-series decomposition library with:

- a Python API,
- a CLI,
- optional native C++ acceleration,
- benchmark-facing utilities used to evaluate decomposition quality.

Contributions are welcome in these areas:

- decomposition methods and backends,
- packaging and cross-platform installation,
- documentation, tutorials, and examples,
- test coverage and reproducibility,
- performance profiling and numerical stability.

## Development setup

```bash
cd /path/to/de-time
python3 -m pip install -U pip
python3 -m pip install -e .[multivar]
python3 -m pytest tests -q
```

For source builds of the native extension, a local C++ toolchain and CMake are required.

## Contribution guidelines

- Prefer small, reviewable pull requests.
- Add or update tests for behavior changes.
- Keep public APIs documented in `README.md` and the docs tree.
- Preserve Python fallback behavior when adding optional native or third-party backends.
- Avoid adding heavyweight dependencies to the core install path unless they are broadly justified.
- Use `ROADMAP.md` to understand the current priority order before proposing
  large feature additions.
- Use `SECURITY.md` for vulnerability reporting; do not open public issues for
  suspected exploitable problems.

## Code quality expectations

- Public-facing changes should include at least one smoke test or regression test.
- New methods should document their parameters, expected input shape, and backend support.
- Optional dependencies must fail with clear installation guidance.

## Licensing note

This package is currently prepared under the BSD 3-Clause License so it can be distributed and reviewed as open-source research software. If the maintainer intends to release under a different OSI-approved license, confirm that before publishing to package indexes or submitting archival source bundles.

## Reporting issues

Use the GitHub issue tracker for:

- installation failures,
- numerical correctness bugs,
- API inconsistencies,
- platform-specific build problems,
- documentation gaps.

When reporting a bug, include:

- operating system,
- Python version,
- install method,
- minimal reproducible example,
- full traceback or error log.
