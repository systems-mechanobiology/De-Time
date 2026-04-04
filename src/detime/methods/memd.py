from __future__ import annotations

from time import perf_counter
from typing import Any, Dict

from ..backends import finalize_result, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry
from .mvmd import _ensure_multivariate_input, _group_multivariate_modes, _run_backend


@MethodRegistry.register("MEMD", input_mode="multivariate")
def memd_decompose(
    y: Any,
    params: Dict[str, Any],
) -> DecompResult:
    started_at = perf_counter()
    cfg, runtime = split_runtime_params(params)
    if runtime.backend == "native":
        raise RuntimeError("MEMD does not provide a native backend yet; use backend='python' or 'auto'.")
    if runtime.backend == "gpu":
        raise ValueError("MEMD does not provide a GPU backend.")

    y_arr = _ensure_multivariate_input(y, "MEMD")
    imfs = _run_backend("MEMD", y_arr, cfg)
    result = _group_multivariate_modes(imfs, cfg, method="MEMD")
    result.components = {"imfs": result.components["modes"]}
    return finalize_result(
        result,
        method="MEMD",
        runtime=runtime,
        backend_used="python",
        started_at=started_at,
    )
