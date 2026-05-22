from __future__ import annotations

"""De-Time component tables for real-data Hot Trend Lab notebooks."""

from typing import Any, Mapping
import numpy as np
import pandas as pd

from detime import DecompositionConfig, decompose


class HotTrendDecompositionError(RuntimeError):
    """Raised when a real series cannot be decomposed."""


def _as_numeric_series(values: pd.Series, *, transform: str = "none") -> pd.Series:
    s = pd.Series(values).astype("float64").replace([np.inf, -np.inf], np.nan).dropna()
    if s.empty:
        raise HotTrendDecompositionError("Cannot decompose an empty numeric series")
    if transform == "log1p":
        if (s < 0).any():
            raise HotTrendDecompositionError("log1p transform requires values >= 0")
        return np.log1p(s)
    if transform == "log":
        if (s <= 0).any():
            raise HotTrendDecompositionError("log transform requires values > 0")
        return np.log(s)
    if transform == "zscore":
        return (s - s.mean()) / (s.std(ddof=0) + 1e-12)
    return s


def default_params(method: str, *, period: int | None, trend_window: int | None = None) -> dict[str, Any]:
    method = method.upper()
    if method in {"STL", "ROBUST_STL", "STD", "STDR"}:
        if period is None:
            raise ValueError(f"{method} requires period")
        return {"period": int(period)}
    if method == "MA_BASELINE":
        params: dict[str, Any] = {}
        if trend_window is not None:
            params["trend_window"] = int(trend_window)
        if period is not None:
            params["season_period"] = int(period)
        return params
    if method == "SSA":
        window = max(12, int((period or 12) * 2))
        return {"window": window, "rank": 6, "primary_period": int(period or 12)}
    return {}


def decompose_table(
    frame: pd.DataFrame,
    *,
    entity_col: str,
    time_col: str,
    value_col: str,
    method: str = "MA_BASELINE",
    period: int | None = None,
    trend_window: int | None = None,
    transform: str = "log1p",
    params: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Return a long component table from real source data."""

    if frame.empty:
        raise HotTrendDecompositionError("Input frame is empty")
    outputs = []
    for entity, sub in frame.sort_values(time_col).groupby(entity_col):
        sub = sub.sort_values(time_col).reset_index(drop=True)
        y = _as_numeric_series(sub[value_col], transform=transform)
        aligned = sub.loc[y.index].reset_index(drop=True)
        cfg = DecompositionConfig(
            method=method.upper(),
            params=dict(params) if params is not None else default_params(method, period=period, trend_window=trend_window),
        )
        try:
            result = decompose(y.to_numpy(dtype=float), cfg)
        except Exception as exc:
            raise HotTrendDecompositionError(f"De-Time decomposition failed for {entity}: {exc}") from exc
        out = pd.DataFrame(
            {
                time_col: aligned[time_col].values,
                entity_col: entity,
                "observed": y.to_numpy(dtype=float),
                "trend": np.asarray(result.trend, dtype=float).reshape(-1),
                "season": np.asarray(result.season, dtype=float).reshape(-1),
                "residual": np.asarray(result.residual, dtype=float).reshape(-1),
            }
        )
        out["method"] = method.upper()
        out["period"] = period
        out["transform"] = transform
        outputs.append(out)
    if not outputs:
        raise HotTrendDecompositionError("No component tables were produced")
    return pd.concat(outputs, ignore_index=True)


def _robust_zscore(s: pd.Series) -> pd.Series:
    s = pd.Series(s, dtype="float64")
    med = s.median()
    mad = (s - med).abs().median()
    scale = 1.4826 * mad if mad and mad > 1e-12 else s.std(ddof=0)
    return (s - med) / (scale + 1e-12)


def component_summary(components: pd.DataFrame, *, entity_col: str, time_col: str = "date") -> pd.DataFrame:
    rows = []
    for entity, sub in components.groupby(entity_col):
        sub = sub.sort_values(time_col)
        observed = sub["observed"].astype(float)
        trend = sub["trend"].astype(float)
        season = sub["season"].astype(float)
        residual = sub["residual"].astype(float)
        total_var = float(np.var(observed))
        residual_z = _robust_zscore(residual)
        rows.append(
            {
                entity_col: entity,
                "observations": int(len(sub)),
                "first_timestamp": str(pd.to_datetime(sub[time_col]).min()),
                "last_timestamp": str(pd.to_datetime(sub[time_col]).max()),
                "trend_last": float(trend.iloc[-1]),
                "trend_slope_per_step": float(np.polyfit(np.arange(len(trend)), trend, 1)[0]) if len(trend) >= 2 else np.nan,
                "cycle_strength_proxy": float(1.0 - np.var(residual) / total_var) if total_var > 1e-12 else np.nan,
                "residual_std": float(residual.std(ddof=0)),
                "max_abs_residual_z": float(residual_z.abs().max()),
                "method": str(sub["method"].iloc[0]) if "method" in sub else "",
            }
        )
    return pd.DataFrame(rows)


def residual_event_table(
    components: pd.DataFrame,
    *,
    entity_col: str,
    time_col: str,
    top_n: int = 20,
) -> pd.DataFrame:
    out = components.copy()
    out["residual_z"] = out.groupby(entity_col)["residual"].transform(_robust_zscore)
    out["abs_residual_z"] = out["residual_z"].abs()
    cols = [time_col, entity_col, "observed", "trend", "season", "residual", "residual_z", "abs_residual_z", "method"]
    return out.sort_values("abs_residual_z", ascending=False).loc[:, cols].head(int(top_n)).reset_index(drop=True)


def editorial_priority(summary: pd.DataFrame, *, entity_col: str) -> pd.DataFrame:
    out = summary.copy()
    for col in ["trend_slope_per_step", "cycle_strength_proxy", "max_abs_residual_z"]:
        s = pd.Series(out[col], dtype="float64")
        out[col + "_rank_pct"] = s.rank(pct=True)
    out["editorial_priority_score"] = (
        0.45 * out["max_abs_residual_z_rank_pct"]
        + 0.35 * out["trend_slope_per_step_rank_pct"]
        + 0.20 * out["cycle_strength_proxy_rank_pct"]
    )
    return out.sort_values("editorial_priority_score", ascending=False)
