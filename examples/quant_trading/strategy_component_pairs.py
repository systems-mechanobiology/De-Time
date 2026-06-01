from __future__ import annotations

"""Component-level pair trading and cointegration diagnostics.

The classical pair-trading idea is: two assets share a long-run relationship, so
we trade deviations from that relationship.  A decomposition-first pair strategy
makes the relationship explicit:

- trend similarity: both assets move through comparable long-horizon direction;
- cycle similarity: both assets share comparable oscillatory timing;
- residual gap: the temporary, tradable deviation between the two assets;
- cointegration diagnostics: statistical checks that a linear combination is
  stationary enough to justify spread trading.

This module does not copy private notebook code.  It implements the same trading
logic from scratch using De-Time features and a transparent next-bar backtester.
"""

from dataclasses import dataclass, asdict
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .decomposition_features import walkforward_price_volume_features, rolling_zscore
from .strategy_lab import DetailedBacktestResult, backtest_target_weights_next_bar, stats_table
from .strategy_pairs import Pair, classic_pair_zscore_weights, rolling_pair_correlation, rolling_hedge_ratio


@dataclass(frozen=True)
class ComponentPairConfig:
    """Controls for component-level pair strategies."""

    method: str = "STL"
    period: int | str = 42
    train_window: int = 180
    step: int = 21
    z_window: int = 63
    hedge_window: int = 120
    similarity_window: int = 120
    entry_z: float = 1.50
    exit_z: float = 0.25
    min_trend_corr: float = 0.50
    min_cycle_corr: float = 0.25
    max_fair_spread_trend_abs: float = 0.0025
    max_cointegration_pvalue: float = 0.10
    require_cointegration: bool = False
    allow_short: bool = True
    max_gross: float = 1.0

    @property
    def name(self) -> str:
        return f"{self.method.upper()}_p{self.period}_tw{self.train_window}"

    def to_record(self) -> dict[str, object]:
        out = asdict(self)
        out["name"] = self.name
        return out


@dataclass(frozen=True)
class CointegrationResult:
    """Small serializable cointegration result container."""

    test: str
    statistic: float
    pvalue: float
    critical_1pct: float | None = None
    critical_5pct: float | None = None
    critical_10pct: float | None = None
    valid: bool = True
    reason: str = ""

    def to_record(self, prefix: str) -> dict[str, object]:
        return {f"{prefix}_{k}": v for k, v in asdict(self).items()}


