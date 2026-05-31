from __future__ import annotations

"""Column 05: pair trading and spread decomposition.

The functions in this module deliberately keep the classical pair-trading
scaffold visible.  A baseline pair strategy trades a rolling z-score of the raw
spread.  The De-Time rewrite decomposes the spread itself:

    spread_t = trend_t + cycle_t + residual_t

The traded object is the residual.  Trend drift becomes a pair-breakdown risk,
cycle slope becomes entry timing, and volume/liquidity checks keep the example
from treating every statistical deviation as executable arbitrage.
"""

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_weights
from .decomposition_features import walkforward_decompose, rolling_zscore
from .strategy_baselines import stats_table

Pair = tuple[str, str]

DEFAULT_LIVE_PAIRS: tuple[Pair, ...] = (
    ("KO", "PEP"),
    ("XOM", "CVX"),
    ("MA", "V"),
    ("SPY", "QQQ"),
    ("GLD", "SLV"),
)

# Bundled real-data fallback pairs from the Learn Algorithmic Trading FX files.
# These are not synthetic.  They are included so the notebook and smoke tests
# can execute without network access.  FX volume from Yahoo is usually zero, so
# the offline runs are price-only; live equity/ETF runs can use volume checks.
BUNDLED_REAL_PAIRS: tuple[Pair, ...] = (
    ("AUDUSD=X", "NZDUSD=X"),
    ("EURUSD=X", "GBPUSD=X"),
    ("CADUSD=X", "CHFUSD=X"),
)


@dataclass(frozen=True)
class PairSpreadBundle:
    pair: Pair
    beta: pd.Series
    spread: pd.Series
    spread_features: dict[str, pd.DataFrame]


def _validate_pair(prices: pd.DataFrame, pair: Pair) -> tuple[str, str]:
    left, right = pair
    missing = [ticker for ticker in (left, right) if ticker not in prices.columns]
    if missing:
        raise KeyError(f"Pair {pair!r} requires missing price columns: {missing}")
    return left, right


def _clean_prices(prices: pd.DataFrame, pair: Pair | None = None) -> pd.DataFrame:
    cols = list(pair) if pair is not None else list(prices.columns)
    clean = prices.loc[:, cols].sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    clean = clean.dropna(how="any")
    if clean.empty:
        raise ValueError("price panel is empty after cleaning")
    if (clean <= 0).any().any():
        raise ValueError("pair trading examples require strictly positive prices")
    return clean


