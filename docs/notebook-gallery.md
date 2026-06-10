# DeTime Method Gallery

<div class="gallery-intro">
  <p>Explore DeTime's decomposition methods. Each card links to a dedicated page with executable code, output, and a decomposition plot. All examples use compact synthetic data and run quickly.</p>
</div>

<div class="gallery-note">
  <strong>Tip</strong><br>
  Regenerate all assets with <code>python scripts/generate_notebook_gallery.py</code>.
  <a href="#download-gallery">Jump to downloads</a> for the full notebook, Python source, or zipped example.
</div>

## Flagship Methods

<div class="method-card-grid">

<a class="method-card" href="../gallery/ssa/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 36 C30 12 60 58 90 30 S150 14 180 38 S240 60 300 24 S360 10 400 36" stroke="#1F4FFF" stroke-width="2.6" stroke-opacity=".34"/><path d="M0 48 C80 44 160 36 240 28 S340 18 400 16" stroke="#00A6A6" stroke-width="2.2" stroke-opacity=".22"/><path d="M0 56 C20 48 40 62 60 54 S100 46 120 54 S160 62 180 54 S220 46 240 54 S300 62 400 50" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>SSA</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Univariate SSA</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
      <span class="method-badge">flagship</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/std/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 50 C40 48 80 44 120 42 S200 36 280 30 S360 26 400 22" stroke="#1F4FFF" stroke-width="2.8" stroke-opacity=".34"/><path d="M0 36 C14 20 28 52 42 28 S70 16 84 36 S112 54 126 30 S154 18 168 38 S196 56 400 32" stroke="#2D67FF" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 60 C60 58 140 56 200 52 S300 48 400 44" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>STD</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Seasonal-trend decomposition</p>
    <div class="method-card-footer">
      <span class="method-badge badge-channel">channelwise</span>
      <span class="method-badge">flagship</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/stdr/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 50 C40 48 80 44 120 42 S200 36 280 30 S360 26 400 22" stroke="#1F4FFF" stroke-width="2.8" stroke-opacity=".34"/><path d="M0 36 C14 20 28 52 42 28 S70 16 84 36 S112 54 126 30 S154 18 168 38 S196 56 400 32" stroke="#2D67FF" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 60 C60 58 140 56 200 52 S300 48 400 44" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>STDR</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Robust seasonal-trend decomposition</p>
    <div class="method-card-footer">
      <span class="method-badge badge-channel">channelwise</span>
      <span class="method-badge">flagship</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/mssa/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 30 C30 10 60 50 90 26 S150 8 180 34 S240 54 300 20 S360 6 400 30" stroke="#1F4FFF" stroke-width="2.6" stroke-opacity=".34"/><path d="M0 42 C30 22 60 58 90 36 S150 18 180 44 S240 60 300 30 S360 14 400 42" stroke="#00A6A6" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 54 C30 34 60 66 90 48 S150 30 180 56 S240 68 300 40 S360 24 400 54" stroke="#8EC5FF" stroke-width="1.8" stroke-opacity=".18"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>MSSA</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Multivariate SSA</p>
    <div class="method-card-footer">
      <span class="method-badge badge-multi">multivariate</span>
      <span class="method-badge">flagship</span>
    </div>
  </div>
</a>

</div>

## Wrapper Methods

<div class="method-card-grid">

<a class="method-card" href="../gallery/stl/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 50 C40 48 80 44 120 42 S200 36 280 30 S360 26 400 22" stroke="#1F4FFF" stroke-width="2.8" stroke-opacity=".34"/><path d="M0 36 C14 20 28 52 42 28 S70 16 84 36 S112 54 126 30 S154 18 168 38 S196 56 400 32" stroke="#2D67FF" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 60 C60 58 140 56 200 52 S300 48 400 44" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>STL</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Statsmodels STL wrapper</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/mstl/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 50 C40 48 80 44 120 42 S200 36 280 30 S360 26 400 22" stroke="#1F4FFF" stroke-width="2.8" stroke-opacity=".34"/><path d="M0 36 C14 20 28 52 42 28 S70 16 84 36 S112 54 126 30 S154 18 168 38 S196 56 400 32" stroke="#2D67FF" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 60 C60 58 140 56 200 52 S300 48 400 44" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>MSTL</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Statsmodels MSTL wrapper</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/robust-stl/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 50 C40 48 80 44 120 42 S200 36 280 30 S360 26 400 22" stroke="#1F4FFF" stroke-width="2.8" stroke-opacity=".34"/><path d="M0 36 C14 20 28 52 42 28 S70 16 84 36 S112 54 126 30 S154 18 168 38 S196 56 400 32" stroke="#2D67FF" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 60 C60 58 140 56 200 52 S300 48 400 44" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>ROBUST_STL</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Robust STL wrapper</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

