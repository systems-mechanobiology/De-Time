from __future__ import annotations

"""Compatibility facade for the quant-trading feature factory.

The revised first two columns use ``decomposition_features.py`` as the main
implementation. This module keeps the old import path alive for existing
notebooks and adds small wrappers for OHLCV input and legacy helper names.
"""

from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from . import decomposition_features as _df
from .decomposition_features import (  # noqa: F401
    DeTimeFeatureError,
    PeriodEstimate,
    build_feature_table,
    combine_price_volume_features,
    default_decomposition_params,
    feature_coverage_report,
    prefix_feature_dict,
    rolling_zscore,
    walkforward_decompose,
    walkforward_price_volume_features,
)


def estimate_dominant_period(
    series: pd.Series,
    *,
    candidates: Sequence[int] = (21, 42, 63, 126, 252),
    transform: str = "log",
    use_log: bool | None = None,
    detrend_window: int = 126,
) -> int:
    """Return the selected period as an integer for notebook ergonomics."""

    if use_log is None:
        use_log = transform.lower() == "log"
    return int(_df.estimate_dominant_period(series, candidates=candidates, use_log=bool(use_log), detrend_window=detrend_window).period)


def period_score_table(
    series: pd.Series,
    *,
    candidates: Sequence[int] = (21, 42, 63, 126, 252),
    transform: str = "log",
) -> pd.DataFrame:
    """Score a small period candidate set for audit tables."""

    rows = []
    for p in candidates:
        try:
            est = _df.estimate_dominant_period(series, candidates=(int(p),), use_log=(transform.lower() == "log"))
            score = est.score
        except Exception:
            score = np.nan
        rows.append({"period": int(p), "score": float(score) if np.isfinite(score) else np.nan})
    out = pd.DataFrame(rows)
    if not out.empty:
        out["selected"] = out["score"] == out["score"].max()
    return out


def select_period(series: pd.Series, *, candidates: Sequence[int] = (21, 42, 63, 126), transform: str = "log") -> int:
    return estimate_dominant_period(series, candidates=candidates, transform=transform)


def decompose_one_series(
    series: pd.Series,
    *,
    method: str = "STL",
    period: int | str = 63,
    period_candidates: Sequence[int] = (21, 42, 63, 126, 252),
    transform: str = "log",
    use_log: bool | None = None,
    z_window: int = 63,
    value_name: str = "value",
    **kwargs,
) -> pd.DataFrame:
    """Decompose one series with a ``transform`` argument kept for notebooks."""

    s = pd.Series(series).astype(float)
    if transform.lower() == "log1p":
        s = np.log1p(s.clip(lower=0))
        actual_use_log = False
    elif use_log is not None:
        actual_use_log = bool(use_log)
    else:
        actual_use_log = transform.lower() == "log"
    frame = _df.decompose_one_series(
        s,
        method=method,
        period=period,
        period_candidates=period_candidates,
        use_log=actual_use_log,
        z_window=z_window,
        value_name=value_name,
        **kwargs,
    )
    if "cycle" in frame and "season" not in frame:
        frame["season"] = frame["cycle"]
    return frame


