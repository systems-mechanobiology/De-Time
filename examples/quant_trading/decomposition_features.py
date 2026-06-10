from __future__ import annotations

"""Decomposition-first feature factory for price and volume series.

The functions in this module are the core of the revised quant tutorial column.
They make the hidden structure behind classic indicators explicit:

- price trend estimates direction and persistence;
- price cycle estimates timing and oscillatory context;
- price residual estimates deviation from the current structure;
- volume trend/residual estimates participation and abnormal activity;
- reconstruction error and component stability estimate feature reliability.

All walk-forward routines only emit the final row of each training window, then
forward-fill to the next recomputation date.  That convention keeps the feature
factory usable in tutorials without turning full-sample decomposition into a
look-ahead shortcut.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from detime import DecompositionConfig, decompose


class DeTimeFeatureError(RuntimeError):
    """Raised when DeTime feature extraction cannot complete."""


@dataclass(frozen=True)
class PeriodEstimate:
    period: int
    score: float
    source: str
    candidates: tuple[int, ...]


def rolling_zscore(x: pd.Series | pd.DataFrame, window: int = 63) -> pd.Series | pd.DataFrame:
    """Rolling z-score with stable small-denominator handling."""

    window = int(window)
    mu = x.rolling(window, min_periods=max(5, window // 4)).mean()
    sd = x.rolling(window, min_periods=max(5, window // 4)).std(ddof=0)
    return (x - mu) / (sd + 1e-12)


def _clean_series(series: pd.Series) -> pd.Series:
    s = pd.Series(series).astype(float).sort_index()
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    if s.empty:
        raise DeTimeFeatureError("Cannot decompose an empty series.")
    return s


def _safe_log_transform(series: pd.Series, *, use_log: bool) -> pd.Series:
    s = _clean_series(series)
    if use_log:
        if (s <= 0).any():
            raise DeTimeFeatureError("Log decomposition requires strictly positive values.")
        return np.log(s)
    return s.copy()


def _periodogram_score(values: np.ndarray, period: int) -> float:
    y = np.asarray(values, dtype=float)
    y = y[np.isfinite(y)]
    if len(y) < max(20, period * 2):
        return float("nan")
    y = y - np.nanmean(y)
    if np.nanstd(y) < 1e-12:
        return 0.0
    freqs = np.fft.rfftfreq(len(y), d=1.0)
    power = np.abs(np.fft.rfft(y)) ** 2
    target = 1.0 / float(period)
    idx = int(np.argmin(np.abs(freqs - target)))
    lo = max(1, idx - 1)
    hi = min(len(power), idx + 2)
    return float(np.nanmean(power[lo:hi]) / (np.nanmean(power[1:]) + 1e-12))


def _acf_score(values: np.ndarray, period: int) -> float:
    y = np.asarray(values, dtype=float)
    y = y[np.isfinite(y)]
    if len(y) <= period + 5:
        return float("nan")
    y = y - np.nanmean(y)
    den = float(np.dot(y, y)) + 1e-12
    return float(np.dot(y[:-period], y[period:]) / den)


def estimate_dominant_period(
    series: pd.Series,
    *,
    candidates: Sequence[int] = (21, 42, 63, 126, 252),
    use_log: bool = True,
    detrend_window: int = 126,
) -> PeriodEstimate:
    """Estimate a dominant trading-cycle period from a short candidate set.

    This is deliberately conservative.  The tutorial avoids a wide optimizer over
    period values; it chooses from interpretable market horizons and records the
    selected value in the notebook/audit artifacts.
    """

    y = _safe_log_transform(series, use_log=use_log)
    candidates = tuple(int(c) for c in candidates if int(c) > 2)
    if not candidates:
        raise ValueError("period candidates must not be empty")
    detrended = y - y.rolling(int(detrend_window), min_periods=max(20, int(detrend_window) // 3)).mean()
    detrended = detrended.dropna()
    if detrended.empty:
        detrended = y - y.mean()

    records: list[tuple[int, float]] = []
    for p in candidates:
        acf = _acf_score(detrended.to_numpy(), p)
        spec = _periodogram_score(detrended.to_numpy(), p)
        score = np.nanmean([acf, spec])
        records.append((p, float(score) if np.isfinite(score) else -np.inf))
    best_period, best_score = max(records, key=lambda item: item[1])
    return PeriodEstimate(period=int(best_period), score=float(best_score), source="acf_periodogram_candidates", candidates=candidates)


def default_decomposition_params(method: str, period: int) -> dict[str, Any]:
    """Default DeTime parameters used by the quant tutorial examples."""

    method = method.upper()
    period = int(period)
    if method in {"STL", "ROBUST_STL", "STD", "STDR"}:
        return {"period": period}
    if method == "MSTL":
        return {"periods": [period, max(period * 2, period + 2)]}
    if method == "SSA":
        return {"window": max(period * 2, 20), "rank": 6, "primary_period": period}
    if method == "WAVELET":
        return {"wavelet": "db4", "level": 3}
    if method in {"EMD", "CEEMDAN"}:
        return {"primary_period": period}
    if method == "VMD":
        return {"K": 4, "alpha": 2000.0, "primary_period": period}
    if method in {"MA", "MA_BASELINE", "MOVING_AVERAGE"}:
        return {"trend_window": max(period, 5), "season_period": period}
    return {"period": period}


def _component_features(frame: pd.DataFrame, *, period: int, z_window: int) -> pd.DataFrame:
    out = frame.copy()
    out["trend_slope"] = out["trend"].diff(5) / 5.0
    out["trend_acceleration"] = out["trend_slope"].diff(5) / 5.0
    transformed_ret = out["transformed"].diff()
    local_vol = transformed_ret.rolling(max(10, int(z_window)), min_periods=max(5, int(z_window) // 4)).std(ddof=0)
    out["trend_strength"] = out["trend_slope"] / (local_vol + 1e-12)
    out["trend_gap"] = out["transformed"] - out["trend"]

    out["cycle_z"] = rolling_zscore(out["cycle"], z_window)
    out["cycle_slope"] = out["cycle"].diff(3) / 3.0
    amp = out["cycle"].rolling(max(int(period), 10), min_periods=max(5, int(period) // 3)).quantile(0.90) - out["cycle"].rolling(
        max(int(period), 10), min_periods=max(5, int(period) // 3)
    ).quantile(0.10)
    out["cycle_amplitude"] = (amp / 2.0).abs()
    out["cycle_position"] = (out["cycle"] / (out["cycle_amplitude"] + 1e-12)).clip(-3.0, 3.0)
    out["cycle_turn_up"] = (out["cycle_slope"] > 0).astype(float)

    out["residual_z"] = rolling_zscore(out["residual"], z_window)
    out["residual_abs_z"] = out["residual_z"].abs()
    out["residual_vol"] = out["residual"].rolling(max(10, int(z_window)), min_periods=max(5, int(z_window) // 4)).std(ddof=0)
    out["reconstruction_error"] = (out["transformed"] - out["reconstructed"]).abs()
    out["component_stability"] = 1.0 / (1.0 + out["reconstruction_error"] + out["residual_vol"].fillna(0.0))
    return out


def decompose_one_series(
    series: pd.Series,
    *,
    method: str = "STL",
    period: int | str = 63,
    period_candidates: Sequence[int] = (21, 42, 63, 126, 252),
    params: Mapping[str, Any] | None = None,
    backend: str = "auto",
    use_log: bool = True,
    z_window: int = 63,
    value_name: str = "value",
) -> pd.DataFrame:
    """Decompose one series and return trend/cycle/residual features."""

    raw = _clean_series(series)
    transformed = _safe_log_transform(raw, use_log=use_log)
    if isinstance(period, str):
        if period.lower() != "auto":
            raise ValueError("period must be an integer or 'auto'")
        p_est = estimate_dominant_period(raw, candidates=period_candidates, use_log=use_log)
        chosen_period = p_est.period
    else:
        p_est = None
        chosen_period = int(period)

    cfg = DecompositionConfig(
        method=method.upper(),
        params=dict(params) if params is not None else default_decomposition_params(method, chosen_period),
        backend=backend,  # type: ignore[arg-type]
    )
    result = decompose(transformed.to_numpy(dtype=float), cfg)
    trend = pd.Series(np.asarray(result.trend, dtype=float).reshape(-1), index=raw.index, name="trend")
    cycle = pd.Series(np.asarray(result.season, dtype=float).reshape(-1), index=raw.index, name="cycle")
    residual = pd.Series(np.asarray(result.residual, dtype=float).reshape(-1), index=raw.index, name="residual")
    reconstructed = trend + cycle + residual
    frame = pd.DataFrame(
        {
            value_name: raw,
            "transformed": transformed,
            "trend": trend,
            "cycle": cycle,
            "residual": residual,
            "reconstructed": reconstructed,
        },
        index=raw.index,
    )
    frame = _component_features(frame, period=chosen_period, z_window=z_window)
    meta = dict(result.meta)
    meta.update({"method": method.upper(), "period": chosen_period, "period_estimate": None if p_est is None else p_est.__dict__})
    frame.attrs["detime_meta"] = meta
    frame.attrs["method"] = method.upper()
    frame.attrs["period"] = chosen_period
    return frame


FEATURE_COLUMNS = [
    "trend",
    "cycle",
    "residual",
    "trend_slope",
    "trend_acceleration",
    "trend_strength",
    "trend_gap",
    "cycle_z",
    "cycle_slope",
    "cycle_amplitude",
    "cycle_position",
    "cycle_turn_up",
    "residual_z",
    "residual_abs_z",
    "residual_vol",
    "reconstruction_error",
    "component_stability",
]


def _last_feature_row(frame: pd.DataFrame) -> dict[str, float]:
    last = frame[[c for c in FEATURE_COLUMNS if c in frame.columns]].iloc[-1]
    return {str(k): float(v) for k, v in last.items() if np.isfinite(float(v))}


def walkforward_decompose(
    panel: pd.DataFrame,
    *,
    method: str = "STL",
    period: int | str = 63,
    period_candidates: Sequence[int] = (21, 42, 63, 126, 252),
    params: Mapping[str, Any] | None = None,
    backend: str = "auto",
    train_window: int = 252,
    step: int = 21,
    min_window: int | None = None,
    use_log: bool = True,
    z_window: int = 63,
    value_name: str = "value",
) -> dict[str, pd.DataFrame]:
    """Walk-forward decomposition features for a panel of price or volume series."""

    if panel.empty:
        raise DeTimeFeatureError("input panel is empty")
    clean = panel.sort_index().replace([np.inf, -np.inf], np.nan).ffill().bfill()
    train_window = int(train_window)
    step = int(step)
    if train_window < 40:
        raise ValueError("train_window should be at least 40 observations")
    min_window = int(min_window or max(40, train_window // 2))
    panels = {name: pd.DataFrame(index=clean.index, columns=clean.columns, dtype=float) for name in FEATURE_COLUMNS}
    period_panel = pd.DataFrame(index=clean.index, columns=clean.columns, dtype=float)
    start_end = max(train_window, min_window)
    for end in range(start_end, len(clean) + 1, step):
        window = clean.iloc[max(0, end - train_window) : end]
        stamp = clean.index[end - 1]
        for col in clean.columns:
            s = window[col].dropna()
            if len(s) < min_window:
                continue
            try:
                frame = decompose_one_series(
                    s,
                    method=method,
                    period=period,
                    period_candidates=period_candidates,
                    params=params,
                    backend=backend,
                    use_log=use_log,
                    z_window=z_window,
                    value_name=value_name,
                )
            except Exception:
                # Fail closed at the cell/notebook level by leaving NaNs; the audit
                # scripts expose incomplete feature coverage.  We do not synthesize
                # replacement prices or features.
                continue
            row = _last_feature_row(frame)
            for name, value in row.items():
                if name in panels:
                    panels[name].loc[stamp, col] = value
            period_panel.loc[stamp, col] = int(frame.attrs.get("period", np.nan))
    panels["selected_period"] = period_panel
    return {name: p.ffill() for name, p in panels.items()}


def prefix_feature_dict(features: dict[str, pd.DataFrame], prefix: str) -> dict[str, pd.DataFrame]:
    """Add a prefix to feature names while preserving frame values."""

    return {f"{prefix}{name}": frame.copy() for name, frame in features.items()}


def combine_price_volume_features(
    price_features: dict[str, pd.DataFrame],
    volume_features: dict[str, pd.DataFrame] | None = None,
) -> dict[str, pd.DataFrame]:
    """Merge price features and optional volume features.

    Price feature names are left unprefixed for backward compatibility; volume
    features receive the ``volume_`` prefix.
    """

    combined = {k: v.copy() for k, v in price_features.items()}
    if volume_features is not None:
        combined.update(prefix_feature_dict(volume_features, "volume_"))
        if "volume_trend_slope" in combined and "volume_residual_z" in combined:
            combined["volume_participation"] = combined["volume_trend_slope"].rank(axis=1, pct=True) + combined[
                "volume_residual_z"
            ].clip(lower=0.0).rank(axis=1, pct=True)
            combined["volume_shock"] = combined["volume_residual_z"].abs()
    return combined


def walkforward_price_volume_features(
    prices: pd.DataFrame,
    volumes: pd.DataFrame | None = None,
    *,
    method: str = "STL",
    period: int | str = 63,
    period_candidates: Sequence[int] = (21, 42, 63, 126, 252),
    backend: str = "auto",
    train_window: int = 252,
    step: int = 21,
    z_window: int = 63,
) -> dict[str, pd.DataFrame]:
    """Build price and volume decomposition features with matching dates/assets."""

    price_features = walkforward_decompose(
        prices,
        method=method,
        period=period,
        period_candidates=period_candidates,
        backend=backend,
        train_window=train_window,
        step=step,
        use_log=True,
        z_window=z_window,
        value_name="price",
    )
    volume_features = None
    if volumes is not None:
        aligned_volume = volumes.reindex(index=prices.index, columns=prices.columns).replace([np.inf, -np.inf], np.nan).ffill().bfill()
        # log1p volume outside the decomposition transform keeps zero-volume days valid.
        volume_features = walkforward_decompose(
            np.log1p(aligned_volume),
            method=method,
            period=period,
            period_candidates=period_candidates,
            backend=backend,
            train_window=train_window,
            step=step,
            use_log=False,
            z_window=z_window,
            value_name="log1p_volume",
        )
    return combine_price_volume_features(price_features, volume_features)


def build_feature_table(prices: pd.DataFrame, features: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create a feature x ticker MultiIndex table."""

    clean = prices.sort_index().ffill().bfill()
    aligned = {name: frame.reindex(index=clean.index, columns=clean.columns) for name, frame in features.items()}
    aligned["return_1d"] = clean.pct_change().reindex_like(clean)
    aligned["realized_vol_20"] = aligned["return_1d"].rolling(20, min_periods=10).std(ddof=0) * np.sqrt(252)
    if "trend_slope" in aligned:
        aligned["trend_strength_price_vol_adj"] = aligned["trend_slope"] / (aligned["realized_vol_20"] / np.sqrt(252) + 1e-12)
    return pd.concat(aligned, axis=1).sort_index(axis=1)


def feature_coverage_report(features: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Report non-null coverage by feature and asset."""

    rows: list[dict[str, object]] = []
    for name, frame in features.items():
        for col in frame.columns:
            s = frame[col]
            rows.append(
                {
                    "feature": name,
                    "asset": col,
                    "observations": int(s.shape[0]),
                    "non_null": int(s.notna().sum()),
                    "coverage": float(s.notna().mean()),
                    "first_valid": s.first_valid_index(),
                    "last_valid": s.last_valid_index(),
                }
            )
    return pd.DataFrame(rows)
