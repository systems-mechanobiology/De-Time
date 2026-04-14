# Docs index

This file is a compact documentation map for agents and contributors.

## Fastest navigation

- `START_HERE.md`
  - shortest useful entry into the package
- `ENTRYPOINTS.md`
  - minimal list of commands and files worth opening first
- `AGENT_MANIFEST.md`
  - what the package is good for and where it should not be used
- `AGENT_INPUT_CONTRACT.md`
  - accepted input shapes, routing rules, and expected artifacts

## Human-facing docs

- `README.md`
  - GitHub-facing product overview
- `docs/index.md`
  - docs homepage
- `docs/install.md`
  - installation and platform notes
- `docs/quickstart.md`
  - first Python and CLI workflows
- `docs/api.md`
  - public package surface
- `docs/methods.md`
  - method families and maturity notes
- `docs/method-references.md`
  - citations and upstream package links for retained methods
- `docs/tutorials/univariate.md`
  - runnable workflow tutorial with published outputs

## Examples

- `examples/univariate_quickstart.py`
- `examples/multivariate_mssa.py`
- `examples/method_survey.py`
- `examples/profile_and_cli.py`

## Submission and software notes

- `JMLR_SOFTWARE_IMPROVEMENTS.md`
- `JMLR_MLOSS_CHECKLIST.md`
- `JMLR_SUBMISSION_CHECKLIST.md`

## Best next files for agents

- open `AGENT_INPUT_CONTRACT.md` before trying to synthesize a wrapper
- open `docs/api.md` before calling programmatic entrypoints
- open `src/detime/registry.py` if you need exact method and input-mode rules
- open `src/detime/io.py` if you need the persisted artifact contract
