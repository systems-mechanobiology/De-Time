from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from .core import DecompositionConfig
from .registry import decompose


def read_series(*args, **kwargs):
    from .io import read_series as _read_series

    return _read_series(*args, **kwargs)


def _build_config(
    method: str,
    params: Dict[str, Any],
    backend: str = "auto",
    speed_mode: str = "exact",
    n_jobs: int = 1,
    device: str = "cpu",
    channel_names: Sequence[str] | None = None,
):
    return DecompositionConfig(
        method=method,
        params=params,
        backend=backend,
        speed_mode=speed_mode,
        n_jobs=n_jobs,
        device=device,
        channel_names=list(channel_names or []) or None,
    )


def _summary(samples_ms: List[float]) -> Dict[str, float]:
    if not samples_ms:
        return {
            "min_ms": 0.0,
            "mean_ms": 0.0,
            "median_ms": 0.0,
            "p95_ms": 0.0,
            "stdev_ms": 0.0,
        }
    ordered = sorted(samples_ms)
    p95_index = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return {
        "min_ms": float(min(samples_ms)),
        "mean_ms": float(statistics.fmean(samples_ms)),
        "median_ms": float(statistics.median(samples_ms)),
        "p95_ms": float(ordered[p95_index]),
        "stdev_ms": float(statistics.pstdev(samples_ms)) if len(samples_ms) > 1 else 0.0,
    }


def run_profile(
    series: str,
    method: str,
    params: Optional[Dict[str, Any]] = None,
    col: Optional[str] = None,
    cols: Optional[Sequence[str] | str] = None,
    backend: str = "auto",
    speed_mode: str = "exact",
    n_jobs: int = 1,
    device: str = "cpu",
    repeat: int = 5,
    warmup: int = 1,
) -> Dict[str, Any]:
    try:
        series_arr, info = read_series(series, col=col, cols=cols, method=method, return_info=True)
    except TypeError:
        series_arr = read_series(series, col=col, cols=cols)
        info = {
            "channel_names": list(cols or []) if cols else ([col] if col else None),
            "multivariate": np.asarray(series_arr).ndim > 1,
        }
    cfg = _build_config(
        method=method,
        params=dict(params or {}),
        backend=backend,
        speed_mode=speed_mode,
        n_jobs=n_jobs,
        device=device,
        channel_names=info.get("channel_names"),
    )

    warmup = max(0, int(warmup))
    repeat = max(1, int(repeat))
    for _ in range(warmup):
        decompose(series_arr, cfg)

    samples_ms: List[float] = []
    last_result = None
    for _ in range(repeat):
        start = time.perf_counter()
        last_result = decompose(series_arr, cfg)
        samples_ms.append((time.perf_counter() - start) * 1000.0)

    backend_used = backend
    if last_result is not None:
        meta = getattr(last_result, "meta", {}) or {}
        backend_used = meta.get("backend_used", backend)

    report: Dict[str, Any] = {
        "method": method,
        "series": str(series),
        "column": col,
        "columns": list(info.get("channel_names") or []) if info.get("multivariate") else None,
        "backend_requested": backend,
        "backend_used": backend_used,
        "speed_mode": speed_mode,
        "n_jobs": int(n_jobs),
        "device": device,
        "warmup": warmup,
        "repeat": repeat,
        "samples_ms": [float(x) for x in samples_ms],
        "summary": _summary(samples_ms),
    }
    if last_result is not None:
        meta = getattr(last_result, "meta", {}) or {}
        report["result_meta"] = dict(meta)
    return report


def format_profile_report(report: Dict[str, Any], fmt: str = "json") -> str:
    if fmt == "json":
        return json.dumps(report, indent=2, sort_keys=True) + "\n"

    lines = [
        f"method={report.get('method')}",
        f"backend_requested={report.get('backend_requested')}",
        f"backend_used={report.get('backend_used')}",
        f"speed_mode={report.get('speed_mode')}",
        f"repeat={report.get('repeat')}",
        f"warmup={report.get('warmup')}",
        f"samples_ms={report.get('samples_ms')}",
        f"summary={report.get('summary')}",
    ]
    return "\n".join(lines) + "\n"


def write_profile_report(report: Dict[str, Any], path: Path, fmt: str = "json") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_profile_report(report, fmt=fmt), encoding="utf-8")
