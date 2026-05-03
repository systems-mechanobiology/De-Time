# De-Time

De-Time gives one Python and CLI interface for trend, oscillation, residual,
method-specific components, and metadata across univariate and aligned
multichannel decomposition workflows.

<div class="hero-panel hero-split">
  <div class="hero-copy">
    <img class="brand-logo" alt="De-Time logo" src="assets/brand/detime-logo.svg">
    <h2>De-Time</h2>
    <p class="hero-kicker">One interface for trend, oscillation, residual, and metadata.</p>
    <p>Give De-Time one series or aligned multichannel data. It returns trend, seasonal or oscillatory structure, residuals, method-specific components, and metadata through the same Python and CLI interface.</p>
    <div class="hero-actions">
      <a href="quickstart/">Run First Example</a>
      <a class="secondary" href="install/">Install from GitHub</a>
    </div>
  </div>
  <div class="hero-points">
    <ul>
      <li>Stable Python and CLI entrypoints for decomposition workflows</li>
      <li>Flagship support for <code>SSA</code>, <code>STD</code>, <code>STDR</code>, and <code>MSSA</code></li>
      <li>Examples publish real stdout, plots, and saved artifacts</li>
      <li>Machine-facing schemas and recommendation when automation matters</li>
    </ul>
  </div>
</div>

<div class="trust-strip">
  <span class="trust-pill">Canonical import: <code>detime</code></span>
  <span class="trust-pill">Distribution: <code>de-time</code></span>
  <span class="trust-pill">Flagship methods: SSA / STD / STDR / MSSA</span>
  <span class="trust-pill">Machine-facing schemas and low-token result modes</span>
</div>

## Data in, components out

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Input</strong>
      <span>1D series or aligned 2D panel</span>
    </div>
    <div class="pipeline-step">
      <strong>Config</strong>
      <span><code>DecompositionConfig(method, params)</code></span>
    </div>
    <div class="pipeline-step">
      <strong>Run</strong>
      <span><code>decompose(...)</code> or <code>detime run</code></span>
    </div>
    <div class="pipeline-step">
      <strong>Output</strong>
      <span>trend, season, residual, components, metadata</span>
    </div>
  </div>
</div>

## Getting Started

<div class="info-grid">
  <a class="info-card" href="install/">
    <h3>Install</h3>
    <p>Current GitHub install path, extras, native build prerequisites, and FAQ.</p>
  </a>
  <a class="info-card" href="quickstart/">
    <h3>Quickstart</h3>
    <p>First successful Python and CLI runs with the retained De-Time surface.</p>
  </a>
  <a class="info-card" href="methods/">
    <h3>Choose a Method</h3>
    <p>Pick a flagship path quickly before dropping into wrappers or optional backends.</p>
  </a>
  <a class="info-card" href="notebook-gallery/">
    <h3>Notebook Gallery</h3>
    <p>GitHub-visible plots and summaries for the retained decomposition methods.</p>
  </a>
</div>

## Core Reference

<div class="info-grid">
  <a class="info-card" href="methods/">
    <h3>Methods Overview</h3>
    <p>Method families, maturity levels, and where to start on the retained surface.</p>
  </a>
  <a class="info-card" href="method-matrix/">
    <h3>Method Matrix</h3>
    <p>Inputs, maturity, parameters, dependencies, outputs, and recommended use in one table.</p>
  </a>
  <a class="info-card" href="config-reference/">
    <h3>Config Reference</h3>
    <p>Top-level <code>DecompositionConfig</code> fields plus per-method parameter semantics.</p>
  </a>
  <a class="info-card" href="api/">
    <h3>API Overview</h3>
    <p>Canonical Python surface, config and result contracts, and CLI summary.</p>
  </a>
</div>

## Workflow Examples

<div class="showcase-grid">
  <a class="showcase-card" href="tutorials/univariate/">
    <img alt="Univariate workflow decomposition" src="assets/generated/home/ssa_components.png">
    <div class="showcase-card-body">
      <h3>Univariate Workflows</h3>
      <p>Follow the retained single-series path from example data to plotted components and saved outputs.</p>
    </div>
  </a>
  <a class="showcase-card" href="tutorials/multivariate/">
    <img alt="Multivariate workflow decomposition" src="assets/generated/home/mssa_multivariate.png">
    <div class="showcase-card-body">
      <h3>Multivariate Workflows</h3>
      <p>Move from aligned channels to shared-structure decomposition and machine-readable result artifacts.</p>
    </div>
  </a>
</div>

## Advanced / Review

<div class="info-grid">
  <a class="info-card" href="comparisons/">
    <h3>Compare Alternatives</h3>
    <p>When to use De-Time and when to use specialist packages directly.</p>
  </a>
  <a class="info-card" href="reproducibility/">
    <h3>Reproducibility</h3>
    <p>Coverage boundaries, release checks, generated evidence, and validation commands.</p>
  </a>
  <a class="info-card" href="method-references/">
    <h3>Method References</h3>
    <p>Primary literature and official upstream package links for retained methods.</p>
  </a>
  <a class="info-card" href="citation/">
    <h3>Citation / Release Notes</h3>
    <p>Package citation metadata, release notes, and links needed for software review.</p>
  </a>
</div>
