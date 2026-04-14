# Profiling

Use profiling only after you trust the decomposition output itself. The
`profile` command is for runtime characterization of a workflow you already
understand, not for selecting methods by scoreboard.

## Basic usage

```bash
python -m detime profile \
  --method SSA \
  --series examples/data/example_series.csv \
  --col value \
  --param window=24 \
  --param rank=6 \
  --param primary_period=12 \
  --repeat 5 \
  --warmup 1 \
  --format text
```

Published stdout from the current docs build:

```text
method=SSA
backend_requested=auto
backend_used=native
speed_mode=exact
repeat=5
warmup=1
...
```

Published raw text report:

- [ssa_profile_text.txt](../assets/generated/tutorials/cli-and-profiling/profile/ssa_profile_text.txt)

## Save a report

```bash
python -m detime profile \
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

Published command stdout:

```text
Profile report written to out/profile/std_native.txt
```

Published saved report:

- [std_native.txt](../assets/generated/tutorials/cli-and-profiling/profile/std_native.txt)
- [std_native_stdout.txt](../assets/generated/tutorials/cli-and-profiling/profile/std_native_stdout.txt)

Representative saved report excerpt:

```text
method=STD
backend_requested=native
backend_used=native
speed_mode=exact
repeat=10
warmup=2
...
```

## Multivariate JSON profile

```bash
python -m detime profile \
  --method MSSA \
  --series examples/data/example_multivariate.csv \
  --cols x0,x1 \
  --param window=24 \
  --param primary_period=12 \
  --repeat 3 \
  --format json
```

Published JSON output:

- [mssa_profile.json](../assets/generated/tutorials/cli-and-profiling/profile/mssa_profile.json)

Representative excerpt:

```json
{
  "method": "MSSA",
  "backend_used": "python",
  "columns": ["x0", "x1"],
  "summary": {
    "mean_ms": 11.9110,
    "min_ms": 11.6017,
    "p95_ms": 12.0886
  }
}
```

## Compatibility

The legacy aliases still work for one deprecation cycle:

- `tsdecomp profile`
- `python -m tsdecomp profile`
