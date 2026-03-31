# De-Time (`de-time`; preferred import `detime`, legacy import `tsdecomp`): A Unified Software Library for Time-Series Decomposition

## Draft manuscript

### Authors

`[Author list and affiliations to fill in]`

### Abstract

Time-series decomposition is widely used in forecasting, signal analysis, and
scientific data analysis, yet software support is fragmented across classical
seasonal-trend methods, empirical mode methods, multi-scale transforms, and
benchmark-oriented research code. We present De-Time, an open-source Python
software package for time-series decomposition across multiple method families.
De-Time is the software brand; in distribution terms we refer to the package as
`de-time`, with preferred import name `detime` and legacy import `tsdecomp`
maintained for compatibility during transition. The package exposes a compact
public API, a command-line interface for batch execution and profiling,
multivariate decomposition support under the same result model, and selective
native C++ acceleration for higher-cost methods. In contrast to an earlier
benchmark-oriented research artifact, De-Time is packaged as a standalone
library with explicit build metadata, tests, documentation, examples,
continuous integration, and source-distribution hygiene suitable for software
review. The software contribution of De-Time is not a new decomposition
algorithm; rather, it is a reusable research library that consolidates
heterogeneous decomposition workflows into one distributable and extensible
software package.

### 1. Introduction

Time-series decomposition is often used to separate long-term trend, seasonal
structure, and residual variation before forecasting, anomaly detection,
scientific interpretation, or downstream machine learning. In practice,
researchers and practitioners face an awkward software landscape. Classical
methods such as STL and MSTL are available in one ecosystem, empirical
decomposition methods such as EMD and CEEMDAN in another, variational or
wavelet methods in still others, and many benchmark-specific implementations
remain buried inside paper artifact repositories. As a result, comparing
methods, switching between implementations, or integrating decomposition into
larger evaluation pipelines often requires method-specific code and inconsistent
data handling.

De-Time addresses this software gap by providing a unified decomposition
workflow for multiple method families in one package. The package was
originally extracted from a broader benchmark repository, but has been
restructured into a standalone software library with its own package metadata,
public API, documentation, tests, examples, and release workflows. The primary
goal is to make decomposition methods easy to call, compare, and extend without
requiring users to adopt the original benchmark infrastructure.

The software contribution of De-Time has four parts. First, it provides a
single high-level API centered on `DecompositionConfig`, `DecompResult`, and
`decompose(series, config)`. Second, it adds multivariate decomposition support
without splitting the public interface into a second result type. Third, it
supports optional native C++ acceleration for selected core methods while
preserving a simple installation path based on prebuilt wheels. Fourth, it
packages this functionality as standalone research software with tests,
documentation, examples, and release workflows suitable for independent reuse.

### 2. Related software and scope

The software ecosystem around decomposition is broad but fragmented. Packages
such as `statsmodels` provide classical seasonal-trend decomposition methods
including STL and MSTL, `PyEMD` focuses on empirical mode decomposition,
`PyWavelets` focuses on wavelet transforms, and `PySDKit` offers selected
modal and multivariate methods. These are valuable libraries and De-Time
reuses upstream method implementations where that is the right engineering
choice. The gap addressed here is not another implementation of a single method
family, but software support for a common decomposition workflow.

| Package | Primary scope | Limitation for cross-family workflows | De-Time delta |
|---|---|---|---|
| `statsmodels` | Classical decomposition such as `STL` and `MSTL` | Strong within-family support, but no common decomposition surface spanning empirical, modal, and multivariate methods | Wraps classical methods into the same API, CLI, and result model as other families |
| `PyEMD` | `EMD`, `EEMD`, `CEEMDAN` family | Narrow family focus and no shared trend/season/residual interface with non-EMD methods | Exposes EMD-family methods alongside classical and subspace methods under one interface |
| `PyWavelets` | Wavelet transforms | Transform-oriented API rather than decomposition workflow API | Makes wavelet-based paths available within the same decomposition result model |
| `PySDKit` | Selected modal and multivariate methods | Not designed as a compact workflow layer across heterogeneous decomposition packages | Supports optional multivariate backends while keeping one top-level library API |
| De-Time | Unified decomposition workflows | Broad scope requires explicit maturity boundaries and selective native work rather than full reimplementation | Adds common API, CLI, serialization, profiling, multivariate support, and native kernels for selected methods |

