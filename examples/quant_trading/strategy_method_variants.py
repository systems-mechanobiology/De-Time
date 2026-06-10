from __future__ import annotations

"""Method-specific decomposition trading variants.

This module turns the tutorial idea into executable strategy families:

different decomposition methods + different window/period choices => different
trading strategies.

A moving average strategy changes when the fast/slow windows change.  A
DeTime strategy changes when the decomposition front-end changes (STL, SSA,
STD, Wavelet, etc.) or when the decomposition horizon changes (short-cycle,
medium-cycle, long-cycle windows).  The trading rule can be identical, but the
trend, cycle, and residual fed into the rule are method-specific.  The result is
a family of comparable strategies rather than one hand-picked signal.
"""

from dataclasses import dataclass, asdict
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .classic_indicators import ema, macd
from .decomposition_features import feature_coverage_report, walkforward_price_volume_features
from .strategy_lab import (
    DetailedBacktestResult,
    HybridRegimeConfig,
    OscillationReversionConfig,
    SignalSet,
    TrendFollowingConfig,
    backtest_signal_set,
    decomposition_hybrid_regime_signals,
    decomposition_oscillation_reversion_signals,
    decomposition_trend_following_signals,
    positions_from_signals,
    stats_table,
)


@dataclass(frozen=True)
class DecompositionVariantSpec:
    """One decomposition choice interpreted as one strategy variant."""

    method: str
    period: int | str = 42
    train_window: int = 180
    step: int = 21
    z_window: int = 63
    label: str | None = None
    role: str = "medium_cycle"

    @property
    def name(self) -> str:
        base = self.label or f"{self.method.upper()}_p{self.period}_tw{self.train_window}_s{self.step}"
        return str(base).replace(" ", "_").replace("/", "_")

    def to_record(self) -> dict[str, object]:
        out = asdict(self)
        out["name"] = self.name
        return out


@dataclass(frozen=True)
class DecompositionMACDConfig:
    """Controls for MACD computed on the decomposed trend component."""

    fast: int = 12
    slow: int = 26
    signal: int = 9
    min_trend_strength: float = 0.05
    exit_trend_strength: float = -0.02
    max_cycle_position: float = 1.50
    max_residual_abs_z: float = 3.00
    allow_short: bool = False
    max_gross: float = 1.0


@dataclass(frozen=True)
class DecompositionBollingerConfig:
    """Controls for residual bands around the trend+cycle fair value."""

    entry_z: float = 2.00
    exit_z: float = 0.25
    max_abs_trend_strength: float = 0.45
    require_cycle_turn: bool = False
    allow_short: bool = True
    max_gross: float = 1.0


@dataclass(frozen=True)
class DecompositionTrendCrossoverConfig:
    """Controls for EMA crossover applied to the decomposed trend."""

    fast: int = 8
    slow: int = 34
    min_trend_strength: float = 0.05
    max_residual_abs_z: float = 3.00
    allow_short: bool = False
    max_gross: float = 1.0


def default_variant_specs(*, include_wavelet: bool = True) -> list[DecompositionVariantSpec]:
    """A compact, interpretable grid for tutorial runs.

    Short-cycle specs react quickly but may overtrade.  Long-cycle specs are
    smoother but slower.  Method choice changes the extracted component itself:
    STL is fixed-period seasonal-trend decomposition, SSA is low-rank Hankel
    subspace extraction, STD is seasonal-trend-dispersion decomposition, and
    Wavelet is multi-scale time-frequency decomposition when PyWavelets is
    installed.
    """

    specs = [
        DecompositionVariantSpec("STL", period=21, train_window=126, step=21, z_window=42, role="short_cycle"),
        DecompositionVariantSpec("STL", period=42, train_window=180, step=21, z_window=63, role="medium_cycle"),
        DecompositionVariantSpec("SSA", period=42, train_window=180, step=21, z_window=63, role="subspace_medium_cycle"),
        DecompositionVariantSpec("SSA", period=63, train_window=252, step=21, z_window=63, role="subspace_long_cycle"),
        DecompositionVariantSpec("STD", period=42, train_window=180, step=21, z_window=63, role="dispersion_medium_cycle"),
    ]
    if include_wavelet:
        specs.append(DecompositionVariantSpec("WAVELET", period=42, train_window=180, step=21, z_window=63, role="multiscale_optional"))
    return specs


def _align_feature(features: Mapping[str, pd.DataFrame], name: str, prices: pd.DataFrame, *, fill: float = 0.0) -> pd.DataFrame:
    frame = features.get(name)
    if frame is None:
        return pd.DataFrame(float(fill), index=prices.index, columns=prices.columns)
    return frame.reindex(index=prices.index, columns=prices.columns).replace([np.inf, -np.inf], np.nan).ffill().fillna(float(fill))


