# Comparison Evidence

Generated for De-Time `0.1.1` on 2026-04-14T22:07:10.282587+00:00.

## Capability matrix

| package | primary_scope | unified_config_object | unified_result_object | machine_readable_catalog | batch_cli | profiling_path | multivariate_support | maturity_labeling | compact_output | mcp_tool_surface |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| De-Time | workflow-oriented decomposition layer | yes | yes | yes | yes | yes | yes | explicit | yes | yes |
| statsmodels | classical decomposition and modeling | no | partial | no | no | no | limited | implicit | no | no |
| PyEMD | EMD-family toolkit | no | no | no | no | no | family-specific | family-specific | no | no |
| PyWavelets | wavelet toolkit | no | no | no | no | no | transform-specific | family-specific | no | no |
| PySDKit | signal decomposition toolkit | partial | partial | no | limited | no | yes | less explicit | no | no |
| SSALib | SSA specialist toolkit | SSA-specific | SSA-specific | no | no | no | no | focused | no | no |
| sktime | broad time-series ecosystem | no | no | no | no | no | partial | ecosystem-level | no | no |

## Install and reproducibility matrix

| package | public_release_story | pypi_path | github_release | wheels | ci_platforms | docs_website | tutorials | api_docs | coverage_disclosure | reproducibility_script |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| De-Time | 0.1.1 target from main | tag-driven publish workflow | de-time-v0.1.1 | yes | ubuntu, macOS, windows | GitHub Pages | yes | yes | dual report | yes |
| statsmodels | yes | yes | yes | yes | yes | yes | yes | yes | project-dependent | project-dependent |
| PyEMD | yes | yes | yes | partial | project-dependent | partial | partial | partial | project-dependent | no |
| PyWavelets | yes | yes | yes | yes | yes | yes | yes | yes | project-dependent | no |
| PySDKit | yes | yes | yes | partial | project-dependent | yes | partial | partial | project-dependent | no |
| SSALib | yes | yes | yes | partial | project-dependent | yes | partial | partial | project-dependent | no |
| sktime | yes | yes | yes | yes | yes | yes | yes | yes | project-dependent | project-dependent |

## Family-fairness notes

| family | specialist | specialist_deeper_strength | de_time_position |
| --- | --- | --- | --- |
| classical decomposition | statsmodels | deeper classical decomposition and statistical modeling | wraps STL and MSTL under one config/result/CLI layer |
| SSA | SSALib | deeper SSA-only environment with SSA-specific tooling | uses SSA as one flagship method inside a cross-family workflow layer |
| EMD family | PyEMD | deeper EMD-family tooling | exposes EMD and CEEMDAN through the same contract used for other families |
| wavelet workflows | PyWavelets | deeper wavelet transforms and transform-specific APIs | uses wavelets as one workflow option rather than a wavelet-first toolkit |
| unified toolkit layer | PySDKit | broader signal-decomposition toolkit with optional multivariate backends | focuses on time-series decomposition workflows, machine-facing contracts, and compact outputs |

## Agent-facing matrix

| package | json_schema_assets | compact_result_modes | recommend_interface | machine_readable_catalog | mcp_surface | artifact_contract | token_benchmark | tool_evals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| De-Time | yes | full/summary/meta | yes | yes | local-first | yes | yes | yes |
| statsmodels | no | no | no | no | no | no | no | no |
| PyEMD | no | no | no | no | no | no | no | no |
| PyWavelets | no | no | no | no | no | no | no | no |
| PySDKit | no | no | no | no | no | no | no | no |
| SSALib | no | no | no | no | no | no | no | no |
| sktime | no | no | no | no | no | no | no | no |

## Runtime snapshot source

- `docs\assets\generated\evidence\performance_snapshot.csv`
