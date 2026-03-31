# Profiling and benchmarking

## Profiling a single method

`detime` includes a `profile` command so runtime and backend information can
be recorded in a consistent way.

```bash
detime profile \
  --method SSA \
  --series examples/data/example_series.csv \
  --col value \
  --param window=24 \
  --param primary_period=12 \
  --repeat 5 \
  --warmup 1
```

## Backend selection

For methods that support native acceleration:

- `backend=auto` prefers native when available,
- `backend=native` requires the native implementation,
- `backend=python` forces the Python path.

## Speed mode

The runtime also carries a `speed_mode`.

- `exact` is the default
- `fast` is currently most meaningful for methods such as `MSSA`, where the
  implementation can switch to approximate SVD

## Benchmark-oriented usage

For reproducible sweeps:

- keep method parameters explicit,
- record `backend_used` from the result metadata,
- prefer scripts checked into `examples/` over ad hoc notebooks.

Legacy compatibility:

- `tsdecomp profile` still works
- `python -m tsdecomp profile ...` still works
