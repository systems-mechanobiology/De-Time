# Notebook Gallery

The beginner method gallery is a committed Jupyter notebook with plotted
outputs for the retained De-Time method surface:

- [`examples/notebooks/de_time_method_gallery.ipynb`](https://github.com/systems-mechanobiology/De-Time/blob/main/examples/notebooks/de_time_method_gallery.ipynb)

The notebook uses the public API:

```python
from detime import DecompositionConfig, MethodRegistry, decompose
```

It includes one runnable section for each retained method:

`SSA`, `STD`, `STDR`, `MSSA`, `STL`, `MSTL`, `ROBUST_STL`, `EMD`, `CEEMDAN`,
`VMD`, `WAVELET`, `MA_BASELINE`, `MVMD`, `MEMD`, and `GABOR_CLUSTER`.

Methods run when the local environment has the needed dependencies. Optional
or experimental methods that need extra upstream packages or a trained model
report an explicit skipped status instead of failing the notebook.

## Run locally

Install the current repository plus notebook tooling:

```bash
python -m pip install "git+https://github.com/systems-mechanobiology/De-Time.git"
python -m pip install "de-time[notebook] @ git+https://github.com/systems-mechanobiology/De-Time.git"
```

For contributor work from a local checkout:

```bash
python -m pip install -e .[dev,docs,notebook]
jupyter lab examples/notebooks/de_time_method_gallery.ipynb
```

To regenerate the committed notebook:

```bash
python scripts/generate_notebook_gallery.py
```

Use [Config Reference](config-reference.md) when adapting the notebook examples
to real datasets and [Method Matrix](method-matrix.md) when choosing a method.