</div>

## Empirical & Adaptive Methods

<div class="method-card-grid">

<a class="method-card" href="../gallery/emd/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 36 C12 18 24 54 36 28 S60 8 72 42 S96 58 108 22 S132 6 144 40 S168 56 180 20 S204 8 400 36" stroke="#1F4FFF" stroke-width="2.4" stroke-opacity=".32"/><path d="M0 40 C20 28 40 52 60 36 S100 24 120 44 S160 56 180 32 S220 20 400 40" stroke="#00A6A6" stroke-width="2" stroke-opacity=".22"/><path d="M0 50 C30 46 60 54 90 48 S150 44 180 50 S240 54 270 46 S330 44 400 50" stroke="#9AA8C7" stroke-width="1.6" stroke-opacity=".14"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>EMD</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Empirical mode decomposition</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/ceemdan/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 36 C12 18 24 54 36 28 S60 8 72 42 S96 58 108 22 S132 6 144 40 S168 56 180 20 S204 8 400 36" stroke="#1F4FFF" stroke-width="2.4" stroke-opacity=".32"/><path d="M0 40 C20 28 40 52 60 36 S100 24 120 44 S160 56 180 32 S220 20 400 40" stroke="#00A6A6" stroke-width="2" stroke-opacity=".22"/><path d="M0 50 C30 46 60 54 90 48 S150 44 180 50 S240 54 270 46 S330 44 400 50" stroke="#9AA8C7" stroke-width="1.6" stroke-opacity=".14"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>CEEMDAN</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Noise-assisted EMD</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/vmd/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 36 C30 12 60 58 90 30 S150 14 180 38 S240 60 300 24 S360 10 400 36" stroke="#1F4FFF" stroke-width="2.6" stroke-opacity=".34"/><path d="M0 48 C80 44 160 36 240 28 S340 18 400 16" stroke="#00A6A6" stroke-width="2.2" stroke-opacity=".22"/><path d="M0 56 C20 48 40 62 60 54 S100 46 120 54 S160 62 180 54 S220 46 240 54 S300 62 400 50" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>VMD</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Variational mode decomposition</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/wavelet/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 36 C30 12 60 58 90 30 S150 14 180 38 S240 60 300 24 S360 10 400 36" stroke="#1F4FFF" stroke-width="2.6" stroke-opacity=".34"/><path d="M0 48 C80 44 160 36 240 28 S340 18 400 16" stroke="#00A6A6" stroke-width="2.2" stroke-opacity=".22"/><path d="M0 56 C20 48 40 62 60 54 S100 46 120 54 S160 62 180 54 S220 46 240 54 S300 62 400 50" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>WAVELET</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Wavelet decomposition</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/ma-baseline/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 50 C40 48 80 44 120 42 S200 36 280 30 S360 26 400 22" stroke="#1F4FFF" stroke-width="2.8" stroke-opacity=".34"/><path d="M0 36 C14 20 28 52 42 28 S70 16 84 36 S112 54 126 30 S154 18 168 38 S196 56 400 32" stroke="#2D67FF" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 60 C60 58 140 56 200 52 S300 48 400 44" stroke="#9AA8C7" stroke-width="1.8" stroke-opacity=".16"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>MA_BASELINE</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Moving-average baseline</p>
    <div class="method-card-footer">
      <span class="method-badge ">univariate</span>
    </div>
  </div>
</a>

</div>

## Multivariate & Experimental

<div class="method-card-grid">

