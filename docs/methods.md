# Methods & Chooser

Start with the four retained flagship paths. Move to wrappers only when the
data or comparison need points there.

## Flagship method cards

<div class="method-use-grid">
  <div class="method-use-card">
    <h3><code>SSA</code></h3>
    <p><strong>Use when:</strong> one series needs interpretable subspace components.</p>
    <p><strong>Avoid when:</strong> the series is too short for a meaningful window.</p>
    <p><strong>Key params:</strong> <code>window</code>, <code>rank</code>, <code>primary_period</code>.</p>
  </div>
  <div class="method-use-card">
    <h3><code>STD</code></h3>
    <p><strong>Use when:</strong> a known seasonal period should split trend, season, and dispersion quickly.</p>
    <p><strong>Avoid when:</strong> the main period is unknown or unstable.</p>
    <p><strong>Key params:</strong> <code>period</code>.</p>
  </div>
  <div class="method-use-card">
    <h3><code>STDR</code></h3>
    <p><strong>Use when:</strong> the same seasonal-trend task has outliers or noisier cycles.</p>
    <p><strong>Avoid when:</strong> structural breaks dominate the seasonal pattern.</p>
    <p><strong>Key params:</strong> <code>period</code>.</p>
  </div>
  <div class="method-use-card">
    <h3><code>MSSA</code></h3>
    <p><strong>Use when:</strong> aligned channels share trend or oscillatory structure.</p>
    <p><strong>Avoid when:</strong> channels are unrelated or one univariate method is enough.</p>
    <p><strong>Key params:</strong> <code>window</code>, <code>rank</code>, <code>primary_period</code>.</p>
  </div>
</div>

## Decision flow

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>One regular seasonal series?</strong>
      <span>Start with <code>STD</code>. Use <code>STDR</code> if outliers matter.</span>
    </div>
    <div class="pipeline-step">
      <strong>One series, unknown components?</strong>
      <span>Start with <code>SSA</code>, then compare against <code>STD</code> or <code>STL</code>.</span>
    </div>
    <div class="pipeline-step">
      <strong>Aligned channels?</strong>
      <span>Use <code>MSSA</code> for shared structure; use <code>STD</code> channelwise for a fast baseline.</span>
    </div>
    <div class="pipeline-step">
      <strong>Need a specialist family?</strong>
      <span>Move to <code>EMD</code>, <code>CEEMDAN</code>, <code>VMD</code>, <code>WAVELET</code>, <code>MVMD</code>, or <code>MEMD</code>.</span>
    </div>
  </div>
</div>

## Wrapper use cases

| Method | Typical scenario | First parameter to check |
|---|---|---|
| `STL` | classical seasonal-trend baseline for one known period | `period` |
| `MSTL` | one series with multiple seasonal periods | `periods` |
| `ROBUST_STL` | STL-style baseline with outliers | `period` |
| `EMD` | adaptive IMF inspection for nonlinear signals | `n_imfs` |
| `CEEMDAN` | noise-assisted EMD when mode stability matters | `trials` |
| `VMD` | band-limited modes with a chosen mode count | `K`, `alpha` |
| `WAVELET` | multiscale signal inspection | `wavelet`, `level` |
| `MVMD` | optional multivariate VMD through PySDKit | `K`, `alpha` |
| `MEMD` | optional multivariate EMD through PySDKit | `primary_period` |

## More detail

- [Method Matrix](method-matrix.md) gives a compact table across input mode,
  maturity, dependencies, parameters, outputs, and recommended use.
- [Config Reference](config-reference.md) documents exact
  `DecompositionConfig` fields and method-specific parameters.
- [Method References](method-references.md) collects primary literature and
  official package links.
- [Notebook Gallery](notebook-gallery.md) shows runnable plots for the retained
  method surface.
