---
hide_toc: true
---

# Why De-Time

De-Time exists because decomposition workflows are often split across
single-method libraries, notebook snippets, and benchmark-only artifacts. That
fragmentation makes it harder to compare methods, preserve metadata, and move
from exploratory work to something another researcher can rerun.

De-Time responds to that problem as software, not as a new method. It standardizes:

- how decomposition is configured,
- how results are returned,
- how CLI and Python usage align,
- how native acceleration and optional backends are surfaced.

The project is deliberately narrow. It aims to be a good decomposition package,
not a general forecasting framework and not a benchmark leaderboard.

That narrow scope also explains why De-Time is positioned beside specialist
libraries rather than against them. The package tries to make decomposition
workflows reproducible and machine-readable, not to declare every specialist
implementation obsolete.

That narrow scope is still relevant to machine learning workflows. In practice,
decomposition is often used before downstream modeling for denoising, feature
extraction, representation shaping, and shared-structure analysis across
channels. De-Time focuses on making those workflow steps reproducible rather
than on claiming a new decomposition algorithm.