def _bool(x: pd.DataFrame) -> pd.DataFrame:
    return x.replace([np.inf, -np.inf], np.nan).fillna(False).astype(bool)


def _constant_size(prices: pd.DataFrame, value: float = 1.0) -> pd.DataFrame:
    return pd.DataFrame(float(value), index=prices.index, columns=prices.columns)


def decomposition_macd_trend_signals(
    prices: pd.DataFrame,
    features: Mapping[str, pd.DataFrame],
    *,
    config: DecompositionMACDConfig | None = None,
    name: str = "detime_trend_macd",
) -> SignalSet:
    """MACD strategy where MACD is computed on the decomposed trend.

    Classic MACD computes fast/slow EMAs on raw price.  This variant treats the
    decomposed trend as the smoothed object and uses cycle/residual filters to
    avoid buying at an overextended local cycle high.
    """

    cfg = config or DecompositionMACDConfig()
    px = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    trend = _align_feature(features, "trend", px, fill=np.nan)
    trend_strength = _align_feature(features, "trend_strength", px, fill=0.0)
    cycle_position = _align_feature(features, "cycle_position", px, fill=0.0)
    residual_abs_z = _align_feature(features, "residual_abs_z", px, fill=0.0)

    m = macd(trend, fast=cfg.fast, slow=cfg.slow, signal=cfg.signal)
    line = m["macd"].reindex_like(px).fillna(0.0)
    sig = m["signal"].reindex_like(px).fillna(0.0)
    hist = m["histogram"].reindex_like(px).fillna(0.0)

    long_entries = (
        (line > sig)
        & (hist > 0.0)
        & (trend_strength > float(cfg.min_trend_strength))
        & (cycle_position < float(cfg.max_cycle_position))
        & (residual_abs_z < float(cfg.max_residual_abs_z))
    )
    long_exits = (line < sig) | (trend_strength < float(cfg.exit_trend_strength)) | (residual_abs_z >= float(cfg.max_residual_abs_z))

    if cfg.allow_short:
        short_entries = (
            (line < sig)
            & (hist < 0.0)
            & (trend_strength < -float(cfg.min_trend_strength))
            & (cycle_position > -float(cfg.max_cycle_position))
            & (residual_abs_z < float(cfg.max_residual_abs_z))
        )
        short_exits = (line > sig) | (trend_strength > -float(cfg.exit_trend_strength)) | (residual_abs_z >= float(cfg.max_residual_abs_z))
    else:
        short_entries = short_exits = None

    weights = positions_from_signals(
        _bool(long_entries),
        _bool(long_exits),
        short_entries=None if short_entries is None else _bool(short_entries),
        short_exits=None if short_exits is None else _bool(short_exits),
        size=_constant_size(px),
        max_gross=cfg.max_gross,
    )
    diagnostics = {
        "trend": trend,
        "trend_macd": line,
        "trend_macd_signal": sig,
        "trend_macd_histogram": hist,
        "trend_strength": trend_strength,
        "cycle_position": cycle_position,
        "residual_abs_z": residual_abs_z,
    }
    return SignalSet(name=name, long_entries=_bool(long_entries), long_exits=_bool(long_exits), short_entries=short_entries, short_exits=short_exits, target_weights=weights, diagnostics=diagnostics)


def decomposition_trend_crossover_signals(
    prices: pd.DataFrame,
    features: Mapping[str, pd.DataFrame],
    *,
    config: DecompositionTrendCrossoverConfig | None = None,
    name: str = "detime_trend_crossover",
) -> SignalSet:
    """Dual moving-average strategy where the input is the decomposed trend."""

    cfg = config or DecompositionTrendCrossoverConfig()
    px = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    trend = _align_feature(features, "trend", px, fill=np.nan)
    trend_strength = _align_feature(features, "trend_strength", px, fill=0.0)
    residual_abs_z = _align_feature(features, "residual_abs_z", px, fill=0.0)
    fast = ema(trend, cfg.fast).reindex_like(px).ffill()
    slow = ema(trend, cfg.slow).reindex_like(px).ffill()

    long_entries = (fast > slow) & (trend_strength > float(cfg.min_trend_strength)) & (residual_abs_z < float(cfg.max_residual_abs_z))
    long_exits = (fast < slow) | (trend_strength < 0.0) | (residual_abs_z >= float(cfg.max_residual_abs_z))
    if cfg.allow_short:
        short_entries = (fast < slow) & (trend_strength < -float(cfg.min_trend_strength)) & (residual_abs_z < float(cfg.max_residual_abs_z))
        short_exits = (fast > slow) | (trend_strength > 0.0) | (residual_abs_z >= float(cfg.max_residual_abs_z))
    else:
        short_entries = short_exits = None

    weights = positions_from_signals(
        _bool(long_entries),
        _bool(long_exits),
        short_entries=None if short_entries is None else _bool(short_entries),
        short_exits=None if short_exits is None else _bool(short_exits),
        size=_constant_size(px),
        max_gross=cfg.max_gross,
    )
    diagnostics = {
        "trend": trend,
        "fast_trend_ema": fast,
        "slow_trend_ema": slow,
        "trend_strength": trend_strength,
        "residual_abs_z": residual_abs_z,
    }
    return SignalSet(name=name, long_entries=_bool(long_entries), long_exits=_bool(long_exits), short_entries=short_entries, short_exits=short_exits, target_weights=weights, diagnostics=diagnostics)


