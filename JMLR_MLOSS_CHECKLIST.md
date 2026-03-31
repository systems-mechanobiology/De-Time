# JMLR MLOSS submission checklist for `tsdecomp`

This file is a maintainer-facing checklist for preparing a software-paper
submission to the JMLR MLOSS track.

## Software package items

- [x] standalone package directory
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

## Evidence to prepare outside the codebase

- [ ] public repository URL you want to cite in the paper
- [ ] issue tracker URL you want reviewers to use
- [ ] brief statement of user community or adoption evidence for the cover letter
- [ ] short comparison paragraph against nearby software packages
- [ ] final software paper text and author metadata

## Notes on current scope

The package is strongest as a reusable research software library for
time-series decomposition rather than as a polished end-user application.

The clearest “core library” methods are:

- `STD`
- `STDR`
- `SSA`
- `MSSA`
- `DR_TS_REG`

Other methods are still valid package features, but some remain wrappers over
external libraries or benchmark-oriented support code.

## Suggested submission framing

The paper should emphasize:

1. a unified decomposition interface across multiple method families,
2. native acceleration for selected core methods,
3. multivariate support under the same API,
4. packaging, tests, and documentation improvements that distinguish the
   software from its earlier benchmark-artifact form.