Accordingly, De-Time should be read as workflow software rather than as a
claim that every included method is deeper or faster than the most specialized
single-family package.

### 3. Software overview

De-Time is a Python package for univariate and multivariate decomposition of
time-series data. The package includes a public Python API, a CLI, method
registration, runtime backend selection, result serialization, and profiling
support. The top-level software story is intentionally compact. Users select a
method name and pass method-specific parameters through a common configuration
object, then receive a unified result object containing `trend`, `season`,
`residual`, optional intermediate components, and metadata.

We use "De-Time" as the software name throughout this manuscript. For package
distribution we refer to the branded distribution name `de-time`; the preferred
import name is `detime`, while `tsdecomp` is retained as a legacy import for
backward compatibility with earlier users and artifact code.

The currently supported software surface covers several classes of methods.
Classical seasonal-trend methods include `STL`, `MSTL`, and `ROBUST_STL`.
Matrix-factorization and subspace methods include `SSA` and multivariate
`MSSA`. Blockwise seasonal-trend-dispersion methods are exposed through `STD`
and `STDR`. Empirical and modal methods include `EMD`, `CEEMDAN`, `VMD`,
`WAVELET`, `MVMD`, and `MEMD`. The package also includes a small number of
benchmark-derived or wrapper-oriented methods such as `DR_TS_REG`, `DR_TS_AE`,
`SL_LIB`, and `GABOR_CLUSTER`. We do not claim that all methods have identical
maturity or implementation depth. Instead, the package documents a stable core
set while remaining honest about optional or wrapper-based paths.

The strongest current software path is built around `STD`, `STDR`, `SSA`,
`MSSA`, and `DR_TS_REG`. These methods best illustrate the package's intended
identity: a reusable library with one interface, method-level runtime metadata,
multivariate support where appropriate, and improved engineering quality
relative to the original benchmark artifact.

### 4. Implementation and design

The design of De-Time emphasizes interface stability rather than forcing all
methods into a single internal algorithmic style. Each method is registered in
a central method registry and classified by input mode. Univariate methods
accept one-dimensional inputs, multivariate methods accept arrays of shape
`(T, C)`, and channelwise methods accept multivariate inputs but decompose each
channel independently. This allows a single `decompose(...)` entry point to
handle univariate and multivariate workflows without introducing separate
high-level APIs.

Runtime behavior is mediated through a backend abstraction with modes such as
`auto`, `native`, and `python`. This makes it possible to expose native C++
acceleration without changing the user-facing method signatures. In the current
package, native implementations are available for `SSA`, `STD`, `STDR`, and
`DR_TS_REG`, while other methods continue to use Python or upstream scientific
Python backends. This design keeps the package easy to install for users who
only need the Python interface, while enabling faster execution on supported
platforms through prebuilt wheels.

Multivariate support is handled through the same result model rather than a
specialized parallel hierarchy. For example, `MSSA`, `MVMD`, and `MEMD` return
trend, seasonal, and residual outputs with shape `(T, C)`, and their
additional components can be stored as higher-dimensional arrays in the common
result container. The CLI and output serialization logic were updated
accordingly so that multivariate runs can be profiled and saved without a
separate command structure.

The package also includes a CLI for single-run decomposition, batch execution,
and runtime profiling. This is important in practice because many decomposition
libraries provide only function-level access, leaving users to build their own
wrappers for file I/O, benchmarking, and result inspection. De-Time treats
these operational tasks as part of the software contribution rather than as
unpublished utility scripts.

### 5. Package quality, reproducibility, and distribution

Beyond the method wrappers themselves, a central contribution of De-Time is
the conversion of a research artifact into reviewable software. The package now
contains explicit package metadata, an open-source license, contributor-facing
documentation, example scripts, tutorials, a documentation tree, continuous
integration, and build rules for source and wheel distributions. These changes
matter because MLOSS submissions are judged as software, not only as code made
available alongside a paper.

The package provides multiple entry points for new users. A README gives a
concise overview and installation path. A documentation tree includes install
guidance, quickstart material, API overview pages, tutorials for univariate and
multivariate workflows, and runnable examples. A small set of tracked example
CSV inputs and scripts makes the CLI demonstrations directly executable. The
distribution also includes JMLR-facing notes that explain how the present
software differs from the earlier benchmark-oriented repository structure.

