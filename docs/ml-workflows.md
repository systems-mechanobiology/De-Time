# ML Workflows

De-Time is not a forecasting framework and it does not claim a new
decomposition algorithm. Its relevance to machine learning comes from the
workflow layer around decomposition.

## Where it fits in ML pipelines

Common machine-learning-facing uses include:

- denoising a series before feature engineering or model fitting,
- separating trend and seasonal structure before downstream regression or
  classification,
- generating components that can be summarized into tabular features,
- inspecting shared structure across channels before multivariate modeling.

The package contribution is that these steps use one configuration contract,
one result object, and one CLI/Python surface rather than a mix of notebooks,
method-specific wrappers, and one-off scripts.

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Raw series</strong>
      <span>sensor, experimental, or panel data</span>
    </div>
    <div class="pipeline-step">
      <strong>De-Time</strong>
      <span>trend / season / residual / components</span>
    </div>
    <div class="pipeline-step">
      <strong>Features</strong>
      <span>component summaries, residual diagnostics, channel structure</span>
    </div>
    <div class="pipeline-step">
      <strong>Model</strong>
      <span>regression, classification, clustering, or inspection</span>
    </div>
  </div>
</div>

## Small scikit-learn-facing example

```python
import numpy as np
from sklearn.linear_model import LinearRegression

from detime import DecompositionConfig, decompose

t = np.arange(120, dtype=float)
series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)

result = decompose(
    series,
    DecompositionConfig(
        method="SSA",
        params={"window": 24, "rank": 6, "primary_period": 12},
    ),
)

X = np.column_stack([result.trend, result.season, result.residual])
y = series

model = LinearRegression().fit(X, y)
print(model.score(X, y))
```

This example is intentionally small. The point is not that De-Time replaces
scikit-learn, but that decomposition outputs can feed a downstream estimator
through a stable package-level workflow.

## Project and review notes

Release checks, coverage boundaries, and reviewer-facing evidence live in
[Reproducibility](reproducibility.md). This page stays focused on where the
package fits in downstream ML work.
