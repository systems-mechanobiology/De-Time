# Choose a Method

## Default starting points

| Situation | Recommended first method | Why |
|---|---|---|
| One interpretable seasonal signal | `STD` or `STDR` | simple configuration and stable outputs |
| One signal where component grouping matters | `SSA` | flexible component grouping with native support |
| Multiple aligned channels with shared structure | `MSSA` | joint decomposition across channels |
| You already know the main period | `STL` | reliable upstream baseline |

## Move to wrappers when

- you specifically need adaptive decompositions such as `EMD`, `CEEMDAN`, or
  `VMD`,
- you need wavelet-based multi-scale structure,
- you need optional multivariate backends such as `MVMD` or `MEMD`.

## Avoid starting with

- experimental wrappers before you have a stable baseline,
- multivariate methods on data that is really just one series,
- deprecated `tsdecomp` imports in new code,
- benchmark-derived methods in this repository, because they have moved out to
  `de-time-bench`.
