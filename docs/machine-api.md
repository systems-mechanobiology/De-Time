# Machine API

De-Time exposes a local-first machine-facing surface for agents, scripts, and
workflow tooling that need something more structured than the human-facing
README.

## Contract scope

The current machine contract series is `0.1`. Within this series, the package
aims to keep the following stable:

- schema names: `config`, `result`, `meta`, `method-registry`
- MCP tool names
- the core method-catalog field set
- the `full` / `summary` / `meta` serialization modes

Breaking machine-facing changes should land with a package minor bump rather
than as a silent patch-level surprise.

## Schema assets

Packaged JSON schemas live under `src/detime/schema_assets/` and are also
available through:

- `detime schema --name config`
- `detime schema --name result`
- `detime schema --name meta`
- `detime schema --name method-registry`

These schemas are intended for validation, tool wiring, and regression checks,
not just for documentation.

The `method-registry` payload now exposes stable root metadata fields:

- `package`
- `version`
- `contract_version`
- `methods`

Consumers should key compatibility checks off `contract_version` and treat
`version` as the package release identifier for the generated catalog bundle.

## Stable catalog fields

`MethodRegistry.list_catalog()` is the machine-readable source of truth for the
public method catalog. Every entry is expected to expose at least:

- `family`
- `maturity`
- `implementation`
- `dependency_tier`
- `multivariate_support`
- `native_backed`
- `min_length`
- `summary`
- `recommended_for`
- `typical_failure_modes`

The current catalog also carries assumptions, not-recommended cases, and
optional-dependency hints so the generated method cards and MCP responses stay
aligned. It now also carries structured `references` and `package_links`
arrays so machine consumers can trace each retained method back to its
literature and official upstream project pages.

## Recommendation interface

`detime recommend` and the MCP `recommend_method` tool provide the same routing
surface:

- input length
- channel count
- speed / balanced / accuracy preference
- whether optional backends are allowed
- whether native-backed methods are required

This lets an agent shortlist methods before touching any full decomposition
payloads.

## Serialization modes

De-Time intentionally separates artifact size from decomposition execution.
Machine consumers can request:

- `full`
  - complete serialized arrays
- `summary`
  - array shapes plus summary statistics and diagnostics
- `meta`
  - metadata and diagnostics only

The recommended progressive-disclosure path is:

1. ask for `meta` or `summary`
2. inspect diagnostics and backend metadata
3. request `full` only if downstream logic truly needs raw arrays

Token-budget evidence for these modes is summarized in
[Token Benchmarks](token-benchmarks.md). That page is kept as a reference
appendix rather than a primary navigation item.

## MCP surface

The MCP server is available at:

```bash
python -m detime.mcp.server
```

Current status:

- local-first
- stdio transport
- no hosted remote endpoint claimed
- intended for deterministic tool access rather than free-form prompting

Stable tools in the current surface:

- `list_methods`
- `get_schema`
- `recommend_method`
- `run_decomposition`
- `summarize_result`

Recommended tool subsets:

- routing only: `list_methods`, `recommend_method`, `get_schema`
- bounded-context execution: add `run_decomposition` in `summary` or `meta`
  mode
- post-hoc condensation: add `summarize_result`

## Artifact contract

Programmatic calls return one `DecompResult`. CLI calls persist one of the
following artifact patterns:

- `*_components.csv`
- `*_meta.json`
- optional `*_components_3d.npz`
- `*_summary.json`
- `*_full.json`

Agents should prefer `meta.result_layout`, `meta.n_channels`, and
`meta.channel_names` over filename inference.