def _clean_positive(prices: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    clean = prices.loc[:, list(columns)].sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill().dropna(how="any")
    clean = clean[(clean > 0).all(axis=1)]
    if clean.empty:
        raise ValueError("positive price panel is empty after cleaning")
    return clean


def _feature(features: Mapping[str, pd.DataFrame], name: str, index: pd.Index, columns: Sequence[str], *, fill: float = 0.0) -> pd.DataFrame:
    frame = features.get(name)
    if frame is None:
        return pd.DataFrame(float(fill), index=index, columns=list(columns))
    return frame.reindex(index=index, columns=list(columns)).replace([np.inf, -np.inf], np.nan).ffill().fillna(float(fill))


def _safe_corr(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    return x.rolling(int(window), min_periods=max(20, int(window) // 3)).corr(y).replace([np.inf, -np.inf], np.nan).ffill().fillna(0.0)


def _safe_engle_granger(y0: pd.Series, y1: pd.Series) -> CointegrationResult:
    data = pd.concat([y0, y1], axis=1).dropna()
    if len(data) < 40:
        return CointegrationResult("engle_granger", np.nan, np.nan, valid=False, reason="not enough observations")
    try:
        from statsmodels.tsa.stattools import coint  # type: ignore

        stat, pvalue, crit = coint(data.iloc[:, 0].astype(float), data.iloc[:, 1].astype(float))
        return CointegrationResult(
            "engle_granger",
            float(stat),
            float(pvalue),
            float(crit[0]) if len(crit) > 0 else None,
            float(crit[1]) if len(crit) > 1 else None,
            float(crit[2]) if len(crit) > 2 else None,
            valid=True,
        )
    except Exception as exc:
        return CointegrationResult("engle_granger", np.nan, np.nan, valid=False, reason=repr(exc))


def _safe_adf(x: pd.Series) -> CointegrationResult:
    data = pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) < 40 or float(data.std(ddof=0)) < 1e-12:
        return CointegrationResult("adf", np.nan, np.nan, valid=False, reason="not enough variation or observations")
    try:
        from statsmodels.tsa.stattools import adfuller  # type: ignore

        stat, pvalue, _, _, crit, _ = adfuller(data.astype(float), autolag="AIC")
        return CointegrationResult(
            "adf",
            float(stat),
            float(pvalue),
            float(crit.get("1%", np.nan)),
            float(crit.get("5%", np.nan)),
            float(crit.get("10%", np.nan)),
            valid=True,
        )
    except Exception as exc:
        return CointegrationResult("adf", np.nan, np.nan, valid=False, reason=repr(exc))


def _pair_weights_from_state(state: pd.Series, beta: pd.Series, pair: Pair, *, max_gross: float = 1.0) -> pd.DataFrame:
    left, right = pair
    idx = state.index
    beta_s = beta.reindex(idx).replace([np.inf, -np.inf], np.nan).ffill().fillna(1.0).clip(lower=0.05, upper=10.0)
    weights = pd.DataFrame(0.0, index=idx, columns=[left, right])
    weights[left] = state.astype(float)
    weights[right] = -beta_s.astype(float) * state.astype(float)
    gross = weights.abs().sum(axis=1).replace(0.0, np.nan)
    return weights.div(gross, axis=0).fillna(0.0) * float(max_gross)


def build_component_pair_features(
    prices: pd.DataFrame,
    *,
    pairs: Sequence[Pair],
    volumes: pd.DataFrame | None = None,
    config: ComponentPairConfig | None = None,
) -> dict[str, pd.DataFrame]:
    """Build asset-level De-Time features for all assets used by pairs."""

    cfg = config or ComponentPairConfig()
    assets = sorted({asset for pair in pairs for asset in pair})
    clean = _clean_positive(prices, assets)
    vols = volumes.reindex(index=clean.index, columns=clean.columns).ffill().bfill() if volumes is not None else None
    return walkforward_price_volume_features(
        clean,
        vols,
        method=cfg.method.upper(),
        period=cfg.period,
        train_window=cfg.train_window,
        step=cfg.step,
        z_window=cfg.z_window,
    )


def component_pair_diagnostics(
    prices: pd.DataFrame,
    pair: Pair,
    features: Mapping[str, pd.DataFrame],
    *,
    config: ComponentPairConfig | None = None,
) -> pd.DataFrame:
    """Diagnose trend/cycle similarity and cointegration for one pair."""

    cfg = config or ComponentPairConfig()
    clean = _clean_positive(prices, pair)
    idx = clean.index
    left, right = pair
    trend = _feature(features, "trend", idx, pair, fill=np.nan)
    cycle = _feature(features, "cycle", idx, pair, fill=0.0)
    residual = _feature(features, "residual", idx, pair, fill=0.0)
    residual_z = _feature(features, "residual_z", idx, pair, fill=0.0)
    logp = np.log(clean)
    beta = rolling_hedge_ratio(clean, pair, lookback=cfg.hedge_window).reindex(idx).ffill().fillna(1.0)

    fair_left = trend[left] + cycle[left]
    fair_right = trend[right] + cycle[right]
    raw_spread = logp[left] - beta * logp[right]
    fair_spread = fair_left - beta * fair_right
    residual_gap = residual[left] - beta * residual[right]
    residual_z_gap = residual_z[left] - residual_z[right]

    trend_corr = _safe_corr(trend[left], trend[right], cfg.similarity_window)
    cycle_corr = _safe_corr(cycle[left], cycle[right], cfg.similarity_window)
    residual_corr = _safe_corr(residual[left], residual[right], cfg.similarity_window)
    return_corr = rolling_pair_correlation(clean, pair, window=cfg.similarity_window).reindex(idx).ffill().fillna(0.0)

    raw_coint = _safe_engle_granger(logp[left], logp[right])
    fair_coint = _safe_engle_granger(fair_left, fair_right)
    raw_spread_adf = _safe_adf(raw_spread)
    fair_spread_adf = _safe_adf(fair_spread)
    residual_gap_adf = _safe_adf(residual_gap)

    last = idx[-1]
    row = {
        "pair": f"{left}/{right}",
        "method_variant": cfg.name,
        "date": last,
        "latest_beta": float(beta.loc[last]),
        "latest_return_corr": float(return_corr.loc[last]),
        "latest_trend_corr": float(trend_corr.loc[last]),
        "latest_cycle_corr": float(cycle_corr.loc[last]),
        "latest_residual_corr": float(residual_corr.loc[last]),
        "latest_raw_spread": float(raw_spread.loc[last]),
        "latest_fair_spread": float(fair_spread.loc[last]),
        "latest_residual_gap": float(residual_gap.loc[last]),
        "latest_residual_z_gap": float(residual_z_gap.loc[last]),
        "trend_similarity_pass": bool(trend_corr.loc[last] >= cfg.min_trend_corr),
        "cycle_similarity_pass": bool(cycle_corr.loc[last] >= cfg.min_cycle_corr),
    }
    row.update(raw_coint.to_record("raw_price_coint"))
    row.update(fair_coint.to_record("fair_value_coint"))
    row.update(raw_spread_adf.to_record("raw_spread_adf"))
    row.update(fair_spread_adf.to_record("fair_spread_adf"))
    row.update(residual_gap_adf.to_record("residual_gap_adf"))
    return pd.DataFrame([row])


def component_residual_gap_pair_weights(
    prices: pd.DataFrame,
    pair: Pair,
    features: Mapping[str, pd.DataFrame],
    *,
    config: ComponentPairConfig | None = None,
) -> pd.DataFrame:
    """Trade the residual gap when trend and cycle components are similar.

    If residual_z(left) - residual_z(right) is high, left is temporarily rich
    relative to right: short left, long right.  If the gap is low, long left and
    short right.  This is the decomposition-first analogue of a pair z-score.
    """

    cfg = config or ComponentPairConfig()
    clean = _clean_positive(prices, pair)
    idx = clean.index
    left, right = pair
    trend = _feature(features, "trend", idx, pair, fill=np.nan)
    cycle = _feature(features, "cycle", idx, pair, fill=0.0)
    residual_z = _feature(features, "residual_z", idx, pair, fill=0.0)
    beta = rolling_hedge_ratio(clean, pair, lookback=cfg.hedge_window).reindex(idx).ffill().fillna(1.0)

    trend_corr = _safe_corr(trend[left], trend[right], cfg.similarity_window)
    cycle_corr = _safe_corr(cycle[left], cycle[right], cfg.similarity_window)
    residual_gap_z = rolling_zscore(residual_z[left] - residual_z[right], window=cfg.z_window).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    diagnostics = component_pair_diagnostics(clean, pair, features, config=cfg)
    raw_coint_p = float(diagnostics["raw_price_coint_pvalue"].iloc[0]) if "raw_price_coint_pvalue" in diagnostics else np.nan
    fair_coint_p = float(diagnostics["fair_value_coint_pvalue"].iloc[0]) if "fair_value_coint_pvalue" in diagnostics else np.nan
    cointegration_ok_scalar = True
    if cfg.require_cointegration:
        cointegration_ok_scalar = bool(np.nanmin([raw_coint_p, fair_coint_p]) <= cfg.max_cointegration_pvalue)

    similarity_ok = (trend_corr >= cfg.min_trend_corr) & (cycle_corr >= cfg.min_cycle_corr) & cointegration_ok_scalar
    raw_state = pd.Series(np.nan, index=idx, dtype=float)
    raw_state[(residual_gap_z < -abs(cfg.entry_z)) & similarity_ok] = 1.0
    raw_state[(residual_gap_z > abs(cfg.entry_z)) & similarity_ok] = -1.0
    raw_state[(residual_gap_z.abs() < abs(cfg.exit_z)) | (~similarity_ok)] = 0.0
    state = raw_state.ffill().fillna(0.0)
    if not cfg.allow_short:
        state = state.clip(lower=0.0)
    return _pair_weights_from_state(state, beta, pair, max_gross=cfg.max_gross)


def component_fair_spread_pair_weights(
    prices: pd.DataFrame,
    pair: Pair,
    features: Mapping[str, pd.DataFrame],
    *,
    config: ComponentPairConfig | None = None,
) -> pd.DataFrame:
    """Trade raw-price spread around the decomposed trend+cycle relationship."""

    cfg = config or ComponentPairConfig()
    clean = _clean_positive(prices, pair)
    idx = clean.index
    left, right = pair
    trend = _feature(features, "trend", idx, pair, fill=np.nan)
    cycle = _feature(features, "cycle", idx, pair, fill=0.0)
    logp = np.log(clean)
    beta = rolling_hedge_ratio(clean, pair, lookback=cfg.hedge_window).reindex(idx).ffill().fillna(1.0)
    raw_spread = logp[left] - beta * logp[right]
    fair_spread = (trend[left] + cycle[left]) - beta * (trend[right] + cycle[right])
    tradable_deviation = rolling_zscore(raw_spread - fair_spread, window=cfg.z_window).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    fair_spread_trend = fair_spread.rolling(cfg.similarity_window, min_periods=max(20, cfg.similarity_window // 3)).mean().diff(5).abs().fillna(0.0)
    relationship_ok = fair_spread_trend <= float(cfg.max_fair_spread_trend_abs)

    raw_state = pd.Series(np.nan, index=idx, dtype=float)
    raw_state[(tradable_deviation < -abs(cfg.entry_z)) & relationship_ok] = 1.0
    raw_state[(tradable_deviation > abs(cfg.entry_z)) & relationship_ok] = -1.0
    raw_state[(tradable_deviation.abs() < abs(cfg.exit_z)) | (~relationship_ok)] = 0.0
    state = raw_state.ffill().fillna(0.0)
    if not cfg.allow_short:
        state = state.clip(lower=0.0)
    return _pair_weights_from_state(state, beta, pair, max_gross=cfg.max_gross)


def component_cointegration_filtered_pair_weights(
    prices: pd.DataFrame,
    pair: Pair,
    features: Mapping[str, pd.DataFrame],
    *,
    config: ComponentPairConfig | None = None,
) -> pd.DataFrame:
    """Pair strategy that turns on only when cointegration diagnostics pass."""

    cfg = config or ComponentPairConfig(require_cointegration=True)
    diag = component_pair_diagnostics(prices, pair, features, config=cfg)
    pvals = [
        float(diag.get("raw_price_coint_pvalue", pd.Series([np.nan])).iloc[0]),
        float(diag.get("fair_value_coint_pvalue", pd.Series([np.nan])).iloc[0]),
        float(diag.get("raw_spread_adf_pvalue", pd.Series([np.nan])).iloc[0]),
        float(diag.get("fair_spread_adf_pvalue", pd.Series([np.nan])).iloc[0]),
    ]
    coint_ok = bool(np.nanmin(pvals) <= cfg.max_cointegration_pvalue) if not all(np.isnan(pvals)) else False
    if not coint_ok:
        clean = _clean_positive(prices, pair)
        return pd.DataFrame(0.0, index=clean.index, columns=list(pair))
    return component_residual_gap_pair_weights(prices, pair, features, config=cfg)


def _combine_pair_weights(prices: pd.DataFrame, pairs: Sequence[Pair], builder) -> pd.DataFrame:
    all_assets = sorted({asset for pair in pairs for asset in pair})
    idx = prices.sort_index().index
    combined = pd.DataFrame(0.0, index=idx, columns=all_assets)
    active = 0
    for pair in pairs:
        try:
            w = builder(pair)
        except Exception:
            continue
        combined = combined.add(w.reindex(index=idx, columns=all_assets).ffill().fillna(0.0), fill_value=0.0)
        active += 1
    if active == 0:
        return combined.fillna(0.0)
    gross = combined.abs().sum(axis=1).replace(0.0, np.nan)
    return combined.div(gross, axis=0).fillna(0.0)


def make_component_pair_weight_grid(
    prices: pd.DataFrame,
    pairs: Sequence[Pair],
    features: Mapping[str, pd.DataFrame],
    *,
    config: ComponentPairConfig | None = None,
) -> dict[str, pd.DataFrame]:
    """Create classical and decomposition-first pair strategies."""

    cfg = config or ComponentPairConfig()
    return {
        "classic_pair_spread_zscore": _combine_pair_weights(prices, pairs, lambda pair: classic_pair_zscore_weights(prices, pair, lookback=cfg.hedge_window, entry_z=cfg.entry_z, exit_z=cfg.exit_z)),
        f"detime_{cfg.name}_component_residual_gap": _combine_pair_weights(prices, pairs, lambda pair: component_residual_gap_pair_weights(prices, pair, features, config=cfg)),
        f"detime_{cfg.name}_fair_spread_deviation": _combine_pair_weights(prices, pairs, lambda pair: component_fair_spread_pair_weights(prices, pair, features, config=cfg)),
        f"detime_{cfg.name}_cointegration_filtered_residual_gap": _combine_pair_weights(prices, pairs, lambda pair: component_cointegration_filtered_pair_weights(prices, pair, features, config=cfg)),
    }


def run_component_pair_suite(
    prices: pd.DataFrame,
    pairs: Sequence[Pair],
    *,
    volumes: pd.DataFrame | None = None,
    config: ComponentPairConfig | None = None,
    execution_prices: pd.DataFrame | None = None,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    periods_per_year: int = 252,
) -> tuple[pd.DataFrame, dict[str, DetailedBacktestResult], pd.DataFrame, pd.DataFrame]:
    """Run component-level pair strategies with detailed backtest outputs."""

    cfg = config or ComponentPairConfig()
    assets = sorted({asset for pair in pairs for asset in pair})
    clean = _clean_positive(prices, assets)
    feats = build_component_pair_features(clean, pairs=pairs, volumes=volumes, config=cfg)
    diagnostics = []
    for pair in pairs:
        try:
            diagnostics.append(component_pair_diagnostics(clean, pair, feats, config=cfg))
        except Exception as exc:
            diagnostics.append(pd.DataFrame([{"pair": f"{pair[0]}/{pair[1]}", "method_variant": cfg.name, "diagnostic_error": repr(exc)}]))
    diag_table = pd.concat(diagnostics, ignore_index=True) if diagnostics else pd.DataFrame()

    weights = make_component_pair_weight_grid(clean, pairs, feats, config=cfg)
    results: dict[str, DetailedBacktestResult] = {}
    exec_px = execution_prices.reindex(index=clean.index, columns=assets).ffill() if execution_prices is not None else None
    for name, weight in weights.items():
        results[name] = backtest_target_weights_next_bar(
            clean,
            weight.reindex(index=clean.index, columns=assets).ffill().fillna(0.0),
            execution_prices=exec_px,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            periods_per_year=periods_per_year,
            name=name,
        )
    stats = stats_table(results)
    if not stats.empty:
        stats.insert(1, "strategy_family", stats["strategy"].str.replace(f"detime_{cfg.name}_", "", regex=False).str.replace("classic_", "classic_", regex=False))
        for key, value in cfg.to_record().items():
            stats[f"config_{key}"] = value
    feature_snapshot = pd.concat({k: v.tail(5) for k, v in feats.items() if k in {"trend", "cycle", "residual_z", "trend_strength", "selected_period"}}, axis=1) if feats else pd.DataFrame()
    return stats, results, diag_table, feature_snapshot


def collect_pair_orders_and_trades(results: Mapping[str, DetailedBacktestResult]) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders = []
    trades = []
    for name, result in results.items():
        if not result.orders.empty:
            frame = result.orders.copy()
            frame.insert(0, "strategy", name)
            orders.append(frame)
        if not result.trades.empty:
            frame = result.trades.copy()
            frame.insert(0, "strategy", name)
            trades.append(frame)
    return pd.concat(orders, ignore_index=True) if orders else pd.DataFrame(), pd.concat(trades, ignore_index=True) if trades else pd.DataFrame()


__all__ = [name for name in globals() if not name.startswith("_")]
