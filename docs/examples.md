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

## Running them

From the package directory:

```bash
PYTHONPATH=src python3 examples/univariate_quickstart.py
PYTHONPATH=src python3 examples/multivariate_mssa.py
PYTHONPATH=src python3 examples/method_survey.py
```
