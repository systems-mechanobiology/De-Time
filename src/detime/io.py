from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Sequence, Union

import numpy as np
import pandas as pd

from .core import DecompResult
from .serialization import normalize_fields, serialize_result


def _normalize_cols(cols: str | Sequence[str] | None) -> list[str] | None:
    if cols is None:
        return None
    if isinstance(cols, str):
        items = [part.strip() for part in cols.split(",")]
    else:
        items = [str(part).strip() for part in cols]
    cleaned = [item for item in items if item]
    return cleaned or None


def _load_frame(path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported file format: {path.suffix}")


def _is_multivariate_method(method: str | None) -> bool:
    if not method:
        return False
    try:
        from .registry import MethodRegistry

        return MethodRegistry.is_multivariate_method(method)
    except Exception:
        return False


def read_series(
    path: Union[str, Path],
    col: str = None,
    cols: str | Sequence[str] | None = None,
    *,
    method: str | None = None,
    return_info: bool = False,
) -> np.ndarray | tuple[np.ndarray, Dict[str, Any]]:
    """
    Read time series from CSV or Parquet.
    """
    if col and cols:
        raise ValueError("Specify either 'col' or 'cols', not both.")

    path = Path(path)
    df = _load_frame(path)

    selected_cols = _normalize_cols(cols)
    if col:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in {path}.")
        arr = df[col].to_numpy(dtype=float)
        info = {"channel_names": [col], "selected_columns": [col], "multivariate": False}
    elif selected_cols:
        missing = [name for name in selected_cols if name not in df.columns]
        if missing:
            raise ValueError(f"Columns not found in {path}: {missing}")
        arr = df[selected_cols].to_numpy(dtype=float)
        info = {
            "channel_names": selected_cols,
            "selected_columns": selected_cols,
            "multivariate": True,
        }
    else:
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        if _is_multivariate_method(method):
            if not numeric_cols:
                raise ValueError(
                    f"{method} requires numeric columns for multivariate input, but none were found in {path}."
                )
            arr = df[numeric_cols].to_numpy(dtype=float)
            info = {
                "channel_names": numeric_cols,
                "selected_columns": numeric_cols,
                "multivariate": True,
            }
        elif numeric_cols:
            arr = df[numeric_cols[0]].to_numpy(dtype=float)
            info = {
                "channel_names": [numeric_cols[0]],
                "selected_columns": [numeric_cols[0]],
                "multivariate": False,
            }
        else:
            arr = df.iloc[:, 0].to_numpy()
            info = {
                "channel_names": [str(df.columns[0])],
                "selected_columns": [str(df.columns[0])],
                "multivariate": False,
            }

    if return_info:
        return arr, info
    return arr


def _default_channel_names(meta: Dict[str, Any], width: int) -> list[str]:
    channel_names = list(meta.get("channel_names", []) or [])
    if len(channel_names) == width:
        return [str(name) for name in channel_names]
    return [f"ch{i}" for i in range(width)]


def _flatten_component(name: str, value: np.ndarray, channel_names: list[str]) -> Dict[str, np.ndarray]:
    arr = np.asarray(value)
    if arr.ndim == 1:
        return {name: arr}
    if arr.ndim == 2:
        if arr.shape[1] != len(channel_names):
            raise ValueError(
                f"Component '{name}' has width {arr.shape[1]}, expected {len(channel_names)} channels."
            )
        return {
            f"{name}__{channel_names[idx]}": arr[:, idx]
            for idx in range(arr.shape[1])
        }
    raise ValueError(f"Component '{name}' must be 1D or 2D for CSV export, got shape {arr.shape}.")


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def save_result(
    result: DecompResult,
    out_dir: Union[str, Path],
    name: str,
    *,
    output_mode: str = "full",
    fields: str | Sequence[str] | None = None,
):
    """
    Save decomposition result to CSV and metadata to JSON.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected_fields = normalize_fields(fields)

    if output_mode != "full":
        payload = serialize_result(result, mode=output_mode, fields=selected_fields)
        with open(out_dir / f"{name}_{output_mode}.json", "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, cls=NumpyEncoder)
        return

    meta = dict(result.meta or {})
    trend = np.asarray(result.trend)
    season = np.asarray(result.season)
    residual = np.asarray(result.residual)

    if trend.ndim not in {1, 2} or season.ndim != trend.ndim or residual.ndim != trend.ndim:
        raise ValueError("trend, season, and residual must all be 1D or all be 2D.")

    width = 1 if trend.ndim == 1 else int(trend.shape[1])
    channel_names = _default_channel_names(meta, width)
    meta.setdefault("channel_names", channel_names)
    meta.setdefault("n_channels", width)
    meta.setdefault("result_layout", "univariate" if trend.ndim == 1 else "multivariate")
    meta.setdefault("component_shapes", {})

    data: Dict[str, np.ndarray] = {}
    data.update(_flatten_component("trend", trend, channel_names))
    data.update(_flatten_component("season", season, channel_names))
    data.update(_flatten_component("residual", residual, channel_names))

    npz_payload: Dict[str, np.ndarray] = {}
    for key, value in result.components.items():
        arr = np.asarray(value)
        meta["component_shapes"][key] = list(arr.shape)
        if arr.ndim in {1, 2}:
            data.update(_flatten_component(key, arr, channel_names))
        elif arr.ndim == 3:
            npz_payload[key] = arr
        else:
            raise ValueError(f"Unsupported component shape for '{key}': {arr.shape}")

    pd.DataFrame(data).to_csv(out_dir / f"{name}_components.csv", index=False)

    if npz_payload:
        np.savez(out_dir / f"{name}_components_3d.npz", **npz_payload)
        meta["saved_3d_components"] = {
            key: {
                "path": f"{name}_components_3d.npz",
                "shape": list(np.asarray(value).shape),
            }
            for key, value in npz_payload.items()
        }

    with open(out_dir / f"{name}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, cls=NumpyEncoder)

    if selected_fields:
        payload = serialize_result(result, mode="full", fields=selected_fields)
        with open(out_dir / f"{name}_full.json", "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, cls=NumpyEncoder)
