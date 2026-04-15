# De-Time

De-Time is workflow-oriented research software for reproducible time-series
decomposition. It gives you one public package, one decomposition contract, and
one docs surface across univariate, multivariate, native-backed, and
machine-facing workflows.

<div class="hero-panel hero-split">
  <div class="hero-copy">
    <h2>De-Time</h2>
    <p class="hero-kicker">Workflow-oriented time-series decomposition software</p>
    <p>One package, one decomposition contract, and one docs surface across univariate, multivariate, native-backed, and machine-facing workflows.</p>
    <div class="hero-actions">
      <a href="quickstart/">Get Started</a>
      <a class="secondary" href="install/">Install</a>
    </div>
  </div>
  <div class="hero-points">
    <ul>
      <li>Stable Python and CLI entrypoints for decomposition workflows</li>
      <li>Flagship support for <code>SSA</code>, <code>STD</code>, <code>STDR</code>, and <code>MSSA</code></li>
      <li>Machine-facing schemas, recommendation, and MCP support</li>
      <li>Reproducible docs, evidence artifacts, and release validation</li>
    </ul>
  </div>
</div>

<div class="trust-strip">
  <span class="trust-pill">Canonical import: <code>detime</code></span>
  <span class="trust-pill">Distribution: <code>de-time</code></span>
  <span class="trust-pill">Flagship methods: SSA / STD / STDR / MSSA</span>
  <span class="trust-pill">Machine-facing schemas and low-token result modes</span>
</div>

## What it is

- A canonical Python package with import path `detime`.
- A stable `decompose()` entrypoint plus `DecompositionConfig` and
  `DecompResult`.
- A documentation set centered on practical workflows rather than benchmark
  scoreboards.
- A package whose flagship methods are `SSA`, `STD`, `STDR`, and `MSSA`.
- A machine-facing surface with schemas, recommendations, and a minimal MCP
  server.

## What it is not

- Not a new decomposition algorithm.
- Not a benchmark-paper artifact disguised as a library.
- Not a replacement for every specialized upstream implementation.
- Not a promise that every wrapper has the same maturity as the flagship path.

## Getting Started

<div class="info-grid">
  <a class="info-card" href="install/">
    <h3>Install</h3>
    <p>Public install path, extras, native build prerequisites, and troubleshooting.</p>
  </a>
  <a class="info-card" href="quickstart/">
    <h3>Quickstart</h3>
    <p>First successful Python and CLI runs with the retained De-Time surface.</p>
  </a>
  <a class="info-card" href="choose-a-method/">
    <h3>Choose a Method</h3>
    <p>Pick a flagship path quickly before dropping into wrappers or optional backends.</p>
  </a>
  <a class="info-card" href="tutorials/univariate/">
    <h3>Univariate Tutorial</h3>
    <p>Step-by-step workflow with real generated outputs published on the page.</p>
  </a>
</div>

## Core Reference

<div class="info-grid">
  <a class="info-card" href="methods/">
    <h3>Methods Overview</h3>
    <p>Method families, maturity levels, and where to start on the retained surface.</p>
  </a>
  <a class="info-card" href="method-cards/">
    <h3>Method Cards</h3>
    <p>Per-method assumptions, failure modes, and recommended use cases.</p>
  </a>
  <a class="info-card" href="api/">
    <h3>API Overview</h3>
    <p>Canonical Python surface, config and result contracts, and CLI summary.</p>
  </a>
  <a class="info-card" href="machine-api/">
    <h3>Machine API</h3>
    <p>Schemas, catalog contracts, recommendation flow, and MCP entrypoints.</p>
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
    <h3>Comparisons</h3>
    <p>Position De-Time relative to specialist packages without overselling replacement claims.</p>
  </a>
  <a class="info-card" href="reproducibility/">
    <h3>Reproducibility</h3>
    <p>Coverage boundaries, release checks, generated evidence, and validation workflow.</p>
  </a>
  <a class="info-card" href="method-references/">
    <h3>Method References</h3>
    <p>Primary literature and official upstream package links for the retained methods.</p>
  </a>
  <a class="info-card" href="citation/">
    <h3>Citation / Release Notes</h3>
    <p>Package citation metadata, release notes, and links needed for software review.</p>
  </a>
</div>

## Package boundary

This repository ships the software package itself. Companion benchmark
artifacts live in the separate
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench)
repository. The main package no longer exposes benchmark orchestration,
leaderboard helpers, or benchmark-derived methods.

The legacy `tsdecomp` import and CLI still resolve to De-Time, but only as a
deprecated compatibility alias through `0.1.x`.
