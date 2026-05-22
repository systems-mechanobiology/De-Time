from __future__ import annotations

"""Feature engineering from De-Time trend, cycle, and residual components."""

from typing import Any, Mapping

import numpy as np
import pandas as pd

from detime import DecompositionConfig, decompose


class DeTimeFeatureError(RuntimeError):
    """Raised when De-Time feature extraction cannot complete."""


def rolling_zscore(x: pd.Series | pd.DataFrame, window: int = 63) -> pd.Series | pd.DataFrame:
    """Rolling z-score with stable small-denominator handling."""

    mu = x.rolling(window, min_periods=max(5, window // 4)).mean()
    sd = x.rolling(window, min_periods=max(5, window // 4)).std(ddof=0)
    return (x - mu) / (sd + 1e-12)


def _default_params(method: str, period: int) -> dict[str, Any]:
    method = method.upper()
    if method in {"STL", "ROBUST_STL", "STD", "STDR"}:
        return {"period": int(period)}
    if method == "MSTL":
        return {"periods": [int(period), int(period * 2)]}
    if method == "SSA":
        return {"window": max(int(period * 2), 20), "rank": 6, "primary_period": int(period)}
    if method == "WAVELET":
        return {"wavelet": "db4", "level": 3}
    if method in {"EMD", "CEEMDAN"}:
        return {"primary_period": int(period)}
    if method == "VMD":
        return {"K": 4, "alpha": 2000.0, "primary_period": int(period)}
    return {"period": int(period)}


def decompose_one_series(
    price: pd.Series,
    *,
    method: str = "STL",
    period: int = 63,
    params: Mapping[str, Any] | None = None,
    backend: str = "auto",
    use_log_price: bool = True,
    z_window: int = 63,
) -> pd.DataFrame:
    """Decompose one real price series and return component-derived features.

    The input is expected to be real market data. The function does not fabricate
    missing observations; it only forward/backward fills sparse vendor gaps after
    the original download has been validated.
    """

    s = pd.Series(price).dropna().astype(float).sort_index()
    if s.empty:
        raise DeTimeFeatureError("Cannot decompose an empty price series.")
    if (s <= 0).any() and use_log_price:
        raise DeTimeFeatureError("Log-price decomposition requires strictly positive prices.")

    y = np.log(s) if use_log_price else s.copy()
    cfg = DecompositionConfig(
        method=method.upper(),
        params=dict(params) if params is not None else _default_params(method, period),
        backend=backend,  # type: ignore[arg-type]
    )
    result = decompose(y.to_numpy(dtype=float), cfg)
    trend = pd.Series(np.asarray(result.trend, dtype=float).reshape(-1), index=s.index, name="trend")
    season = pd.Series(np.asarray(result.season, dtype=float).reshape(-1), index=s.index, name="season")
    residual = pd.Series(np.asarray(result.residual, dtype=float).reshape(-1), index=s.index, name="residual")
    reconstructed = trend + season + residual

    frame = pd.DataFrame(
        {
            "price": s,
            "transformed_price": y,
            "trend": trend,
            "season": season,
            "residual": residual,
            "reconstructed": reconstructed,
        },
        index=s.index,
    )
    frame["trend_slope"] = frame["trend"].diff(5) / 5.0
    frame["trend_gap"] = frame["transformed_price"] - frame["trend"]
    frame["season_z"] = rolling_zscore(frame["season"], z_window)
    frame["season_slope"] = frame["season"].diff(3) / 3.0
    frame["residual_z"] = rolling_zscore(frame["residual"], z_window)
    frame["residual_abs_z"] = frame["residual_z"].abs()
    frame["reconstruction_error"] = (frame["transformed_price"] - frame["reconstructed"]).abs()
    frame.attrs["detime_meta"] = dict(result.meta)
    frame.attrs["method"] = method.upper()
    frame.attrs["period"] = int(period)
    return frame


def _last_feature_row(frame: pd.DataFrame) -> dict[str, float]:
    cols = [
        "trend", "season", "residual", "trend_slope", "trend_gap", "season_z", "season_slope",
        "residual_z", "residual_abs_z", "reconstruction_error",
    ]
    last = frame[cols].iloc[-1]
    return {str(k): float(v) for k, v in last.items() if np.isfinite(float(v))}


def walkforward_decompose(
    prices: pd.DataFrame,
    *,
    method: str = "STL",
    period: int = 63,
    params: Mapping[str, Any] | None = None,
    backend: str = "auto",
    train_window: int = 252,
    step: int = 21,
    min_window: int | None = None,
    use_log_price: bool = True,
    z_window: int = 63,
) -> dict[str, pd.DataFrame]:
    """Walk-forward De-Time feature factory for a price panel.

    Only the last feature row of each training window is written to the feature
    panel, then forward-filled until the next recomputation date. This avoids the
    common look-ahead error of decomposing the full sample before backtesting.
    """

    if prices.empty:
        raise DeTimeFeatureError("prices is empty")
    clean = prices.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    train_window = int(train_window)
    step = int(step)
    if train_window < 40:
        raise ValueError("train_window should be at least 40 observations.")
    min_window = int(min_window or max(40, train_window // 2))

    feature_names = [
        "trend", "season", "residual", "trend_slope", "trend_gap", "season_z", "season_slope",
        "residual_z", "residual_abs_z", "reconstruction_error",
    ]
    panels = {name: pd.DataFrame(index=clean.index, columns=clean.columns, dtype=float) for name in feature_names}

    start_end = max(train_window, min_window)
    for end in range(start_end, len(clean) + 1, step):
        window = clean.iloc[max(0, end - train_window):end]
        stamp = clean.index[end - 1]
        for col in clean.columns:
            s = window[col].dropna()
            if len(s) < min_window:
                continue
            frame = decompose_one_series(
                s,
                method=method,
                period=period,
                params=params,
                backend=backend,
                use_log_price=use_log_price,
                z_window=z_window,
            )
            row = _last_feature_row(frame)
            for name, value in row.items():
                if name in panels:
                    panels[name].loc[stamp, col] = value

    return {name: panel.ffill() for name, panel in panels.items()}


def build_feature_table(prices: pd.DataFrame, features: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create a column MultiIndex feature table: feature x ticker."""

    aligned = {name: frame.reindex_like(prices) for name, frame in features.items()}
    aligned["return_1d"] = prices.pct_change().reindex_like(prices)
    aligned["realized_vol_20"] = aligned["return_1d"].rolling(20, min_periods=10).std(ddof=0) * np.sqrt(252)
    if "trend_slope" in aligned:
        aligned["trend_strength"] = aligned["trend_slope"] / (aligned["realized_vol_20"] / np.sqrt(252) + 1e-12)
    return pd.concat(aligned, axis=1).sort_index(axis=1)