def decomposition_residual_bollinger_signals(
    prices: pd.DataFrame,
    features: Mapping[str, pd.DataFrame],
    *,
    config: DecompositionBollingerConfig | None = None,
    name: str = "detime_residual_bollinger",
) -> SignalSet:
    """Bollinger-style strategy around trend+cycle fair value.

    Classic Bollinger bands use a moving average and raw-price standard
    deviation.  This variant uses fair value = trend + cycle and residual_z as
    the band distance.  It only trades the band when the decomposed trend is not
    too strong, which keeps a falling trend from being mistaken for a cheap
    reversion entry.
    """

    cfg = config or DecompositionBollingerConfig()
    px = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    trend = _align_feature(features, "trend", px, fill=np.nan)
    cycle = _align_feature(features, "cycle", px, fill=0.0)
    residual_z = _align_feature(features, "residual_z", px, fill=0.0)
    residual_vol = _align_feature(features, "residual_vol", px, fill=0.0)
    trend_strength = _align_feature(features, "trend_strength", px, fill=0.0)
    cycle_slope = _align_feature(features, "cycle_slope", px, fill=0.0)

    weak_trend = trend_strength.abs() <= float(cfg.max_abs_trend_strength)
    long_entries = (residual_z <= -abs(float(cfg.entry_z))) & weak_trend
    short_entries = (residual_z >= abs(float(cfg.entry_z))) & weak_trend if cfg.allow_short else None
    if cfg.require_cycle_turn:
        long_entries &= cycle_slope >= 0.0
        if short_entries is not None:
            short_entries &= cycle_slope <= 0.0
    long_exits = (residual_z >= -abs(float(cfg.exit_z))) | (~weak_trend)
    short_exits = (residual_z <= abs(float(cfg.exit_z))) | (~weak_trend) if cfg.allow_short else None

    weights = positions_from_signals(
        _bool(long_entries),
        _bool(long_exits),
        short_entries=None if short_entries is None else _bool(short_entries),
        short_exits=None if short_exits is None else _bool(short_exits),
        size=_constant_size(px),
        max_gross=cfg.max_gross,
    )
    fair_log = trend + cycle
    fair_value = np.exp(fair_log).where(np.isfinite(fair_log))
    upper_band = np.exp(fair_log + abs(float(cfg.entry_z)) * residual_vol.abs()).where(np.isfinite(fair_log))
    lower_band = np.exp(fair_log - abs(float(cfg.entry_z)) * residual_vol.abs()).where(np.isfinite(fair_log))
    diagnostics = {
        "fair_value": fair_value,
        "upper_residual_band": upper_band,
        "lower_residual_band": lower_band,
        "residual_z": residual_z,
        "trend_strength": trend_strength,
        "cycle_slope": cycle_slope,
        "weak_trend_regime": weak_trend.astype(float),
    }
    return SignalSet(name=name, long_entries=_bool(long_entries), long_exits=_bool(long_exits), short_entries=short_entries, short_exits=short_exits, target_weights=weights, diagnostics=diagnostics)


def make_method_specific_signal_sets(
    prices: pd.DataFrame,
    features: Mapping[str, pd.DataFrame],
    *,
    spec: DecompositionVariantSpec,
    allow_short_trend: bool = False,
    allow_short_reversion: bool = True,
) -> list[SignalSet]:
    """Create all strategy signals from one decomposition variant."""

    prefix = f"detime_{spec.name}"
    trend_cfg = TrendFollowingConfig(allow_short=allow_short_trend)
    rev_cfg = OscillationReversionConfig(allow_short=allow_short_reversion)
    hybrid_cfg = HybridRegimeConfig(trend=trend_cfg, reversion=rev_cfg)
    return [
        decomposition_trend_following_signals(prices, features, config=trend_cfg, name=f"{prefix}_trend_following"),
        decomposition_oscillation_reversion_signals(prices, features, config=rev_cfg, name=f"{prefix}_oscillation_reversion"),
        decomposition_hybrid_regime_signals(prices, features, config=hybrid_cfg, name=f"{prefix}_hybrid_regime"),
        decomposition_residual_bollinger_signals(prices, features, config=DecompositionBollingerConfig(allow_short=allow_short_reversion), name=f"{prefix}_residual_bollinger"),
        decomposition_macd_trend_signals(prices, features, config=DecompositionMACDConfig(allow_short=allow_short_trend), name=f"{prefix}_trend_macd"),
        decomposition_trend_crossover_signals(prices, features, config=DecompositionTrendCrossoverConfig(allow_short=allow_short_trend), name=f"{prefix}_trend_crossover"),
    ]


