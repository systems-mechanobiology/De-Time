Dear Editors,

Please consider our submission describing De-Time, an open-source software
package for time-series decomposition research, for the JMLR MLOSS track.

De-Time is the software brand. For distribution we refer to the package as
`de-time`, with preferred import name `detime` and legacy import `tsdecomp`
maintained for compatibility during transition.

De-Time provides a unified Python API and CLI across multiple decomposition
families, including classical seasonal-trend methods, empirical mode methods,
wavelet and variational decompositions, and multivariate workflows. A central
goal of the package is to make decomposition methods easier to compare, run,
profile, and integrate into research pipelines without forcing users to work
through a benchmark-specific codebase or a collection of unrelated scripts.

The package is openly released under the BSD 3-Clause License. The software
version under review is `0.1.0`. The current public project locations are:

- Repository: https://github.com/systems-mechanobiology/De-Time
- Issue tracker: https://github.com/systems-mechanobiology/De-Time/issues
- Documentation website: https://systems-mechanobiology.github.io/De-Time/

The package includes:

- a public API centered on `DecompositionConfig`, `DecompResult`, and
  `decompose(...)`,
- command-line workflows for single-run execution, batch execution, and runtime
  profiling,
- native C++ acceleration with Python fallback for selected higher-cost methods
  such as `SSA`, `STD`, `STDR`, and `DR_TS_REG`,
- multivariate support under the same top-level API for `MSSA`, `MVMD`, `MEMD`,
  and channelwise `STD` / `STDR`,
- package-level tests, automated CI, source-distribution rules, contributor
  documentation, and user-facing documentation with runnable examples.

We disclose a significantly overlapping prior/concurrent manuscript:

- `Time-Series Decomposition as a standalone Task: A Mechanism-Identifiable Benchmark`
  is currently under review as a benchmark paper. That manuscript focuses on
  task definition, synthetic evaluation, metrics, empirical findings, and a
  downstream symbolic-regression study. The present submission instead focuses
  on the standalone software package: package architecture, public API and CLI,
  build and distribution engineering, selective native acceleration,
  multivariate support, documentation, testing, and reproducibility workflows.

This software paper is intended to present the package as a reusable research
tool, not as a benchmark-results paper. Earlier versions of the code lived
inside a broader benchmark-oriented repository and paper artifact. The current
software package differs from that earlier form in several important ways:

- it has been extracted into a standalone package with explicit build and
  release metadata,
- it exposes a coherent public API and CLI rather than requiring direct use of
  benchmark orchestration code,
- it includes improved documentation, examples, tests, and CI,
- it adds native acceleration and multivariate support within a unified package
  interface,
- it is packaged for software review independently of the original benchmark
  artifact.

The clearest software contribution is the combination of:

1. a unified interface across heterogeneous decomposition methods,
2. a practical runtime model with Python and native backends,
3. multivariate support without a separate top-level API,
4. software-engineering improvements that make the package reviewable and
   reusable as standalone open-source research software.

The strongest and most mature current methods in the package are `STD`, `STDR`,
`SSA`, `MSSA`, and `DR_TS_REG`. We are careful not to present every included
wrapper method as equally mature. Some methods still rely on optional upstream
libraries or internal compatibility code, and the package documentation makes
those boundaries explicit.

Regarding evidence of adoption and user community, we can honestly report that
external public adoption is still early because the software has only recently
been extracted into standalone package form. We therefore do not claim a large
public user base yet. Instead, we ask that the software be evaluated on its
engineering quality, documentation, testing, packaging, and scope for reuse.

For nearby software, our positioning is as follows. `statsmodels` covers
classical decomposition such as STL and MSTL, but not a cross-family
decomposition interface; `PyEMD`, `PyWavelets`, and `PySDKit` provide narrower
family-specific functionality. De-Time is not presented as a replacement for
those specialized libraries. Its software contribution is a unified result
model and execution interface across heterogeneous methods, multivariate
support under the same API, selective native acceleration for high-cost
methods, and runnable CLI and profiling workflows in one package.

We also confirm that all co-authors are aware of this submission and consent to
its review by JMLR. Any funding disclosures, conflicts of interest, suggested
action editors, suggested reviewers, and keywords will be supplied in the final
submission package.

We believe De-Time fits the JMLR MLOSS scope as a non-trivial research
software package whose main value lies in reusable implementation, packaging,
documentation, and engineering quality rather than only in benchmark numbers.

Thank you for your consideration.

Sincerely,

[AUTHOR_NAME_BLOCK]
