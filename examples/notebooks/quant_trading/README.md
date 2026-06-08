# Decomposition-first quant trading notebooks

Active tutorial sequence:

| Notebook | Status | Role |
|---|---|---|
| `00_decomposition_first_quant_trading_roadmap.ipynb` | implemented | Reading order and six-tutorial roadmap. |
| `01_market_data_and_decomposition_feature_factory.ipynb` | implemented | OHLCV data audit, period estimate, walk-forward price/volume decomposition. |
| `02_decomposition_aware_moving_average_macd.ipynb` | implemented | Classical MA/MACD baselines and De-Time trend/cycle/residual/volume rewrites. |
| `03_residual_mean_reversion_rsi_bollinger.ipynb` | implemented | Price z-score, RSI, Bollinger and APO baselines rewritten as residual mean-reversion with cycle timing and volume filters. |
| `04_turtle_donchian_breakout_volume_confirmation.ipynb` | implemented | Donchian/Turtle breakout rewritten with trend, cycle, residual-overextension and volume confirmation. |
| `05_pairs_spread_decomposition_stat_arb.ipynb` | implemented | Pair spread z-score baselines rewritten as residual spread trading with trend-drift and optional volume/news filters. |
| `06_cross_sectional_rotation_portfolio.ipynb` | implemented | Cross-sectional momentum and allocation baselines rewritten as De-Time factor scores and portfolios. |
| `07_native_ssa_high_return_low_drawdown_tutorial.ipynb` | implemented | Native SSA dual-trend mean-reversion replay for selected high-return FX and crypto strategies under a 20% drawdown constraint. |

Legacy indicator-first or earlier draft notebooks are preserved in `_legacy/` for reference only.

Run the implemented tutorial batch from the repository root:

```bash
make quant-columns-01-06
```

For the current batch only:

```bash
make smoke-05-06
make quant-columns-05-06
```

### Strategy expansion notebooks

```text
03_detime_method_specific_strategy_variants.ipynb
04_detime_component_pair_trading_cointegration.ipynb
```

These notebooks are the recommended next reading after the two strategy-lab notebooks. They show that different decomposition front-ends and horizons create different strategies, and they extend pair trading with component similarity, residual gaps, and cointegration diagnostics.
