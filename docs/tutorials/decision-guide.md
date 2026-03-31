# Decision guide: how to read plots and choose a method

This page is the shortest path from "I have a signal" to "I know what to try
first and how to judge whether the result is believable."

## Choose by situation

<div class="decision-grid">
  <div class="decision-card">
    <h3>Known period, interpretable baseline</h3>
    <p>Start with <code>STD</code>, <code>STDR</code>, or <code>STL</code>. These are the easiest methods to explain to other people.</p>
  </div>
  <div class="decision-card">
    <h3>Need a strong general univariate baseline</h3>
    <p>Start with <code>SSA</code>. It is usually the best first flexible method when you do not want to over-commit to one rigid seasonal model.</p>
  </div>
  <div class="decision-card">
    <h3>Several channels share structure</h3>
    <p>Start with <code>MSSA</code>. Compare it against channelwise <code>STD</code> to see whether joint structure is actually helping.</p>
  </div>
  <div class="decision-card">
    <h3>Oscillatory or non-stationary signals</h3>
    <p>Try <code>EMD</code>, <code>CEEMDAN</code>, or <code>VMD</code> when the signal is better described as modes than as one stable seasonal pattern.</p>
  </div>
</div>

## First-pass method selection

| Situation | First method | Second method | What you are testing |
|---|---|---|---|
| regular seasonality, known period | `STD` | `STL` | whether a simpler seasonal-trend split is enough |
| smooth drift plus repeating cycle | `SSA` | `STDR` | whether a subspace method gives a cleaner trend |
| multichannel sensors with one shared driver | `MSSA` | channelwise `STD` | whether joint structure changes interpretation |
| frequency-rich or modal behavior | `VMD` | `EMD` | whether modal decomposition fits better than seasonal decomposition |
| fast sanity-check baseline | `MA_BASELINE` | `STD` | whether the signal deserves a more serious method |

## How to read decomposition plots

### Trend panel

Good signs:

- smooth where the underlying drift should be smooth,
- changes direction only when the original series justifies it,
- stays free of obvious seasonal oscillation.

Bad signs:

- jagged trend that still wiggles at the seasonal frequency,
- trend that is nearly flat when the signal clearly drifts,
- sudden step artifacts caused by an overly rigid method or bad window choice.

### Seasonal panel

Good signs:

- stable repeated shape when a real period exists,
- amplitude consistent with the visible oscillation in the original series,
- phase that lines up with the observed cycle.

Bad signs:

- a seasonal curve that slowly drifts like a trend,
- obvious phase shift relative to the observed peaks,
- invented oscillation in places where the signal looks mostly monotone.

### Residual panel

Good signs:

- low-amplitude background noise,
- local spikes only near abrupt events or hard-to-model regions.

Bad signs:

- long coherent structure still sitting in the residual,
- residual that looks more seasonal than the seasonal panel,
- residual that keeps broad drift the trend should have absorbed.

## How to read overlay plots

Trend overlay:

- use it first when comparing methods,
- if one trend is much more wiggly, it is usually leaking seasonal energy,
- if one trend is much flatter than the others, it may be over-smoothing.

Seasonal overlay:

- useful for amplitude and phase agreement,
- if one seasonal curve is phase-shifted, you may be seeing a mismatch between method assumptions and the real cycle.

## How to read multivariate panels

For true joint methods such as `MSSA`:

- look for cross-channel consistency,
- check whether related channels share similar low-frequency structure,
- verify that one noisy channel is not dominating the others.

For channelwise baselines:

- use them as a control,
- if `MSSA` and channelwise `STD` look nearly identical, the joint method may not be buying much.

## How to read heatmaps

Trend `R2`:

- higher is better,
- good for overall trend recovery quality.

Trend `DTW`:

- lower is better,
- useful when shape alignment matters more than pointwise equality.

Seasonal spectral correlation:

- higher is better,
- tells you whether the seasonal frequency content is right.

Seasonal max-lag correlation:

- higher is better,
- useful for spotting phase errors.

## Recommended workflow

1. Start with one visual tutorial on your nearest matching scenario.
2. Compare 2 to 4 methods, not 10.
3. Inspect trend overlay before looking at scalar metrics.
4. Use residual structure to diagnose what the method missed.
5. Only then run a wider benchmark or profile sweep.

## Best next pages

- [Visual Univariate Walkthrough](visual-univariate.md)
- [Visual Method Comparison](visual-comparison.md)
- [Visual Multivariate Walkthrough](visual-multivariate.md)
- [Visual Benchmark Heatmaps](visual-benchmark.md)
