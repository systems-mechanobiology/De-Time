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

## Why this matters for JMLR MLOSS

What De-Time contributes to machine learning software is not algorithmic
novelty. It is a reproducible software boundary for decomposition work that is
often used inside ML experiments, ablations, and preprocessing pipelines.
