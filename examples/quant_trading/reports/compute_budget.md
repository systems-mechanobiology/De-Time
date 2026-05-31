# Compute Budget: Quant Trading Columns 01-06

| Stage | Task | Datasets | Models/baselines | Runs | CPU cores | RAM | GPU | Storage | Estimated wall time | Recommended hardware | Script |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|---|
| smoke | all implemented tutorial smoke checks | archived GOOG sample + bundled real FX panel | trend, mean-reversion, breakout, pairs and rotation smoke variants | 1 | 2-8 | 8-16 GB | none | <1 GB | 5-30 min | local MacBook / Mac mini / i7 | `make smoke` |
| smoke_03_04 | residual mean-reversion and breakout columns | 1 historical GOOG OHLCV file | RSI/Bollinger/APO + residual rewrites; Donchian/Turtle + breakout rewrites | 1 | 2-8 | 8-16 GB | none | <1 GB | 1-10 min | local MacBook / Mac mini / i7 | `make smoke-03-04` |
| smoke_05_06 | pair spread and rotation columns | bundled real FX panel | pair z-score/residual spread strategies + rotation baselines/De-Time score | 1 | 2-8 | 8-16 GB | none | <1 GB | 5-30 min | local MacBook / Mac mini / i7 | `make smoke-05-06` |
| tutorial_01_06 | run all implemented tutorials on bundled real samples | archived GOOG + bundled FX | all classical and De-Time tutorial variants | 1 | 4-16 | 16-32 GB | none | <5 GB | 30-120 min | local i7 or BlueBEAR CPU | `make quant-columns-01-06` |
| live_pilot | yfinance live OHLCV for ETFs/equities | 10-50 symbols | all implemented columns with real volume where available | 1-3 | 8-32 | 32-64 GB | none | 5-20 GB | 1-6 h | local i7 / BlueBEAR CPU | `make quant-columns-05-06-live` plus earlier live targets |
| full_cpu | multi-asset, multi-window, multi-cost robustness sweep | 50+ symbols / licensed data preferred | all classical + De-Time variants, multiple decomposition methods | many | 32-128 | 64-256 GB | none | 20-200 GB | hours-days | BlueBEAR CPU array | future `scripts/slurm_cpu` jobs |
| full_gpu | later neural or automatic-discovery extensions | optional | neural baselines or agentic strategy search | TBD | 8-32 per GPU | 64+ GB | A100 / high-VRAM workstation | TBD | TBD | GPU cluster when needed | future GPU configs |

Columns 01-06 are CPU-oriented. GPU resources are not required unless future work adds neural baselines, large batched inference, or automatic discovery loops.
