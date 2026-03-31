import numpy as np
from importlib import import_module
from typing import Any, Dict

from ..core import DecompResult
from ..registry import MethodRegistry

def _load_python_backend():
    try:
        module = import_module("synthetic_ts_bench.dr_ts_ae")
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise ImportError(
            "synthetic_ts_bench is required for DR_TS_AE decomposition."
        ) from exc
    return module.dr_ts_ae_decompose


@MethodRegistry.register("DR_TS_AE")
def dr_ts_ae_wrapper(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    dr_ts_ae_decompose = _load_python_backend()
    cfg = dict(params or {})
    meta = {}
    if "primary_period" in cfg:
        meta["primary_period"] = cfg["primary_period"]

    res = dr_ts_ae_decompose(
        np.asarray(y, dtype=float).ravel(),
        config=cfg,
        fs=float(cfg.get("fs", 1.0)),
        meta=meta or None,
    )
    meta_out = dict(getattr(res, "extra", {}) or {})
    meta_out.setdefault("method", "DR_TS_AE")
    return DecompResult(
        trend=np.asarray(res.trend, dtype=float),
        season=np.asarray(res.season, dtype=float),
        residual=np.asarray(res.residual, dtype=float),
        meta=meta_out,
    )