<a class="method-card" href="../gallery/mvmd/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 30 C30 10 60 50 90 26 S150 8 180 34 S240 54 300 20 S360 6 400 30" stroke="#1F4FFF" stroke-width="2.6" stroke-opacity=".34"/><path d="M0 42 C30 22 60 58 90 36 S150 18 180 44 S240 60 300 30 S360 14 400 42" stroke="#00A6A6" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 54 C30 34 60 66 90 48 S150 30 180 56 S240 68 300 40 S360 24 400 54" stroke="#8EC5FF" stroke-width="1.8" stroke-opacity=".18"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>MVMD</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Optional multivariate VMD backend</p>
    <div class="method-card-footer">
      <span class="method-badge badge-multi">multivariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/memd/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 30 C30 10 60 50 90 26 S150 8 180 34 S240 54 300 20 S360 6 400 30" stroke="#1F4FFF" stroke-width="2.6" stroke-opacity=".34"/><path d="M0 42 C30 22 60 58 90 36 S150 18 180 44 S240 60 300 30 S360 14 400 42" stroke="#00A6A6" stroke-width="2.2" stroke-opacity=".24"/><path d="M0 54 C30 34 60 66 90 48 S150 30 180 56 S240 68 300 40 S360 24 400 54" stroke="#8EC5FF" stroke-width="1.8" stroke-opacity=".18"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>MEMD</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Optional multivariate EMD backend</p>
    <div class="method-card-footer">
      <span class="method-badge badge-multi">multivariate</span>
    </div>
  </div>
</a>

<a class="method-card" href="../gallery/gabor-cluster/">
  <div class="method-card-art">
    <svg viewBox="0 0 400 72" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke-linecap="round"><path d="M0 36 C40 36 80 20 120 36 S200 52 240 36 S320 20 400 36" stroke="#9AA8C7" stroke-width="2" stroke-opacity=".20"/><circle cx="100" cy="30" r="3" fill="#1F4FFF" fill-opacity=".3"/><circle cx="200" cy="42" r="3" fill="#1F4FFF" fill-opacity=".3"/><circle cx="300" cy="28" r="3" fill="#1F4FFF" fill-opacity=".3"/></g></svg>
  </div>
  <div class="method-card-body">
    <div class="method-card-header">
      <h3>GABOR_CLUSTER</h3>
      <span class="method-card-arrow">→</span>
    </div>
    <p>Experimental Gabor clustering path</p>
    <div class="method-card-footer">
      <span class="method-badge badge-skip">experimental</span>
    </div>
  </div>
</a>

</div>

---

<div class="gallery-summary-section">

## Summary

| Method | Status | Input mode | Trend shape | Residual RMSE |
|---|---|---|---|---:|
| `SSA` | ran | `univariate` | `(96,)` | 0.00000000 |
| `STD` | ran | `channelwise` | `(96,)` | 0.00000000 |
| `STDR` | ran | `channelwise` | `(96,)` | 0.00000000 |
| `MSSA` | ran | `multivariate` | `(96, 3)` | 0.00000000 |
| `STL` | ran | `univariate` | `(96,)` | 0.00000000 |
| `MSTL` | ran | `univariate` | `(96,)` | 0.00000000 |
| `ROBUST_STL` | ran | `univariate` | `(96,)` | 0.00000000 |
| `EMD` | ran | `univariate` | `(96,)` | 0.00000000 |
| `CEEMDAN` | ran | `univariate` | `(96,)` | 0.00000000 |
| `VMD` | ran | `univariate` | `(96,)` | 0.03421948 |
| `WAVELET` | ran | `univariate` | `(96,)` | 0.00000000 |
| `MA_BASELINE` | ran | `univariate` | `(96,)` | 0.00000000 |
| `MVMD` | ran | `multivariate` | `(96, 3)` | 0.08323657 |
| `MEMD` | ran | `multivariate` | `(96, 3)` | 0.00000000 |
| `GABOR_CLUSTER` | skipped | `univariate` | `` | n/a |

Total running time of the gallery script: 4.716 seconds.

Methods run: 14; skipped with explicit reason: 1.

</div>

<a id="download-gallery"></a>

## Downloads

<div class="download-grid">
  <a class="download-card" href="../assets/generated/notebooks/method-gallery/de_time_method_gallery.ipynb">Download Jupyter notebook: <code>de_time_method_gallery.ipynb</code></a>
  <a class="download-card" href="../assets/generated/notebooks/method-gallery/de_time_method_gallery.py">Download Python source code: <code>de_time_method_gallery.py</code></a>
  <a class="download-card" href="../assets/generated/notebooks/method-gallery/de_time_method_gallery.zip">Download zipped example: <code>de_time_method_gallery.zip</code></a>
</div>

The GitHub-rendered notebook is also available at
[examples/notebooks/de_time_method_gallery.ipynb](https://github.com/systems-mechanobiology/DeTime/blob/main/examples/notebooks/de_time_method_gallery.ipynb).
