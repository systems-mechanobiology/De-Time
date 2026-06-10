# DeTime

DeTime gives one Python and CLI interface for trend, oscillation, residual,
method-specific components, and metadata across univariate and aligned
multichannel decomposition workflows.

<div class="hero-panel hero-split linear-theme">
  <div class="hero-copy">
    <img class="hero-logo-floating" alt="DeTime logo" src="assets/brand/logo_pure_white_transparent.png">
    <p class="hero-label">Scientific toolkit / workflow system</p>
    <h2>Decompose time series without redesigning the workflow.</h2>
    <p class="hero-kicker">One interface for trend, oscillation, residual, and metadata.</p>
    <p>Give DeTime one series or aligned multichannel data. It returns trend, seasonal or oscillatory structure, residuals, method-specific components, and metadata through the same Python and CLI interface.</p>
    <div class="hero-actions">
      <a href="quickstart/">Run First Example</a>
      <a class="secondary" href="install/">Install from GitHub</a>
    </div>
  </div>
  <div class="hero-visual">
    <div class="product-window" aria-label="DeTime decomposition interface preview">
      <div class="window-topbar">
        <div class="traffic-lights"><span></span><span></span><span></span></div>
        <div class="window-title"><img alt="" src="assets/brand/detime-logo-color.png"></div>
        <div class="window-actions">142 ms</div>
      </div>
      <div class="app-shell">
        <div class="app-sidebar">
          <span class="sidebar-brand"><img alt="" src="assets/brand/detime-mark.svg"> DeTime</span>
          <span class="active">Overview</span>
          <span>Decompose</span>
          <span>Components</span>
          <span>Diagnose</span>
          <span>Export</span>
        </div>
        <div class="app-main">
          <div class="app-head">
            <div>
              <small>STL Decomposition</small>
              <strong>workflow-oriented time-series decomposition</strong>
            </div>
            <button type="button">Run</button>
          </div>
          <div class="signal-grid">
            <div class="signal-row observed"><span>Observed</span><i></i></div>
            <div class="signal-row trend"><span>Trend</span><i></i></div>
            <div class="signal-row seasonal"><span>Seasonal</span><i></i></div>
            <div class="signal-row residual"><span>Residual</span><i></i></div>
          </div>
          <div class="status-line"><span></span> Decomposition complete</div>
        </div>
      </div>
    </div>
    <div class="decomp-motion" aria-label="Animated time-series decomposition preview">
      <div class="motion-orbit">
        <span></span>
        <span></span>
      </div>
      <div class="motion-waves">
        <div class="motion-wave observed"><strong>Observed</strong><i></i></div>
        <div class="motion-wave trend"><strong>Trend</strong><i></i></div>
        <div class="motion-wave residual"><strong>Residual</strong><i></i></div>
      </div>
    </div>
    <div class="hero-points">
      <ul>
        <li>
          <span class="point-icon icon-entry"></span>
          <span><strong>Python and CLI entrypoints</strong><small>Stable commands for decomposition workflows.</small></span>
        </li>
        <li>
          <span class="point-icon icon-method"></span>
          <span><strong>Flagship method support</strong><small><b>SSA</b><b>STD</b><b>STDR</b><b>MSSA</b></small></span>
        </li>
        <li>
          <span class="point-icon icon-evidence"></span>
          <span><strong>Published examples</strong><small>Real stdout, plots, and saved artifacts.</small></span>
        </li>
        <li>
          <span class="point-icon icon-machine"></span>
          <span><strong>Machine-facing schemas</strong><small>Recommendation and low-token result modes for automation.</small></span>
        </li>
      </ul>
    </div>
  </div>
</div>

<div class="trust-strip">
  <span class="trust-pill">Canonical import: <code>detime</code></span>
  <span class="trust-pill">Distribution: <code>de-time</code></span>
  <span class="trust-pill">Flagship methods: SSA / STD / STDR / MSSA</span>
  <span class="trust-pill">Machine-facing schemas and low-token result modes</span>
</div>

## Quant Trading Tutorials

