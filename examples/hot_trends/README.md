# Hot Trend Lab Utilities

This directory contains the public-data loaders, DeTime decomposition helpers,
source registry, and publication phrasing tables used by the Hot Trend Lab
notebooks.

Install the optional runtime dependencies before running the notebooks:

```powershell
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/hot_trends/requirements.txt
```

The notebooks fetch public data from arXiv, Hugging Face, GitHub, Wikimedia,
DeFiLlama, CoinGecko, and market-data endpoints, then record source coverage
and measurement limits.
