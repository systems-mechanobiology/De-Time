# Profiling

Use profiling only after you trust the decomposition output itself. The
`profile` command is for runtime characterization of a workflow you already
understand, not for selecting methods by scoreboard.

## Basic usage

```bash
detime profile \
  --method SSA \
  --series examples/data/example_series.csv \
  --col value \
  --param window=24 \
  --param rank=6 \
  --param primary_period=12
```

## Save a report

```bash
detime profile \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --backend native \
  --repeat 10 \
  --warmup 2 \
  --format text \
  --output out/profile/std_native.txt
```

## Compatibility

The legacy aliases still work for one deprecation cycle:

- `tsdecomp profile`
- `python -m tsdecomp profile`
