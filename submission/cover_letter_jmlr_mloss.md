# Cover Letter for JMLR MLOSS Submission

Dear Editors,

We submit **De-Time** for consideration in the *Journal of Machine Learning
Research* Machine Learning Open Source Software track.

De-Time is workflow-oriented research software for reproducible time-series
decomposition. Its contribution is not a new algorithm. Instead, it provides a
clean software surface for configuring, running, profiling, saving, and now
machine-serving decomposition workflows that would otherwise be spread across
notebook code, method-specific wrappers, and one-off scripts.

The canonical package namespace is `detime`. The older `tsdecomp` namespace is
retained only as a deprecated top-level import and CLI alias. The public
software surface is intentionally narrow and centers on four flagship
workflows: `SSA`, `STD`, `STDR`, and `MSSA`.

This revision also makes a package-boundary change that we consider essential
for software review. Benchmark-oriented artifact code, synthetic benchmark
generators, leaderboard tooling, and benchmark-derived methods were separated
into a companion repository, `systems-mechanobiology/de-time-bench`, so that
the main submission is a clean software package rather than a mixed benchmark
artifact.

Release `0.1.0` was cut on April 8, 2026 as tag `de-time-v0.1.0` and is
published as the `de-time` PyPI distribution. The repository includes:

- tests for the retained public interface,
- strict documentation builds,
- wheel and source-distribution validation,
- artifact-layout checks that verify removed benchmark stubs and transition-era
  compatibility submodules are absent from wheel and sdist payloads,
- a coverage gate of `fail_under = 90` on the canonical core-plus-flagship
  coverage scope,
- native-backed acceleration for selected flagship methods,
- packaged JSON schemas, low-token result modes, and a minimal MCP server for
  tool-based access,
- migration guidance from the deprecated `tsdecomp` namespace.

In the latest local release review run, the gated `detime` coverage report
reached `93.20%`. We also include a reproducible runtime snapshot showing that
the native path materially accelerates the retained flagship methods relative
to the Python fallback on one released Windows / Python 3.11 installation.
Those reviewer-facing details are summarized in `submission/software_evidence.md`.

We do not position De-Time as a replacement for specialist libraries such as
`statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, `SSALib`, or the maintained
`sktime` VMD path. Instead, we position it as a reproducible workflow layer
that standardizes configuration, result objects, package-level ergonomics, and
selected native acceleration across a fragmented decomposition ecosystem.

Adoption is still early, and we do not claim a large external user community at
this stage. The public repository now exposes issue templates, contributor
documentation, GitHub Discussions, public release notes, and the PyPI
distribution record, which we present as the current minimum auditable
community surface while broader usage evidence accumulates.

Sincerely,

Zipeng Wu
