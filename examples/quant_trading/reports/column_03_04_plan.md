# Column 03-04 Implementation Plan

## Column 03 — Residual mean reversion

Classical baselines:

- raw-price rolling z-score mean reversion;
- Bollinger-band mean reversion;
- RSI oversold recovery;
- Average Price Oscillator reversion.

De-Time rewrites:

- residual z-score reversion with trend, cycle and volume filters;
- RSI computed on the residual channel;
- Bollinger logic computed on residuals rather than raw prices;
- cycle-adjusted residual bands that avoid buying a residual dip at a cycle peak.

Main teaching point: the traded deviation should be `residual_z`, not raw price distance from a moving average, because residual deviation is measured after extracting the current trend and cycle.

## Column 04 — Donchian/Turtle breakout

Classical baselines:

- Donchian 20/10;
- Donchian 55/20;
- simplified long-only Turtle 55/20.

De-Time rewrites:

- prior-channel breakout must pass `trend_slope`, `trend_strength`, `cycle_slope`, `residual_abs_z`, `volume_trend_slope` and `volume_residual_z` filters;
- exits combine channel failure and decomposition-state deterioration.

Main teaching point: breakout is a price event, but the decision to trade it should also know whether trend, cycle, residual and volume components agree.

## Data and evidence policy

The notebooks and smoke tests use bundled historical GOOG OHLCV data copied from the user-provided Learn Algorithmic Trading material. Live scripts support Yahoo Finance downloads. No synthetic price series are used as evidence for the tutorial.
