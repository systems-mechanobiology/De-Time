# Quant trading reproducibility checklist

- Record the data vendor, access timestamp, adjustment policy, and calendar.
- Keep walk-forward decomposition; do not decompose the full sample before backtesting.
- Shift positions by at least one bar after signal generation.
- Report fees, slippage, borrow, financing, FX, and tax assumptions separately.
- Split tutorial demos, pilot research, and production-grade benchmarks.
- Keep missing and failed experiments visible.
- Do not present notebook examples as investment advice or production performance claims.