<div class="quant-home-feature">
  <div class="quant-home-copy">
    <span class="section-kicker">New tutorial column</span>
    <h3>Turn market series into audited decomposition features.</h3>
    <p>The quant trading column keeps DeTime in its proper role: a decomposition layer that routes real market inputs into trend, cycle, residual, signal, and backtest research steps.</p>
    <div class="feature-bullets quant-home-bullets">
      <span>10 notebooks for data loading, timing, pairs, factor selection, rotation, adapters, and audit</span>
      <span>Real runtime market data policy for US, Korea, ETF, and crypto examples</span>
      <span>Walk-forward validation before signal evaluation</span>
    </div>
    <div class="hero-actions quant-home-actions">
      <a href="tutorials/quant-trading/">Open Quant Column</a>
      <a class="secondary" href="tutorials/quant-trading/strategy-map/">Strategy Map</a>
    </div>
  </div>
  <div class="quant-workbench" aria-label="Quant trading tutorial research workbench preview">
    <div class="quant-workbench-top">
      <span>DeTime Research</span>
      <b>STL / Walk-forward</b>
      <i>audit ready</i>
    </div>
    <div class="quant-workbench-grid">
      <div class="quant-universe">
        <small>Universe</small>
        <strong>Market inputs</strong>
        <span>SPY</span>
        <span>005930.KS</span>
        <span>BTC-USD</span>
        <em>real data only</em>
      </div>
      <div class="quant-signal-board">
        <div class="quant-price-chart"><span>Observed price</span><i></i></div>
        <div class="quant-component trend"><span>Trend</span><i></i></div>
        <div class="quant-component seasonal"><span>Cycle</span><i></i></div>
        <div class="quant-component residual"><span>Residual</span><i></i></div>
      </div>
      <div class="quant-notebook-stack">
        <small>Notebook path</small>
        <strong>Features -> Signals -> Backtest</strong>
        <span><b>02</b> Timing vectorbt</span>
        <span><b>04</b> Pairs residual</span>
        <span><b>09</b> Validation audit</span>
      </div>
    </div>
  </div>
</div>

## Why DeTime exists

<div class="why-module">
  <div class="why-copy">
    <span class="section-kicker">Reason for the tool</span>
    <h3>A stable workflow layer for time-series decomposition.</h3>
    <p>DeTime exists because decomposition work often moves between notebooks, method-specific wrappers, CLI scripts, and machine-facing automation. The package keeps the method choice flexible while preserving one Python/CLI surface and one result contract.</p>
  </div>
  <div class="why-table">
    <div class="why-row">
      <span>Different decomposition methods expose different interfaces</span>
      <strong>One <code>decompose()</code> entrypoint</strong>
    </div>
    <div class="why-row">
      <span>Results are hard to compare</span>
      <strong>One <code>DecompResult</code> for trend, season, residual, components, and meta</strong>
    </div>
    <div class="why-row">
      <span>CLI and Python workflows often split</span>
      <strong>One <code>DecompositionConfig</code> model across Python and CLI usage</strong>
    </div>
    <div class="why-row">
      <span>Automation needs compact outputs</span>
      <strong>Schemas, recommendations, and low-token result views</strong>
    </div>
  </div>
</div>

## Data in, components out

<div class="feature-section">
  <div class="feature-copy">
    <span class="section-kicker">Workflow</span>
    <h3>Data in, components out</h3>
    <p>DeTime keeps the user-facing contract stable while the method underneath can change. The same shape of result comes back whether you start with a single series or an aligned multichannel panel.</p>
    <div class="feature-bullets">
      <span>1D series or aligned 2D panel</span>
      <span><code>DecompositionConfig(method, params)</code></span>
      <span><code>decompose(...)</code> or <code>detime run</code></span>
      <span>trend, season, residual, components, metadata</span>
    </div>
  </div>
  <div class="pipeline-panel">
    <div class="pipeline-flow">
      <div class="pipeline-step">
        <span class="step-icon icon-input"></span>
        <strong>Input</strong>
        <span>1D series or aligned 2D panel</span>
      </div>
      <div class="pipeline-step">
        <span class="step-icon icon-config"></span>
        <strong>Config</strong>
        <span><code>DecompositionConfig(method, params)</code></span>
      </div>
      <div class="pipeline-step">
        <span class="step-icon icon-run"></span>
        <strong>Run</strong>
        <span><code>decompose(...)</code> or <code>detime run</code></span>
      </div>
      <div class="pipeline-step">
        <span class="step-icon icon-output"></span>
        <strong>Output</strong>
        <span>trend, season, residual, components, metadata</span>
      </div>
    </div>
  </div>