def rolling_hedge_ratio(
    prices: pd.DataFrame,
    pair: Pair,
    *,
    lookback: int = 120,
    min_periods: int | None = None,
    beta_clip: tuple[float, float] = (0.1, 5.0),
) -> pd.Series:
    """Estimate a rolling hedge ratio from return covariance.

    The tutorial uses a lightweight hedge-ratio estimate rather than a full
    cointegration engine because the point of the column is to isolate what
    decomposition changes in the spread-trading decision.
    """

    left, right = _validate_pair(prices, pair)
    clean = _clean_prices(prices, pair)
    minp = int(min_periods or max(20, int(lookback) // 2))
    returns = np.log(clean).diff()
    cov = returns[left].rolling(int(lookback), min_periods=minp).cov(returns[right])
    var = returns[right].rolling(int(lookback), min_periods=minp).var()
    beta = (cov / (var + 1e-12)).replace([np.inf, -np.inf], np.nan)
    beta = beta.clip(float(beta_clip[0]), float(beta_clip[1])).ffill().fillna(1.0)
    beta.name = "beta"
    return beta.reindex(clean.index).ffill().fillna(1.0)


def pair_spread(
    prices: pd.DataFrame,
    pair: Pair,
    *,
    beta: float | pd.Series | None = None,
    lookback: int = 120,
) -> tuple[pd.Series, pd.Series]:
    """Return log-price spread and beta series for a pair."""

    left, right = _validate_pair(prices, pair)
    clean = _clean_prices(prices, pair)
    if beta is None:
        beta_s = rolling_hedge_ratio(clean, pair, lookback=lookback)
    elif isinstance(beta, pd.Series):
        beta_s = beta.reindex(clean.index).ffill().fillna(1.0).astype(float)
    else:
        beta_s = pd.Series(float(beta), index=clean.index, name="beta")
    spread = np.log(clean[left]) - beta_s * np.log(clean[right])
    spread.name = f"{left}_minus_{right}_spread"
    return spread.replace([np.inf, -np.inf], np.nan).dropna(), beta_s.reindex(clean.index).ffill().fillna(1.0)


def build_pair_spread_bundle(
    prices: pd.DataFrame,
    pair: Pair,
    *,
    beta: float | pd.Series | None = None,
    lookback: int = 120,
    method: str = "STL",
    period: int | str = 63,
    train_window: int = 252,
    step: int = 21,
    z_window: int = 63,
) -> PairSpreadBundle:
    """Build spread, rolling beta and walk-forward De-Time spread features."""

    spread, beta_s = pair_spread(prices, pair, beta=beta, lookback=lookback)
    spread_panel = spread.to_frame("spread")
    features = walkforward_decompose(
        spread_panel,
        method=method,
        period=period,
        train_window=train_window,
        step=step,
        use_log=False,
        z_window=z_window,
        value_name="spread",
    )
    return PairSpreadBundle(pair=pair, beta=beta_s.reindex(spread.index).ffill().fillna(1.0), spread=spread, spread_features=features)


def _feature_series(features: Mapping[str, pd.DataFrame], name: str, index: pd.Index, *, fill: float = 0.0) -> pd.Series:
    frame = features.get(name)
    if frame is None or frame.empty:
        return pd.Series(float(fill), index=index)
    if "spread" in frame.columns:
        series = frame["spread"]
    else:
        series = frame.iloc[:, 0]
    return series.reindex(index).ffill().fillna(float(fill)).astype(float)


def rolling_pair_correlation(prices: pd.DataFrame, pair: Pair, *, window: int = 120) -> pd.Series:
    left, right = _validate_pair(prices, pair)
    clean = _clean_prices(prices, pair)
    returns = np.log(clean).diff()
    corr = returns[left].rolling(int(window), min_periods=max(20, int(window) // 2)).corr(returns[right])
    return corr.reindex(clean.index).ffill().fillna(0.0)


def pair_volume_liquidity_filter(
    volumes: pd.DataFrame | None,
    pair: Pair,
    index: pd.Index,
    *,
    lookback: int = 63,
    min_quantile: float = 0.10,
    max_relative_shock_gap: float = 5.0,
) -> pd.Series:
    """Return a pair-level volume/liquidity mask.

    If volumes are unavailable or all-zero, the mask is permissive.  This keeps
    bundled FX examples executable while still letting live equity/ETF examples
    use volume as an execution and idiosyncratic-news filter.
    """

    if volumes is None:
        return pd.Series(True, index=index)
    left, right = pair
    if left not in volumes.columns or right not in volumes.columns:
        return pd.Series(True, index=index)
    v = volumes[[left, right]].reindex(index).replace([np.inf, -np.inf], np.nan).ffill().fillna(0.0)
    if float(v.abs().sum().sum()) <= 0.0:
        return pd.Series(True, index=index)
    floor = v.rolling(int(lookback), min_periods=max(10, int(lookback) // 3)).quantile(float(min_quantile)).fillna(0.0)
    enough_liquidity = (v >= floor).all(axis=1)
    shock = rolling_zscore(np.log1p(v.clip(lower=0)), window=lookback).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    symmetric_enough = (shock[left] - shock[right]).abs() <= float(max_relative_shock_gap)
    return (enough_liquidity & symmetric_enough).reindex(index).fillna(True)


def _state_to_pair_weights(state: pd.Series, beta: pd.Series, pair: Pair) -> pd.DataFrame:
    idx = state.index
    left, right = pair
    beta_s = beta.reindex(idx).ffill().fillna(1.0).astype(float)
    weights = pd.DataFrame(0.0, index=idx, columns=[left, right])
    weights[left] = state.astype(float)
    weights[right] = -beta_s * state.astype(float)
    gross = weights.abs().sum(axis=1).replace(0.0, np.nan)
    return weights.div(gross, axis=0).fillna(0.0)


def classic_pair_zscore_weights(
    prices: pd.DataFrame,
    pair: Pair,
    *,
    lookback: int = 120,
    entry_z: float = 1.5,
    exit_z: float = 0.25,
    beta: float | pd.Series | None = None,
) -> pd.DataFrame:
    """Classic spread z-score pair trade without decomposition."""

    spread, beta_s = pair_spread(prices, pair, beta=beta, lookback=lookback)
    z = rolling_zscore(spread, window=lookback).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    raw_state = pd.Series(np.nan, index=spread.index, dtype=float)
    raw_state[z < -abs(float(entry_z))] = 1.0
    raw_state[z > abs(float(entry_z))] = -1.0
    raw_state[z.abs() < abs(float(exit_z))] = 0.0
    state = raw_state.ffill().fillna(0.0)
    return _state_to_pair_weights(state, beta_s, pair)


def classic_corr_filtered_pair_weights(
    prices: pd.DataFrame,
    pair: Pair,
    *,
    lookback: int = 120,
    corr_window: int = 120,
    min_corr: float = 0.25,
    entry_z: float = 1.5,
    exit_z: float = 0.25,
) -> pd.DataFrame:
    """Classic z-score pair trade with a rolling correlation gate."""

    base = classic_pair_zscore_weights(prices, pair, lookback=lookback, entry_z=entry_z, exit_z=exit_z)
    corr = rolling_pair_correlation(prices, pair, window=corr_window).reindex(base.index).ffill().fillna(0.0)
    return base.where(corr >= float(min_corr), 0.0).fillna(0.0)


def classic_ratio_zscore_weights(
    prices: pd.DataFrame,
    pair: Pair,
    *,
    lookback: int = 120,
    entry_z: float = 1.5,
    exit_z: float = 0.25,
) -> pd.DataFrame:
    """A simple ratio-z-score baseline often seen in introductory tutorials."""

    left, right = _validate_pair(prices, pair)
    clean = _clean_prices(prices, pair)
    ratio = (clean[left] / clean[right]).replace([np.inf, -np.inf], np.nan)
    z = rolling_zscore(ratio, window=lookback).fillna(0.0)
    raw_state = pd.Series(np.nan, index=ratio.index, dtype=float)
    raw_state[z < -abs(float(entry_z))] = 1.0
    raw_state[z > abs(float(entry_z))] = -1.0
    raw_state[z.abs() < abs(float(exit_z))] = 0.0
    state = raw_state.ffill().fillna(0.0)
    beta = pd.Series(1.0, index=ratio.index)
    return _state_to_pair_weights(state, beta, pair)


def detime_spread_residual_weights(
    prices: pd.DataFrame,
    pair: Pair,
    spread_features: Mapping[str, pd.DataFrame],
    *,
    beta: pd.Series | float | None = None,
    lookback: int = 120,
    volumes: pd.DataFrame | None = None,
    entry_z: float = 1.25,
    exit_z: float = 0.20,
    max_spread_trend_slope: float = 0.002,
    min_pair_corr: float = 0.20,
    require_cycle_turn: bool = True,
    panic_abs_z: float = 3.5,
) -> pd.DataFrame:
    """Trade spread residual deviations only when spread trend drift is contained."""

    spread, beta_s = pair_spread(prices, pair, beta=beta, lookback=lookback)
    idx = spread.index
    rz = _feature_series(spread_features, "residual_z", idx, fill=0.0)
    trend_slope = _feature_series(spread_features, "trend_slope", idx, fill=0.0)
    cycle_slope = _feature_series(spread_features, "cycle_slope", idx, fill=0.0)
    residual_abs_z = _feature_series(spread_features, "residual_abs_z", idx, fill=0.0)
    corr = rolling_pair_correlation(prices, pair, window=lookback).reindex(idx).ffill().fillna(0.0)
    liquidity_ok = pair_volume_liquidity_filter(volumes, pair, idx)

    drift_ok = trend_slope.abs() <= float(max_spread_trend_slope)
    pair_ok = (corr >= float(min_pair_corr)) & liquidity_ok & (residual_abs_z <= float(panic_abs_z))
    long_entry = (rz < -abs(float(entry_z))) & drift_ok & pair_ok
    short_entry = (rz > abs(float(entry_z))) & drift_ok & pair_ok
    if require_cycle_turn:
        long_entry &= cycle_slope >= 0.0
        short_entry &= cycle_slope <= 0.0
    exit_trade = (rz.abs() < abs(float(exit_z))) | (~pair_ok) | (trend_slope.abs() > float(max_spread_trend_slope) * 1.75)

    state = 0.0
    states: list[float] = []
    for dt in idx:
        if state != 0.0 and bool(exit_trade.loc[dt]):
            state = 0.0
        if state == 0.0 and bool(long_entry.loc[dt]):
            state = 1.0
        elif state == 0.0 and bool(short_entry.loc[dt]):
            state = -1.0
        states.append(state)
    return _state_to_pair_weights(pd.Series(states, index=idx), beta_s, pair)


def detime_spread_cycle_timed_weights(
    prices: pd.DataFrame,
    pair: Pair,
    spread_features: Mapping[str, pd.DataFrame],
    *,
    beta: pd.Series | float | None = None,
    lookback: int = 120,
    volumes: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """A stricter variant emphasizing cycle timing and lower residual entry."""

    return detime_spread_residual_weights(
        prices,
        pair,
        spread_features,
        beta=beta,
        lookback=lookback,
        volumes=volumes,
        entry_z=1.5,
        exit_z=0.15,
        max_spread_trend_slope=0.0015,
        min_pair_corr=0.25,
        require_cycle_turn=True,
        panic_abs_z=3.0,
    )


def detime_spread_trend_drift_blocker_weights(
    prices: pd.DataFrame,
    pair: Pair,
    spread_features: Mapping[str, pd.DataFrame],
    *,
    beta: pd.Series | float | None = None,
    lookback: int = 120,
    volumes: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Ablation that highlights the spread-trend drift filter."""

    return detime_spread_residual_weights(
        prices,
        pair,
        spread_features,
        beta=beta,
        lookback=lookback,
        volumes=volumes,
        entry_z=1.25,
        exit_z=0.20,
        max_spread_trend_slope=0.001,
        min_pair_corr=0.10,
        require_cycle_turn=False,
        panic_abs_z=3.5,
    )


def make_classic_pair_weight_grid(prices: pd.DataFrame, pair: Pair) -> dict[str, pd.DataFrame]:
    return {
        "classic_pair_spread_zscore_120": classic_pair_zscore_weights(prices, pair, lookback=120, entry_z=1.5, exit_z=0.25),
        "classic_pair_corr_filtered_zscore": classic_corr_filtered_pair_weights(prices, pair, lookback=120, min_corr=0.25, entry_z=1.5),
        "classic_pair_ratio_zscore_120": classic_ratio_zscore_weights(prices, pair, lookback=120, entry_z=1.5, exit_z=0.25),
    }


def make_detime_pair_weight_grid(
    prices: pd.DataFrame,
    pair: Pair,
    spread_features: Mapping[str, pd.DataFrame],
    *,
    beta: pd.Series | float | None = None,
    volumes: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    return {
        "detime_spread_residual_z": detime_spread_residual_weights(prices, pair, spread_features, beta=beta, volumes=volumes),
        "detime_spread_cycle_timed": detime_spread_cycle_timed_weights(prices, pair, spread_features, beta=beta, volumes=volumes),
        "detime_spread_trend_drift_blocker": detime_spread_trend_drift_blocker_weights(prices, pair, spread_features, beta=beta, volumes=volumes),
    }


def pair_diagnostic_table(
    prices: pd.DataFrame,
    pair: Pair,
    bundle: PairSpreadBundle,
    *,
    volumes: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Latest pair state for notebook display and audit CSVs."""

    idx = bundle.spread.index
    last = idx[-1]
    corr = rolling_pair_correlation(prices, pair, window=120).reindex(idx).ffill().fillna(0.0)
    liquidity = pair_volume_liquidity_filter(volumes, pair, idx)
    rows = [
        {
            "pair": f"{pair[0]}/{pair[1]}",
            "date": last,
            "spread": float(bundle.spread.loc[last]),
            "beta": float(bundle.beta.reindex(idx).ffill().loc[last]),
            "pair_corr_120": float(corr.loc[last]),
            "spread_trend_slope": float(_feature_series(bundle.spread_features, "trend_slope", idx).loc[last]),
            "spread_cycle_slope": float(_feature_series(bundle.spread_features, "cycle_slope", idx).loc[last]),
            "spread_residual_z": float(_feature_series(bundle.spread_features, "residual_z", idx).loc[last]),
            "spread_residual_abs_z": float(_feature_series(bundle.spread_features, "residual_abs_z", idx).loc[last]),
            "volume_liquidity_ok": bool(liquidity.loc[last]),
        }
    ]
    return pd.DataFrame(rows)


def run_pair_suite(
    prices: pd.DataFrame,
    pair: Pair,
    *,
    volumes: pd.DataFrame | None = None,
    method: str = "STL",
    period: int | str = 63,
    train_window: int = 252,
    step: int = 21,
    fee_bps: float = 1.0,
    slippage_bps: float = 2.0,
) -> tuple[pd.DataFrame, dict[str, BacktestResult], PairSpreadBundle]:
    """Run classical and De-Time pair strategies for one pair."""

    pair_prices = _clean_prices(prices, pair)
    bundle = build_pair_spread_bundle(pair_prices, pair, method=method, period=period, train_window=train_window, step=step)
    weights = {}
    weights.update(make_classic_pair_weight_grid(pair_prices, pair))
    weights.update(make_detime_pair_weight_grid(pair_prices, pair, bundle.spread_features, beta=bundle.beta, volumes=volumes))
    results = {name: backtest_weights(pair_prices, w, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, w in weights.items()}
    table = stats_table(results)
    table.insert(0, "pair", f"{pair[0]}/{pair[1]}")
    table.insert(1, "strategy_group", ["detime_pair" if str(idx).startswith("detime") else "classical_pair" for idx in table.index])
    return table.sort_values("sharpe", ascending=False), results, bundle


__all__ = [name for name in globals() if not name.startswith("_")]


# ---------------------------------------------------------------------------
# Multi-pair wrappers used by the Column 05 scripts and smoke tests.
# These definitions intentionally override the single-pair grid functions above
# while preserving those lower-level building blocks.
# ---------------------------------------------------------------------------


def _pair_column(pair: Pair) -> str:
    return f"{pair[0]}__{pair[1]}"


def _normalize_full_portfolio(weights: pd.DataFrame, *, gross: float = 1.0) -> pd.DataFrame:
    w = weights.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    g = w.abs().sum(axis=1).replace(0.0, np.nan)
    return w.div(g, axis=0).fillna(0.0) * float(gross)


def _expand_pair_weights(pair_weights: pd.DataFrame, all_columns: Sequence[str]) -> pd.DataFrame:
    out = pd.DataFrame(0.0, index=pair_weights.index, columns=list(all_columns))
    for col in pair_weights.columns:
        if col in out.columns:
            out[col] = pair_weights[col]
    return out


def _combine_pair_strategy(prices: pd.DataFrame, pairs: Sequence[Pair], builder) -> pd.DataFrame:
    combined = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    active = 0
    for pair in pairs:
        try:
            pair_prices = _clean_prices(prices, pair)
            w = builder(pair_prices, pair)
        except Exception:
            continue
        combined = combined.add(_expand_pair_weights(w.reindex(index=prices.index).ffill().fillna(0.0), prices.columns), fill_value=0.0)
        active += 1
    if active == 0:
        return combined.fillna(0.0)
    return _normalize_full_portfolio(combined)


def build_pair_feature_bundles(
    prices: pd.DataFrame,
    *,
    pairs: Sequence[Pair],
    volumes: pd.DataFrame | None = None,
    method: str = "STL",
    period: int | str = 63,
    hedge_lookback: int = 120,
    train_window: int = 252,
    step: int = 21,
    z_window: int = 63,
) -> dict[str, PairSpreadBundle]:
    """Build one spread-decomposition bundle per pair."""

    bundles: dict[str, PairSpreadBundle] = {}
    for pair in pairs:
        pair_prices = _clean_prices(prices, pair)
        bundle = build_pair_spread_bundle(
            pair_prices,
            pair,
            lookback=hedge_lookback,
            method=method,
            period=period,
            train_window=train_window,
            step=step,
            z_window=z_window,
        )
        bundles[_pair_column(pair)] = bundle
    return bundles


def _combine_feature_bundles(bundles: Mapping[str, PairSpreadBundle]) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame, list[Pair]]:
    feature_names: set[str] = set()
    for bundle in bundles.values():
        feature_names.update(bundle.spread_features.keys())
    index = next(iter(bundles.values())).spread.index if bundles else pd.Index([])
    spread_panel = pd.DataFrame(index=index)
    beta_panel = pd.DataFrame(index=index)
    combined_features: dict[str, pd.DataFrame] = {}
    pair_specs: list[Pair] = []
    for name, bundle in bundles.items():
        pair_specs.append(bundle.pair)
        spread_panel[name] = bundle.spread.reindex(index).ffill()
        beta_panel[name] = bundle.beta.reindex(index).ffill().fillna(1.0)
    for feature in feature_names:
        frame = pd.DataFrame(index=index)
        for name, bundle in bundles.items():
            source = bundle.spread_features.get(feature)
            if source is None or source.empty:
                frame[name] = np.nan
            elif "spread" in source.columns:
                frame[name] = source["spread"].reindex(index).ffill()
            else:
                frame[name] = source.iloc[:, 0].reindex(index).ffill()
        combined_features[feature] = frame
    return combined_features, spread_panel, beta_panel, pair_specs


def walkforward_pair_spread_features(
    prices: pd.DataFrame,
    pairs: Sequence[Pair],
    *,
    hedge_method: str = "rolling",
    hedge_window: int = 120,
    method: str = "STL",
    period: int | str = 63,
    period_candidates: Sequence[int] = (21, 42, 63, 126),
    train_window: int = 252,
    step: int = 21,
    z_window: int = 63,
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame, list[Pair]]:
    """Build decomposed spread features for multiple pairs."""

    # hedge_method is kept in the public signature for tutorial readability.
    del hedge_method, period_candidates
    bundles = build_pair_feature_bundles(
        prices,
        pairs=pairs,
        method=method,
        period=period,
        hedge_lookback=hedge_window,
        train_window=train_window,
        step=step,
        z_window=z_window,
    )
    return _combine_feature_bundles(bundles)


def _single_bundle_from_panels(
    pair: Pair,
    name: str,
    spread_features: Mapping[str, pd.DataFrame],
    spread_panel: pd.DataFrame,
    beta_panel: pd.DataFrame,
) -> PairSpreadBundle:
    index = spread_panel.index
    features: dict[str, pd.DataFrame] = {}
    for feature, frame in spread_features.items():
        if name in frame.columns:
            features[feature] = frame[[name]].rename(columns={name: "spread"})
    beta = beta_panel[name] if name in beta_panel else pd.Series(1.0, index=index)
    return PairSpreadBundle(pair=pair, beta=beta.reindex(index).ffill().fillna(1.0), spread=spread_panel[name].reindex(index).ffill(), spread_features=features)


def make_classic_pair_weight_grid(
    prices: pd.DataFrame,
    pairs: Sequence[Pair] | Pair,
    *,
    lookback: int = 120,
    allow_short: bool = True,
) -> dict[str, pd.DataFrame]:
    """Classical multi-pair baselines."""

    if pairs and isinstance(pairs[0], str):  # type: ignore[index]
        pair_list = [pairs]  # type: ignore[list-item]
    else:
        pair_list = list(pairs)  # type: ignore[arg-type]
    return {
        "classic_pair_spread_zscore_120": _combine_pair_strategy(prices, pair_list, lambda p, q: classic_pair_zscore_weights(p, q, lookback=lookback)),
        "classic_pair_corr_filtered_zscore": _combine_pair_strategy(prices, pair_list, lambda p, q: classic_corr_filtered_pair_weights(p, q, lookback=lookback, min_corr=0.25)),
        "classic_pair_ratio_zscore_120": _combine_pair_strategy(prices, pair_list, lambda p, q: classic_ratio_zscore_weights(p, q, lookback=lookback)),
    }


def make_detime_pair_weight_grid(
    prices: pd.DataFrame,
    pairs_or_bundles: Sequence[Pair] | Mapping[str, PairSpreadBundle] | Pair,
    spread_features: Mapping[str, pd.DataFrame] | None = None,
    *,
    spread_panel: pd.DataFrame | None = None,
    beta_panel: pd.DataFrame | None = None,
    beta: pd.Series | float | None = None,
    asset_features: Mapping[str, pd.DataFrame] | None = None,
    allow_short: bool = True,
    volumes: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    """De-Time pair or multi-pair spread strategies.

    Supports both the notebook-style single-pair call
    ``make_detime_pair_weight_grid(prices, pair, features, beta=...)`` and the
    script-style multi-pair call using spread and beta panels.
    """

    del asset_features, allow_short
    if isinstance(pairs_or_bundles, tuple) and len(pairs_or_bundles) == 2 and all(isinstance(x, str) for x in pairs_or_bundles):
        if spread_features is None:
            raise ValueError("spread_features are required for a single pair.")
        pair = pairs_or_bundles  # type: ignore[assignment]
        return {
            "detime_spread_residual_z": detime_spread_residual_weights(prices, pair, spread_features, beta=beta, volumes=volumes),
            "detime_spread_cycle_timed": detime_spread_cycle_timed_weights(prices, pair, spread_features, beta=beta, volumes=volumes),
            "detime_spread_trend_drift_blocker": detime_spread_trend_drift_blocker_weights(prices, pair, spread_features, beta=beta, volumes=volumes),
        }

    if isinstance(pairs_or_bundles, Mapping):
        bundles = dict(pairs_or_bundles)
    else:
        if spread_features is None or spread_panel is None or beta_panel is None:
            raise ValueError("spread_features, spread_panel and beta_panel are required when passing pair specs.")
        bundles = {}
        for pair in pairs_or_bundles:  # type: ignore[assignment]
            name = _pair_column(pair)
            bundles[name] = _single_bundle_from_panels(pair, name, spread_features, spread_panel, beta_panel)

    pair_list = [bundle.pair for bundle in bundles.values()]

    def _build_residual(pair_prices: pd.DataFrame, pair: Pair) -> pd.DataFrame:
        bundle = bundles[_pair_column(pair)]
        return detime_spread_residual_weights(pair_prices, pair, bundle.spread_features, beta=bundle.beta, volumes=volumes)

    def _build_cycle(pair_prices: pd.DataFrame, pair: Pair) -> pd.DataFrame:
        bundle = bundles[_pair_column(pair)]
        return detime_spread_cycle_timed_weights(pair_prices, pair, bundle.spread_features, beta=bundle.beta, volumes=volumes)

    def _build_drift(pair_prices: pd.DataFrame, pair: Pair) -> pd.DataFrame:
        bundle = bundles[_pair_column(pair)]
        return detime_spread_trend_drift_blocker_weights(pair_prices, pair, bundle.spread_features, beta=bundle.beta, volumes=volumes)

    return {
        "detime_spread_residual_z": _combine_pair_strategy(prices, pair_list, _build_residual),
        "detime_spread_cycle_timed": _combine_pair_strategy(prices, pair_list, _build_cycle),
        "detime_spread_trend_drift_blocker": _combine_pair_strategy(prices, pair_list, _build_drift),
    }


def run_classical_pair_baselines(
    prices: pd.DataFrame,
    pairs: Sequence[Pair],
    *,
    allow_short: bool = True,
    fee_bps: float = 1.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    del allow_short
    return {name: backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, weights in make_classic_pair_weight_grid(prices, pairs).items()}


def run_detime_pair_baselines(
    prices: pd.DataFrame,
    pairs: Sequence[Pair],
    spread_features: Mapping[str, pd.DataFrame],
    *,
    spread_panel: pd.DataFrame,
    beta_panel: pd.DataFrame,
    asset_features: Mapping[str, pd.DataFrame] | None = None,
    allow_short: bool = True,
    fee_bps: float = 1.0,
    slippage_bps: float = 2.0,
) -> dict[str, BacktestResult]:
    weights = make_detime_pair_weight_grid(
        prices,
        pairs,
        spread_features,
        spread_panel=spread_panel,
        beta_panel=beta_panel,
        asset_features=asset_features,
        allow_short=allow_short,
    )
    return {name: backtest_weights(prices, w, fee_bps=fee_bps, slippage_bps=slippage_bps) for name, w in weights.items()}


def compare_pair_suites(classical: Mapping[str, BacktestResult], detime: Mapping[str, BacktestResult]) -> pd.DataFrame:
    left = stats_table(dict(classical)).assign(strategy_group="classical_pair")
    right = stats_table(dict(detime)).assign(strategy_group="detime_pair")
    table = pd.concat([left, right], axis=0)
    order = ["strategy_group", "cagr", "sharpe", "max_drawdown", "calmar", "average_turnover", "average_gross_exposure", "total_return", "volatility", "hit_rate"]
    return table[[c for c in order if c in table.columns]].sort_values("sharpe", ascending=False)


def pair_diagnostics(
    prices: pd.DataFrame,
    pairs: Sequence[Pair],
    *,
    hedge_method: str = "rolling",
    hedge_window: int = 120,
) -> pd.DataFrame:
    del hedge_method
    rows = []
    for pair in pairs:
        pair_prices = _clean_prices(prices, pair)
        bundle = build_pair_spread_bundle(pair_prices, pair, lookback=hedge_window, method="STL", period=42, train_window=min(252, max(126, len(pair_prices) // 3)), step=max(21, len(pair_prices) // 8))
        rows.append(pair_diagnostic_table(pair_prices, pair, bundle).iloc[0].to_dict())
    return pd.DataFrame(rows)


def pair_feature_snapshot(spread_features: Mapping[str, pd.DataFrame], *, tail: int = 5) -> pd.DataFrame:
    rows = []
    for feature, frame in spread_features.items():
        for dt, row in frame.tail(int(tail)).iterrows():
            for pair, value in row.items():
                rows.append({"date": dt, "pair": pair, "feature": feature, "value": value})
    return pd.DataFrame(rows)
