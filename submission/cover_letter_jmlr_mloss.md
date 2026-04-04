# Cover Letter for JMLR MLOSS Submission

Dear Editors,

We submit **De-Time** for consideration in the *Journal of Machine Learning
Research* Machine Learning Open Source Software track.

De-Time is research software for reproducible time-series decomposition. Its
contribution is not a new algorithm. Instead, it provides a coherent software
surface for decomposition workflows that are otherwise split across
method-specific libraries, notebook code, and one-off scripts. The package
standardizes configuration, result objects, CLI usage, saved outputs, and
native capability reporting.

The canonical package name is `detime` and the distribution name is `de-time`.
The legacy `tsdecomp` import and CLI are retained only as a deprecated
compatibility alias. The main software surface is intentionally narrow and now
centers on four flagship workflows: `SSA`, `STD`, `STDR`, and `MSSA`.

During revision we also separated benchmark-oriented artifacts from the main
package. Synthetic benchmark generators, leaderboard tooling, and
benchmark-derived methods were moved out of the core software boundary into a
companion repository, `de-time-bench`. This split was made so that the JMLR
submission reflects a clean software package rather than a mixed
library-plus-benchmark artifact.

The repository includes:

- documented installation and usage,
- tests for the retained public interface,
- CI for package, documentation, and build validation,
- native kernels for selected flagship methods,
- migration guidance from the legacy `tsdecomp` namespace.

The submission does not claim to replace specialist libraries such as
`statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, or SSA-focused tools. Instead,
De-Time is positioned as workflow-oriented research software that integrates
selected decomposition methods behind a stable interface and clear boundary.

Sincerely,

Zipeng Wu