</div>

## Getting Started

<div class="info-grid">
  <a class="info-card" href="install/">
    <span class="card-icon icon-install"></span>
    <h3>Install</h3>
    <p>Current GitHub install path, extras, native build prerequisites, and FAQ.</p>
  </a>
  <a class="info-card" href="quickstart/">
    <span class="card-icon icon-quickstart"></span>
    <h3>Quickstart</h3>
    <p>First successful Python and CLI runs with the retained DeTime surface.</p>
  </a>
  <a class="info-card" href="methods/">
    <span class="card-icon icon-methods"></span>
    <h3>Choose a Method</h3>
    <p>Pick a flagship path quickly before dropping into wrappers or optional backends.</p>
  </a>
  <a class="info-card" href="notebook-gallery/">
    <span class="card-icon icon-notebook"></span>
    <h3>Notebook Gallery</h3>
    <p>GitHub-visible plots and summaries for the retained decomposition methods.</p>
  </a>
</div>

## New Columns

<div class="info-grid">
  <a class="info-card" href="tutorials/quant-trading/">
    <h3>Quant Trading Column</h3>
    <p>Real market data, decomposition features, strategy maps, backtesting adapters, and walk-forward validation.</p>
  </a>
  <a class="info-card" href="tutorials/hot-trend-lab/">
    <h3>Hot Trend Lab</h3>
    <p>Real public-data trend and cycle decomposition for research, open models, developer attention, markets, and crypto.</p>
  </a>
</div>

## Core Reference

<div class="info-grid">
  <a class="info-card" href="methods/">
    <span class="card-icon icon-overview"></span>
    <h3>Methods Overview</h3>
    <p>Method families, maturity levels, and where to start on the retained surface.</p>
  </a>
  <a class="info-card" href="method-matrix/">
    <span class="card-icon icon-matrix"></span>
    <h3>Method Matrix</h3>
    <p>Inputs, maturity, parameters, dependencies, outputs, and recommended use in one table.</p>
  </a>
  <a class="info-card" href="config-reference/">
    <span class="card-icon icon-config-card"></span>
    <h3>Config Reference</h3>
    <p>Top-level <code>DecompositionConfig</code> fields plus per-method parameter semantics.</p>
  </a>
  <a class="info-card" href="api/">
    <span class="card-icon icon-api"></span>
    <h3>API Overview</h3>
    <p>Canonical Python surface, config and result contracts, and CLI summary.</p>
  </a>
</div>

## Workflow Examples

<div class="showcase-grid">
  <a class="showcase-card" href="tutorials/univariate/">
    <img alt="Univariate workflow decomposition" src="assets/generated/home/ssa_components.png">
    <div class="showcase-card-body">
      <span class="card-label">Single-series path</span>
      <h3>Univariate Workflows</h3>
      <p>Follow the retained single-series path from example data to plotted components and saved outputs.</p>
    </div>
  </a>
  <a class="showcase-card" href="tutorials/multivariate/">
    <img alt="Multivariate workflow decomposition" src="assets/generated/home/mssa_multivariate.png">
    <div class="showcase-card-body">
      <span class="card-label">Aligned-channel path</span>
      <h3>Multivariate Workflows</h3>
      <p>Move from aligned channels to shared-structure decomposition and machine-readable result artifacts.</p>
    </div>
  </a>
</div>

## Advanced / Review

<div class="info-grid">
  <a class="info-card" href="comparisons/">
    <span class="card-icon icon-compare"></span>
    <h3>Compare Alternatives</h3>
    <p>When to use DeTime and when to use specialist packages directly.</p>
  </a>
  <a class="info-card" href="reproducibility/">
    <span class="card-icon icon-repro"></span>
    <h3>Reproducibility</h3>
    <p>Coverage boundaries, release checks, generated evidence, and validation commands.</p>
  </a>
  <a class="info-card" href="method-references/">
    <span class="card-icon icon-refs"></span>
    <h3>Method References</h3>
    <p>Primary literature and official upstream package links for retained methods.</p>
  </a>
  <a class="info-card" href="citation/">
    <span class="card-icon icon-cite"></span>
    <h3>Citation / Release Notes</h3>
    <p>Package citation metadata, release notes, and links needed for software review.</p>
  </a>
</div>
