# Hardware Deployment Plan: Quant Trading Columns 01-04

| Stage | Mac mini 16GB | MacBook Pro 28GB | i7-14700K + RTX 3080 Ti | BlueBEAR CPU | 1×A100 / 2×A100 | Recommended placement |
|---|---|---|---|---|---|---|
| Smoke test | feasible | feasible | feasible | feasible | not needed | local |
| Pilot run | feasible for 1 ticker | feasible | feasible | feasible | not needed | local i7 or BlueBEAR CPU |
| Full benchmark after columns 05-06 | not recommended | feasible for small subset | feasible but slow for all sweeps | feasible | not needed unless neural models are added | BlueBEAR CPU |
| Paper reproduction | feasible if using frozen CSV outputs | feasible | feasible | feasible | not needed | local or CPU cluster |

Run the hardware probe before any claim about full feasibility:

```bash
python examples/quant_trading/scripts/system_probe.py
```

## Strategy-lab placement

The strategy lab is CPU-first.  It uses classical decomposition, pandas signal generation, and vectorized next-bar backtesting.  GPU is not required.

- Local Mac / laptop: feasible for bundled GOOG sample and small CSV files.
- i7 workstation: recommended for larger intraday CSVs and method comparisons.
- BlueBEAR CPU: recommended for long intraday data, many symbols, or many method/period sweeps.
- A100 / GPU cluster: not recommended unless a later tutorial adds neural models.
