# JMLR MLOSS submission checklist for De-Time

This file is a maintainer-facing checklist for preparing a software-paper
submission to the JMLR MLOSS track from the current De-Time package state.

## Software package items

- [x] standalone package root
- [x] explicit `pyproject.toml`
- [x] open-source license file
- [x] contributor documentation
- [x] code of conduct
- [x] user documentation tree
- [x] runnable examples
- [x] package-level tests
- [x] automated CI for tests
- [x] source distribution that includes docs/examples/license and excludes junk files
- [x] wheel build path with native extension support
- [x] canonical `detime` import path
- [x] deprecated top-level `tsdecomp` alias with narrow compatibility scope

## Evidence to prepare outside the codebase

- [x] public repository URL for the software record
- [x] public release/tag and PyPI distribution record
- [ ] short cover-letter statement of early user/community activity
- [x] short comparison section against nearby software packages
- [x] software paper text and author metadata

## Notes on current scope

The package is strongest as a reusable research software library for
time-series decomposition workflows rather than as a polished end-user
application.

The clearest flagship methods are:

- `SSA`
- `STD`
- `STDR`
- `MSSA`

Other retained methods remain valid package features, but some are wrappers or
optional backend integrations rather than co-equal flagship implementations.

## Suggested submission framing

The paper should emphasize:

1. a unified decomposition interface across multiple method families,
2. native acceleration for selected retained flagship methods,
3. multivariate support under the same API,
4. machine-facing schemas and low-token result views for reproducible tooling,
5. packaging, release, tests, and documentation improvements that distinguish
   the software from its earlier benchmark-artifact form.
