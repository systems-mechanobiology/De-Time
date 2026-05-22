# Hot Trend Lab Utilities

This directory contains the real public-data loaders, De-Time decomposition helpers, source registry, and editorial guardrails used by the Hot Trend Lab notebooks.

Install the optional runtime dependencies before running the notebooks:

```powershell
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/hot_trends/requirements.txt
```

The notebooks do not create synthetic fallback series. If arXiv, Hugging Face, GitHub, Wikimedia, DeFiLlama, CoinGecko, or market-data endpoints cannot be reached or validated, the notebook should stop with an explicit data error.