From a software-engineering standpoint, the package includes package-level
tests and CI workflows that run those tests on multiple operating systems and
Python versions. Coverage reporting and source-distribution hygiene were added
so that the released archive contains the expected software materials and
excludes cache artifacts. Native build support is handled through CMake and
`pybind11`, with wheel-oriented release engineering intended to preserve a
simple installation story for users who should not need a local compiler.

### 6. Relationship to the earlier benchmark artifact

De-Time did not appear as a standalone library at the outset. Its origin was
an earlier benchmark-oriented repository used for method comparison, experiment
execution, and paper reproduction. That artifact contained valuable code, but
the software boundary was not clean: reusable decomposition logic, benchmark
orchestration, experiment outputs, and paper-facing material were mixed in one
research repository.

The present package differs from that earlier artifact in several ways. First,
the decomposition logic now lives inside a dedicated package directory with
clear package metadata and a standalone install and build path. Second, the
public API has been narrowed to a compact software surface. Third, selected
methods were given native acceleration behind one consistent backend interface.
Fourth, multivariate support was integrated into the same public result model.
Fifth, the package now includes the documentation, examples, CI, contributor
guides, and distribution rules expected of independent software.

This distinction is important for software review. The benchmark paper is about
task definition, synthetic evaluation, metrics, and empirical findings. The
present software paper is about package design, public interfaces,
distribution, documentation, testing, and engineering quality. The software
submission therefore avoids presenting benchmark leaderboards or large
scientific result tables as its main contribution.

### 7. Limitations and scope

De-Time should be understood as a research software library, not as a claim
that every exposed decomposition method has identical maturity or that the
package reimplements every algorithm from scratch. Some methods are implemented
directly in the package, some rely on upstream scientific Python libraries, and
some remain benchmark-derived wrappers. The package documents this heterogeneity
rather than hiding it.

Similarly, native acceleration is currently selective rather than universal.
The package focuses native effort where it is most useful today instead of
forcing all methods through an unnecessary low-level rewrite. This is a
software-engineering tradeoff: preserving a stable interface and good packaging
for a broad method set is more valuable than claiming maximal optimization for
every method.

Finally, the MLOSS contribution here is software-centric. We do not claim that
the package itself resolves all scientific questions about which decomposition
method is best in every setting. Those are empirical questions for separate
evaluation. The role of De-Time is to make such evaluation and practical use
easier, more reproducible, and less fragmented.

### 8. Conclusion

De-Time is an open-source time-series decomposition library that unifies
multiple decomposition families behind one Python API and one CLI, adds
multivariate support under the same software model, and introduces native C++
acceleration for selected core methods while preserving straightforward package
installation. Its main contribution to the MLOSS track is not a new
decomposition theorem or a single new algorithm. Rather, it is the software
engineering required to convert a benchmark-oriented research codebase into a
standalone, documented, tested, distributable package for broader reuse.

We expect De-Time to be most useful to researchers who need a common
software surface for decomposition experiments, comparative studies, and
pipeline integration, especially when those workflows mix classical, empirical,
and multivariate methods. The package remains honest about method maturity, but
it now provides a substantially clearer software story than the original
artifact form.

## References

- Cleveland, R. B., Cleveland, W. S., McRae, J. E., and Terpenning, I. STL: A
  Seasonal-Trend Decomposition Procedure Based on Loess.
- Dokumentov, A., and Hyndman, R. J. MSTL: A Seasonal-Trend Decomposition
  Algorithm for Time Series with Multiple Seasonal Patterns.
- Golyandina, N., Korobeynikov, A., and Zhigljavsky, A. Singular Spectrum
  Analysis with R.
- Huang, N. E., Shen, Z., Long, S. R., et al. The Empirical Mode Decomposition
  and the Hilbert Spectrum for Nonlinear and Non-Stationary Time Series
  Analysis.
- Dragomiretskiy, K., and Zosso, D. Variational Mode Decomposition.
- Dudek, G. Seasonal-Trend Decomposition Based on Blockwise Seasonal
  Representation.
- Relevant software context from `statsmodels`, `PyEMD`, `PyWavelets`, and
  `PySDKit`.
- `Time-Series Decomposition as a standalone Task: A Mechanism-Identifiable Benchmark`.
- Final submission version should cite the De-Time software repository, release
  metadata, and import/distribution transition note once those identifiers are
  frozen.
