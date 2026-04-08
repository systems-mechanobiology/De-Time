# Tutorial: CLI and profiling

The CLI supports three especially useful operational paths:

- `run`
- `batch`
- `profile`
- `schema`
- `recommend`

## Single-file run

```bash
python -m detime run \
  --method SSA \
  --series data/monthly.csv \
  --col value \
  --param window=24 \
  --param rank=6 \
  --param primary_period=12 \
  --out_dir out/ssa \
  --output-mode summary
```

## Multivariate run

```bash
python -m detime run \
  --method MSSA \
  --series data/panel.csv \
  --cols channel_a,channel_b \
  --param window=24 \
  --param rank=6 \
  --param primary_period=12 \
  --out_dir out/mssa
```

## Batch processing

```bash
python -m detime batch \
  --method STD \
  --glob "data/*.csv" \
  --col value \
  --param period=12 \
  --out_dir out/std_batch \
  --output-mode meta
```

## Runtime profiling

```bash
python -m detime profile \
  --method SSA \
  --series data/monthly.csv \
  --col value \
  --param window=24 \
  --param rank=6 \
  --repeat 5 \
  --warmup 1 \
  --format text
```

For multivariate inputs:

```bash
python -m detime profile \
  --method MSSA \
  --series data/panel.csv \
  --cols channel_a,channel_b \
  --param window=24 \
  --param primary_period=12 \
  --repeat 3 \
  --format json
```

## Backend selection

Methods that support native acceleration can be steered explicitly:

```bash
python -m detime profile \
  --method STD \
  --series data/monthly.csv \
  --col value \
  --param period=12 \
  --backend native
```

Or left to automatic selection:

```bash
python -m detime profile \
  --method STD \
  --series data/monthly.csv \
  --col value \
  --param period=12 \
  --backend auto
```

## Machine-facing helpers

```bash
python -m detime schema --name method-registry
python -m detime recommend --length 192 --channels 3 --prefer accuracy
```