def walkforward_decompose_ohlcv(
    ohlcv: Mapping[str, pd.DataFrame] | pd.DataFrame,
    *,
    method: str = "STL",
    period: int | str = 63,
    period_candidates: Sequence[int] = (21, 42, 63, 126, 252),
    backend: str = "auto",
    train_window: int = 252,
    step: int = 21,
    z_window: int = 63,
) -> dict[str, pd.DataFrame]:
    """Build walk-forward price+volume features from OHLCV input."""

    if isinstance(ohlcv, Mapping):
        if "Close" not in ohlcv:
            raise DeTimeFeatureError("OHLCV field-panel dictionary must contain a Close panel.")
        prices = ohlcv["Close"].sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
        volumes = ohlcv.get("Volume")
        if volumes is not None:
            volumes = volumes.reindex(index=prices.index, columns=prices.columns).replace([np.inf, -np.inf], np.nan).ffill().bfill()
    else:
        if "Close" not in ohlcv.columns:
            raise DeTimeFeatureError("OHLCV table must contain a Close column.")
        asset = str(ohlcv.attrs.get("symbol", "asset"))
        prices = ohlcv[["Close"]].rename(columns={"Close": asset})
        volumes = ohlcv[["Volume"]].rename(columns={"Volume": asset}) if "Volume" in ohlcv.columns else None

    features = walkforward_price_volume_features(
        prices,
        volumes,
        method=method,
        period=period,
        period_candidates=period_candidates,
        backend=backend,
        train_window=train_window,
        step=step,
        z_window=z_window,
    )
    # Legacy notebooks used ``season_*`` names; the revised factory uses ``cycle_*``.
    if "cycle" in features and "season" not in features:
        features["season"] = features["cycle"]
    if "cycle_slope" in features and "season_slope" not in features:
        features["season_slope"] = features["cycle_slope"]
    if "cycle_z" in features and "season_z" not in features:
        features["season_z"] = features["cycle_z"]
    return features


walkforward_decompose_price_volume = walkforward_decompose_ohlcv


def decompose_ohlcv(
    ohlcv: pd.DataFrame,
    *,
    method: str = "STL",
    period: int | str = 63,
    z_window: int = 63,
) -> pd.DataFrame:
    """Single-window close+volume decomposition, returned as one table."""

    features = walkforward_decompose_ohlcv(
        ohlcv,
        method=method,
        period=period,
        train_window=max(40, min(len(ohlcv), 252)),
        step=max(1, len(ohlcv)),
        z_window=z_window,
    )
    prices = ohlcv[["Close"]]
    aligned = {name: frame.reindex(index=prices.index).ffill() for name, frame in features.items()}
    return pd.concat({name: frame.iloc[:, 0] for name, frame in aligned.items()}, axis=1)


def latest_feature_snapshot(features: Mapping[str, pd.DataFrame], *, tail: int = 1) -> pd.DataFrame:
    """Return a tidy snapshot from the latest feature rows."""

    rows: list[dict[str, object]] = []
    for name, frame in features.items():
        recent = frame.tail(int(tail))
        for dt, row in recent.iterrows():
            for asset, value in row.items():
                rows.append({"date": dt, "asset": asset, "feature": name, "value": value})
    return pd.DataFrame(rows)


feature_snapshot = latest_feature_snapshot


def feature_signal_map() -> pd.DataFrame:
    """Document how decomposition features feed strategy logic."""

    return pd.DataFrame(
        [
            {"feature": "trend_slope", "role": "trend direction", "used_by": "trend, dual-MA, MACD, residual reversion filter, breakout filter"},
            {"feature": "trend_strength", "role": "trend reliability", "used_by": "trend following and breakout confirmation"},
            {"feature": "cycle_slope", "role": "entry timing", "used_by": "cycle confirmation, residual mean reversion, breakout entries"},
            {"feature": "cycle_position", "role": "cycle overextension", "used_by": "cycle-adjusted residual bands"},
            {"feature": "residual_z", "role": "pullback / overextension", "used_by": "pullback, RSI/Bollinger rewrite, residual bands and risk filters"},
            {"feature": "residual_abs_z", "role": "stress and overextension", "used_by": "breakout overextension cap and decomposition risk mask"},
            {"feature": "volume_trend_slope", "role": "participation", "used_by": "volume confirmation for trend and breakout"},
            {"feature": "volume_residual_z", "role": "abnormal volume", "used_by": "breakout confirmation and weak-volume residual-reversion filter"},
        ]
    )


def build_strategy_feature_panel(prices: pd.DataFrame, features: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    return build_feature_table(prices, dict(features))


__all__ = [name for name in globals() if not name.startswith("_")]
