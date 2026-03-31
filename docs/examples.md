# Examples

The package ships a small set of runnable examples under
[`examples/`](https://github.com/systems-mechanobiology/De-Time/tree/main/examples).

## Included scripts

- `univariate_quickstart.py`
  - demonstrates `STD` and `SSA`
  - shows metadata inspection and reconstruction checks

- `multivariate_mssa.py`
  - demonstrates `MSSA` on a synthetic two-channel series
  - contrasts it with channelwise `STD`

- `method_survey.py`
  - exercises a small, safe subset of methods with one uniform reporting format
  - useful as a lightweight smoke demonstration

- `profile_and_cli.py`
  - materializes tracked example CSV inputs for CLI demos
  - prints ready-to-run `detime run` and `detime profile` commands

- `visual_univariate_walkthrough.py`
  - produces component and residual plots for one `SSA` decomposition
  - best first script for visual inspection

- `visual_method_comparison.py`
  - compares `STD`, `STDR`, `SSA`, and `STL` on one synthetic series
  - produces a method grid plus trend and seasonal overlays

- `visual_multivariate_walkthrough.py`
  - compares `MSSA` against channelwise `STD`
  - produces multichannel figures and a single-channel trend overlay

## Running them

From the package directory:

```bash
PYTHONPATH=src python3 examples/univariate_quickstart.py
PYTHONPATH=src python3 examples/multivariate_mssa.py
PYTHONPATH=src python3 examples/method_survey.py
PYTHONPATH=src python3 examples/visual_univariate_walkthrough.py
PYTHONPATH=src python3 examples/visual_method_comparison.py
PYTHONPATH=src python3 examples/visual_multivariate_walkthrough.py
```
