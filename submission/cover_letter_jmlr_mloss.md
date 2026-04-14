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

This submission is frozen against version `0.1.1`. Repository metadata,
citation metadata, docs, and submission materials are aligned to that reviewed
release candidate, and the public GitHub tag / PyPI publication should be cut
from the same candidate as `de-time-v0.1.1`. The repository includes:

- tests for the retained public interface,
- strict documentation builds,
- wheel and source-distribution validation,
- artifact-layout checks that verify removed benchmark stubs and transition-era
  compatibility submodules are absent from wheel and sdist payloads,
- a coverage gate of `fail_under = 90` on the canonical core-plus-flagship
  coverage scope,
- schema freshness checks for the packaged JSON schemas,
- native-backed acceleration for selected flagship methods,
- deterministic exact native `SSA` behavior in `speed_mode='exact'`,
- packaged JSON schemas, low-token result modes, and a minimal MCP server for
  tool-based access,
- a dedicated `.[multivar]` smoke path for optional `MVMD` / `MEMD` backends,
- migration guidance from the deprecated `tsdecomp` namespace.

In the latest local release review run, the gated `detime` core-surface
coverage report reached `93.73%`, while the separate package-wide report
reached `84.00%`. We also include a reproducible runtime snapshot showing
native speedups of `7.77x` for `SSA`, `5.82x` for `STD`, and `9.32x` for
`STDR` relative to the Python fallback on one Windows / Python 3.11
installation. Those reviewer-facing details are summarized in
`submission/software_evidence.md`.

We do not position De-Time as a replacement for specialist libraries such as
`statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, `SSALib`, or the maintained
`sktime` VMD path. Instead, we position it as a reproducible workflow layer
that standardizes configuration, result objects, package-level ergonomics, and
selected native acceleration across a fragmented decomposition ecosystem.
Primary method citations and official upstream package links are enumerated in
`submission/software_evidence.md` and the generated docs reference page
`docs/method-references.md`.

Adoption is still early, and we do not claim a large external user community at
this stage. We instead present the public repository, contributor
documentation, issue templates, GitHub Discussions, the documentation site, and
the release/publishing pipeline as auditable openness evidence while broader
usage evidence accumulates.

Sincerely,

Zipeng Wu
