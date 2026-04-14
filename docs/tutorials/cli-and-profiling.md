# Tutorial: CLI and profiling

The CLI supports five especially useful operational paths:

- `run`
- `batch`
- `profile`
- `schema`
- `recommend`

All commands below use files that ship with this repository.

## Single-file run

```bash
python -m detime run \
  --method SSA \
  --series examples/data/example_series.csv \
  --col value \
  --param window=24 \
  --param rank=6 \
  --param primary_period=12 \
  --out_dir out/ssa \
  --output-mode summary \
  --plot
```

Published stdout from the current docs build:

```text
Running SSA on examples/data/example_series.csv...
Done. Results saved to out/ssa
```

Published output files:

- [example_series_summary.json](../assets/generated/tutorials/cli-and-profiling/single-file/example_series_summary.json)
- [example_series_plot.png](../assets/generated/tutorials/cli-and-profiling/single-file/example_series_plot.png)
- [example_series_error.png](../assets/generated/tutorials/cli-and-profiling/single-file/example_series_error.png)
- [command_stdout.txt](../assets/generated/tutorials/cli-and-profiling/single-file/command_stdout.txt)

Representative summary excerpt:

```json
{
  "mode": "summary",
  "trend": { "shape": [120], "std": 0.6917 },
  "season": { "shape": [120], "std": 0.7036 },
  "residual": { "shape": [120], "l2_norm": 0.0 },
  "meta": {
    "backend_used": "native",
    "method": "SSA",
    "window": 24,
    "rank": 6
  }
}
```

Published plots from the same run:

![CLI single-file decomposition](../assets/generated/tutorials/cli-and-profiling/single-file/example_series_plot.png)

![CLI single-file residual](../assets/generated/tutorials/cli-and-profiling/single-file/example_series_error.png)

## Multivariate run

```bash
python -m detime run \
  --method MSSA \
  --series examples/data/example_multivariate.csv \
  --cols x0,x1 \
  --param window=24 \
  --param rank=8 \
  --param primary_period=12 \
  --out_dir out/mssa \
  --output-mode summary
```

Published stdout from the current docs build:

```text
Running MSSA on examples/data/example_multivariate.csv...
Done. Results saved to out/mssa
```

Published output files:

- [example_multivariate_summary.json](../assets/generated/tutorials/cli-and-profiling/multivariate/example_multivariate_summary.json)
- [command_stdout.txt](../assets/generated/tutorials/cli-and-profiling/multivariate/command_stdout.txt)

Representative summary excerpt:

```json
{
  "mode": "summary",
  "trend": { "shape": [120, 2] },
  "season": { "shape": [120, 2] },
  "components": {
    "modes": { "shape": [8, 120, 2] }
  },
  "meta": {
    "backend_used": "python",
    "channel_names": ["x0", "x1"]
  }
}
```

## Batch processing

```bash
python -m detime batch \
  --method STD \
  --glob "examples/data/batch/*.csv" \
  --col value \
  --param period=12 \
  --out_dir out/std_batch \
  --output-mode meta
```

Published stdout from the current docs build:

```text
Found 2 files. Processing...
```

Published output files:

- [series_a_meta.json](../assets/generated/tutorials/cli-and-profiling/batch/series_a_meta.json)
- [series_b_meta.json](../assets/generated/tutorials/cli-and-profiling/batch/series_b_meta.json)
- [command_stdout.txt](../assets/generated/tutorials/cli-and-profiling/batch/command_stdout.txt)

Representative `meta` payload excerpt from `series_a_meta.json`:

```json
{
  "mode": "meta",
  "meta": {
    "method": "STD",
    "period": 12,
    "n_cycles": 2,
    "backend_used": "native",
    "input_shape": [24]
  },
  "diagnostics": {
    "component_names": ["dispersion", "seasonal_shape"]
  }
}
```

## Runtime profiling

Text output now respects `--format text` on stdout as well as saved reports.

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

Raw text report:

- [ssa_profile_text.txt](../assets/generated/tutorials/cli-and-profiling/profile/ssa_profile_text.txt)

For multivariate JSON profiling:

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
  "repeat": 3,
  "summary": {
    "mean_ms": 11.9110,
    "min_ms": 11.6017,
    "p95_ms": 12.0886
  }
}
```

## Backend selection and saved reports

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

## Machine-facing helpers

```bash
python -m detime schema --name method-registry
python -m detime recommend --length 192 --channels 3 --prefer accuracy --format text
```

Published outputs:

- [method_registry_schema.json](../assets/generated/tutorials/cli-and-profiling/machine/method_registry_schema.json)
- [recommend_text.txt](../assets/generated/tutorials/cli-and-profiling/machine/recommend_text.txt)
- [recommend.json](../assets/generated/tutorials/cli-and-profiling/machine/recommend.json)

Published recommendation text excerpt:

```text
1. MSSA (13.50)
   Multivariate SSA for shared-structure decomposition across channels.
2. STDR (11.75)
   Robust seasonal-trend decomposition for noisier periodic signals.
3. STD (9.25)
   Fast seasonal-trend decomposition with dispersion-aware diagnostics.
```
