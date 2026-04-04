import numpy as np
from typing import Dict, Any, Optional
from ..backends import finalize_result, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry

@MethodRegistry.register("STL")
def stl_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """
    STL decomposition: y = trend + seasonal + resid.
    """
    try:
        from statsmodels.tsa.seasonal import STL
    except ImportError as exc:
        raise ImportError("statsmodels is required for STL decomposition.") from exc

    cfg, runtime = split_runtime_params(params)
    if runtime.backend in {"native", "gpu"}:
        raise ValueError("STL only provides a python backend.")
    period = cfg.pop("period", None)
    if period is None:
        raise ValueError("STL requires 'period' in params.")
    period = int(period)

    stl = STL(y, period=period, **cfg)
    res = stl.fit()

    trend = np.asarray(res.trend)
    seasonal = np.asarray(res.seasonal)
    residual = np.asarray(res.resid)
    
    result = DecompResult(
        trend=trend,
        season=seasonal,
        residual=residual,
        meta={"method": "STL", "params": {"period": period, **cfg}},
    )
    return finalize_result(result, method="STL", runtime=runtime, backend_used="python")

@MethodRegistry.register("MSTL")
def mstl_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    try:
        from statsmodels.tsa.seasonal import MSTL
    except ImportError as exc:
        raise ImportError("statsmodels>=0.14 is required for MSTL decomposition.") from exc

    cfg, runtime = split_runtime_params(params)
    if runtime.backend in {"native", "gpu"}:
        raise ValueError("MSTL only provides a python backend.")
    periods = cfg.pop("periods", None)
    if periods is None:
         # Try to infer or require it
         raise ValueError("MSTL requires 'periods' list in params.")
    
    # Ensure periods are integers >= 2
    periods = [int(p) for p in periods if p >= 2]
    if not periods:
        raise ValueError("MSTL 'periods' must contain at least one integer >= 2.")

    mstl = MSTL(y, periods=periods, **cfg)
    res = mstl.fit()
    
    seasonal = res.seasonal
    if seasonal.ndim == 2:
        season = seasonal.sum(axis=1)
    else:
        season = seasonal
    
    trend = res.trend
    residual = res.resid
    
    result = DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        meta={"method": "MSTL", "params": {"periods": periods, **cfg}}
    )
    return finalize_result(result, method="MSTL", runtime=runtime, backend_used="python")

@MethodRegistry.register("ROBUST_STL")
def robuststl_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    try:
        from statsmodels.tsa.seasonal import STL
    except ImportError as exc:
        raise ImportError("statsmodels is required for RobustSTL.") from exc

    cfg, runtime = split_runtime_params(params)
    if runtime.backend in {"native", "gpu"}:
        raise ValueError("ROBUST_STL only provides a python backend.")
    period = cfg.pop("period", None)
    if period is None:
        raise ValueError("RobustSTL requires 'period' in params.")
    period = int(period)

    # RobustSTL is just STL with robust=True by default and maybe some specific tuning
    robust = cfg.pop("robust", True)
    
    stl = STL(y, period=period, robust=robust, **cfg)
    res = stl.fit()

    result = DecompResult(
        trend=res.trend,
        season=res.seasonal,
        residual=res.resid,
        meta={"method": "ROBUST_STL", "params": {"period": period, "robust": robust, **cfg}}
    )
    return finalize_result(result, method="ROBUST_STL", runtime=runtime, backend_used="python")
