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

- `visual_leaderboard_walkthrough.py`
  - runs a small synthetic scenario sweep with real decomposition methods
  - produces leaderboard-style heatmaps and a scenario summary CSV

## Visual walkthrough previews

Univariate walkthrough:

[Open the visual univariate tutorial](tutorials/visual-univariate.md)

![Univariate walkthrough preview](assets/generated/tutorials/visual-univariate/ssa_components.png)

Method comparison walkthrough:

[Open the visual method-comparison tutorial](tutorials/visual-comparison.md)

![Method comparison preview](assets/generated/tutorials/visual-comparison/method_grid.png)

Multivariate walkthrough:

[Open the visual multivariate tutorial](tutorials/visual-multivariate.md)

![Multivariate walkthrough preview](assets/generated/tutorials/visual-multivariate/mssa_multivariate.png)

Benchmark heatmap walkthrough:

[Open the visual benchmark tutorial](tutorials/visual-benchmark.md)

![Benchmark heatmap preview](assets/generated/tutorials/visual-benchmark/figures/heatmap_T_r2.png)

## Running them

From the package directory:

```bash
PYTHONPATH=src python3 examples/univariate_quickstart.py
PYTHONPATH=src python3 examples/multivariate_mssa.py
PYTHONPATH=src python3 examples/method_survey.py
PYTHONPATH=src python3 examples/visual_univariate_walkthrough.py
PYTHONPATH=src python3 examples/visual_method_comparison.py
PYTHONPATH=src python3 examples/visual_multivariate_walkthrough.py
PYTHONPATH=src python3 examples/visual_leaderboard_walkthrough.py
```
