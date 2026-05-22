# Hot Trend Lab Notebooks

These notebooks are the executable companion for `docs/tutorials/hot-trend-lab.md`.

They fetch public data at runtime from the source named inside each notebook and
record coverage, freshness, and measurement limits.

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
