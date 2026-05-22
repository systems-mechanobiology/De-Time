# Hot Trend Lab Notebooks

These notebooks are the executable companion for `docs/tutorials/hot-trend-lab.md`.

They use real public data fetched at runtime. They do not generate synthetic fallback time series. If a source is unavailable, the notebook raises `HotTrendDataError` or the relevant vendor error.

Install optional dependencies:

```bash
python -m pip install -e .[dev,docs,notebook]
python -m pip install -r examples/hot_trends/requirements.txt
```

Open the notebooks:

```bash
jupyter lab examples/notebooks/hot_trends
```

Recommended first run:

1. `00_hot_trend_lab_overview.ipynb`
2. `01_arxiv_category_pulse.ipynb`
3. `02_arxiv_agent_research_pulse.ipynb`
