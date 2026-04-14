# Choose a Method

## Default starting points

| Situation | Recommended first method | Why |
|---|---|---|
| One interpretable seasonal signal | `STD` or `STDR` | simple configuration and stable outputs |
| One signal where component grouping matters | `SSA` | flexible component grouping with native support |
| Multiple aligned channels with shared structure | `MSSA` | joint decomposition across channels |
| You already know the main period | `STL` | reliable upstream baseline |

## Use the recommender when

- you want a machine-readable shortlist,
- you need to trade off speed versus accuracy,
- you want to exclude optional backends,
- you want to require native-backed methods.

```bash
detime recommend --length 192 --channels 3 --prefer accuracy
```

## Move to wrappers when

- you specifically need adaptive decompositions such as `EMD`, `CEEMDAN`, or
  `VMD`,
- you need wavelet-based multi-scale structure,
- you need optional multivariate backends such as `MVMD` or `MEMD`.

## Avoid starting with

- experimental wrappers before you have a stable baseline,
- multivariate methods on data that is really just one series,
- deprecated `tsdecomp` imports in new code,
- benchmark-derived methods in this repository, because they live in the
  companion benchmark repository.

Use [Method References](method-references.md) when you need the literature
citations or official upstream package links behind any retained method.
