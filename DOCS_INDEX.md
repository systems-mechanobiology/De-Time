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
  - docs homepage and core routing page
- `docs/install.md`
  - installation and platform notes
- `docs/quickstart.md`
  - first Python and CLI workflows
- `docs/methods.md`
  - methods overview in the top-nav `Methods` group
- `docs/method-matrix.md`
  - generated retained-method comparison table
- `docs/config-reference.md`
  - generated `DecompositionConfig` and method parameter reference
- `docs/notebook-gallery.md`
  - entry page for the GitHub-visible method gallery notebook
- `docs/tutorials/univariate.md`
  - first runnable workflow tutorial with published outputs
- `docs/api.md`
  - public package surface in the top-nav `API` group
- `docs/machine-api.md`
  - schemas, catalog contracts, recommendation, and MCP
- `docs/method-references.md`
  - citations and upstream package links for retained methods
- `docs/comparisons.md`
  - non-core comparison framing under the top-nav `More` group
- `docs/comparison-evidence.md`
  - generated cross-package comparison evidence files

## Examples

- `examples/univariate_quickstart.py`
- `examples/multivariate_mssa.py`
- `examples/method_survey.py`
- `examples/profile_and_cli.py`
- `examples/notebooks/de_time_method_gallery.ipynb`
  - plotted beginner gallery for retained decomposition methods

## Best next files for agents

- open `AGENT_INPUT_CONTRACT.md` before trying to synthesize a wrapper
- open `docs/api.md` before calling programmatic entrypoints
- open `src/detime/registry.py` if you need exact method and input-mode rules
- open `src/detime/io.py` if you need the persisted artifact contract
