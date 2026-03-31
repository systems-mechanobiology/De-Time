import numpy as np
from importlib import import_module
from typing import Any, Dict

from ..core import DecompResult
from ..registry import MethodRegistry

def _load_python_backend():
    try:
        module = import_module("synthetic_ts_bench.sl_lib")
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise ImportError(
            "synthetic_ts_bench is required for SL_LIB decomposition."
        ) from exc
    return module.sl_lib_decompose


@MethodRegistry.register("SL_LIB")
def sl_lib_wrapper(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    sl_lib_decompose = _load_python_backend()
    cfg = dict(params or {})
    res = sl_lib_decompose(
        np.asarray(y, dtype=float).ravel(),
        config=cfg,
        fs=float(cfg.get("fs", 1.0)),
        meta=None,
    )
    meta_out = dict(getattr(res, "extra", {}) or {})
    meta_out.setdefault("method", "SL_LIB")
    return DecompResult(
        trend=np.asarray(res.trend, dtype=float),
        season=np.asarray(res.season, dtype=float),
        residual=np.asarray(res.residual, dtype=float),
        meta=meta_out,
    )
