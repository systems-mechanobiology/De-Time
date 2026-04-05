# Cover Letter for JMLR MLOSS Submission

Dear Editors,

We submit **De-Time** for consideration in the *Journal of Machine Learning
Research* Machine Learning Open Source Software track.

De-Time is workflow-oriented research software for reproducible time-series
decomposition. Its contribution is not a new algorithm. Instead, it provides a
clean software surface for configuring, running, profiling, and saving
decomposition workflows that would otherwise be spread across notebook code,
method-specific wrappers, and one-off scripts.

The canonical package namespace is `detime`. The older `tsdecomp` namespace is
retained only as a deprecated compatibility alias. The public software surface
is intentionally narrow and centers on four flagship workflows: `SSA`, `STD`,
`STDR`, and `MSSA`.

This revision also makes a package-boundary change that we consider essential
for software review. Benchmark-oriented artifact code, synthetic benchmark
generators, leaderboard tooling, and benchmark-derived methods were separated
into a companion repository, `de-time-bench`, so that the main submission is a
clean software package rather than a mixed benchmark artifact.

The current review snapshot is installable directly from GitHub. We use that
GitHub installation path in the reviewed documentation because a PyPI release
of `de-time` is still pending. We prefer this explicit pre-release install
story over claiming a broken public `pip install de-time` path.

The repository includes:

- tests for the retained public interface,
- strict documentation builds,
- wheel and source-distribution validation,
- a coverage gate of `fail_under = 90` on the canonical core-plus-flagship
  coverage scope,
- native-backed acceleration for selected flagship methods,
- migration guidance from the deprecated `tsdecomp` namespace.

In the latest local review run, the gated `detime` coverage report reached
`91.25%`. We also include a small runtime snapshot showing that the native path
materially accelerates the retained flagship methods relative to the Python
fallback on one reviewed wheel installation. Those reviewer-facing details are
summarized in `submission/software_evidence.md`.

We do not position De-Time as a replacement for specialist libraries such as
`statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, `SSALib`, or the maintained
`sktime` VMD path. Instead, we position it as a reproducible workflow layer
that standardizes configuration, result objects, package-level ergonomics, and
selected native acceleration across a fragmented decomposition ecosystem.

Adoption is still early, and we do not claim a large external user community
at this stage. The case for the submission is therefore based on software
boundary, installability, testing discipline, packaging hygiene, and workflow
value rather than on broad community scale.

Sincerely,

Zipeng Wu
