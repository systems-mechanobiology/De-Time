# Scenarios

This page is the shortest route from “what kind of data do I have?” to “what
should I try first?”

## One seasonal scientific signal

Start with:

- `STD`
- `STDR`
- `SSA`

Why:

- these methods are the clearest current De-Time story,
- they are the easiest to interpret visually,
- they are the best first check before moving to larger workflows.

## Multichannel measurements

Start with:

- `MSSA`

Compare against:

- channelwise `STD`
- channelwise `STDR`

Why:

- if channels share structure, a true multivariate method tells a stronger story
  than separate decompositions do,
- channelwise baselines are still useful as a sanity check.

## Adaptive or non-stationary oscillatory structure

Start with:

- `EMD`
- `CEEMDAN`
- `VMD`

Why:

- these methods are useful when fixed seasonal-trend assumptions are too rigid,
- but they should usually come after a stable baseline rather than before it.

## Benchmark-style comparisons

Start with:

- the visual tutorials,
- then `detime profile`,
- then `detime batch`.

Why:

- the fastest way to make a bad benchmark is to skip interpretability checks,
- visual inspection should come before metric sweeps.

## If you are unsure

Use this fallback order:

1. `SSA`
2. `STD`
3. `STDR`
4. `MSSA`

Then open the [Methods Atlas](methods.md) and [Decision Guide](tutorials/decision-guide.md).