def run_method_variant_grid(
    prices: pd.DataFrame,
    volumes: pd.DataFrame | None = None,
    *,
    specs: Sequence[DecompositionVariantSpec] | None = None,
    execution_prices: pd.DataFrame | None = None,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    periods_per_year: int = 252,
    allow_short_trend: bool = False,
    allow_short_reversion: bool = True,
) -> tuple[pd.DataFrame, dict[str, DetailedBacktestResult], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run method × parameter strategy variants with full backtest diagnostics.

    Returns
    -------
    stats_table, results, spec_table, feature_coverage, failed_methods
    """

    spec_list = list(specs or default_variant_specs())
    results: dict[str, DetailedBacktestResult] = {}
    coverage_frames: list[pd.DataFrame] = []
    failed: list[dict[str, object]] = []

    for spec in spec_list:
        try:
            features = walkforward_price_volume_features(
                prices,
                volumes,
                method=spec.method.upper(),
                period=spec.period,
                train_window=spec.train_window,
                step=spec.step,
                z_window=spec.z_window,
            )
            coverage = feature_coverage_report(features)
            coverage.insert(0, "variant", spec.name)
            coverage.insert(1, "method", spec.method.upper())
            coverage_frames.append(coverage)
            trend_cov = coverage.loc[coverage["feature"].eq("trend"), "coverage"]
            if trend_cov.empty or float(trend_cov.max()) < 0.05:
                raise RuntimeError("insufficient trend feature coverage")
            for sig in make_method_specific_signal_sets(
                prices,
                features,
                spec=spec,
                allow_short_trend=allow_short_trend,
                allow_short_reversion=allow_short_reversion,
            ):
                bt = backtest_signal_set(
                    prices,
                    sig,
                    execution_prices=execution_prices,
                    fee_bps=fee_bps,
                    slippage_bps=slippage_bps,
                    periods_per_year=periods_per_year,
                )
                results[sig.name] = bt
        except Exception as exc:
            failed.append({"variant": spec.name, "method": spec.method.upper(), "period": spec.period, "train_window": spec.train_window, "reason": repr(exc)})

    stats = stats_table(results)
    if not stats.empty:
        meta = pd.DataFrame([spec.to_record() for spec in spec_list])
        stats.insert(1, "strategy_family", stats["strategy"].str.extract(r"_(trend_following|oscillation_reversion|hybrid_regime|residual_bollinger|trend_macd|trend_crossover)$", expand=False).fillna("unknown"))
        stats.insert(2, "decomposition_variant", stats["strategy"].str.replace("^detime_", "", regex=True).str.replace(r"_(trend_following|oscillation_reversion|hybrid_regime|residual_bollinger|trend_macd|trend_crossover)$", "", regex=True))
        stats = stats.merge(meta.add_prefix("spec_"), left_on="decomposition_variant", right_on="spec_name", how="left")
    spec_table = pd.DataFrame([spec.to_record() for spec in spec_list])
    coverage_table = pd.concat(coverage_frames, ignore_index=True) if coverage_frames else pd.DataFrame()
    failed_table = pd.DataFrame(failed)
    return stats, results, spec_table, coverage_table, failed_table


def collect_orders_and_trades(results: Mapping[str, DetailedBacktestResult]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Collect detailed order and round-trip ledgers from strategy results."""

    orders = []
    trades = []
    for name, result in results.items():
        if isinstance(result.orders, pd.DataFrame) and not result.orders.empty:
            frame = result.orders.copy()
            frame.insert(0, "strategy", name)
            orders.append(frame)
        if isinstance(result.trades, pd.DataFrame) and not result.trades.empty:
            frame = result.trades.copy()
            frame.insert(0, "strategy", name)
            trades.append(frame)
    return (
        pd.concat(orders, ignore_index=True) if orders else pd.DataFrame(),
        pd.concat(trades, ignore_index=True) if trades else pd.DataFrame(),
    )


__all__ = [name for name in globals() if not name.startswith("_")]
