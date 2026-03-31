# Agent-Friendly Guide

De-Time is designed to be usable by a person in a notebook and by an agent in
an automated workflow without changing the top-level decomposition contract.

## Identity

- brand-facing name: `De-Time`
- distribution name: `de-time`
- preferred Python import: `detime`
- legacy Python import: `tsdecomp`
- preferred CLI: `detime`
- legacy CLI: `tsdecomp`

## Fastest entrypoints

Use these when you want the shortest path into the package:

- `detime run` for one file
- `detime batch` for multiple files
- `detime profile` for runtime checks
- `decompose(series, DecompositionConfig(...))` for programmatic use

## Shape contract

- `1D` arrays go to univariate methods such as `SSA`, `STD`, and `STDR`
- `2D (T, C)` arrays go to multivariate methods such as `MSSA`, `MVMD`, and `MEMD`
- channelwise methods such as `STD` and `STDR` can accept `2D` arrays but
  decompose each channel independently

## First method to try

| Situation | First method |
|---|---|
| known seasonal period, interpretable decomposition | `STD` or `STDR` |
| strong univariate baseline | `SSA` |
| shared multivariate structure across channels | `MSSA` |
| adaptive or non-stationary oscillatory structure | `EMD`, `CEEMDAN`, or `VMD` |
| adaptive multivariate mode decomposition | `MVMD` or `MEMD` |

## Artifacts to expect

Programmatic calls return one `DecompResult` with:

- `trend`
- `season`
- `residual`
- `components`
- `meta`

CLI calls write:

- `<name>_components.csv`
- `<name>_meta.json`
- optional `<name>_components_3d.npz` for higher-order component stacks

## Backend routing

- use `backend="auto"` by default
- use `backend="native"` only when you want to force native execution or debug
  parity
- use `backend="python"` when you want a strict fallback path

## GitHub-oriented docs

If you want the root-level agent docs in the repository, start with:

- [`AGENT_MANIFEST.md`](https://github.com/systems-mechanobiology/De-Time/blob/main/AGENT_MANIFEST.md)
- [`AGENT_INPUT_CONTRACT.md`](https://github.com/systems-mechanobiology/De-Time/blob/main/AGENT_INPUT_CONTRACT.md)
- [`ENTRYPOINTS.md`](https://github.com/systems-mechanobiology/De-Time/blob/main/ENTRYPOINTS.md)
- [`START_HERE.md`](https://github.com/systems-mechanobiology/De-Time/blob/main/START_HERE.md)
- [`DOCS_INDEX.md`](https://github.com/systems-mechanobiology/De-Time/blob/main/DOCS_INDEX.md)
