from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from detime import DecompositionConfig, decompose, native_capabilities
from detime._metadata import installed_version
from detime.registry import METHOD_EXAMPLE_CONFIGS, MethodRegistry


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "generated" / "evidence" / "method_runtime_matrix.json"
DEFAULT_CSV = ROOT / "docs" / "assets" / "generated" / "evidence" / "method_runtime_matrix.csv"


NATIVE_METHOD_EXPORTS = {
    "SSA": "ssa_decompose",
    "STD": "std_decompose",
    "STDR": "std_decompose",
    "MA_BASELINE": "ma_baseline_decompose",
    "MSSA": "mssa_decompose",
    "VMD": "vmd_decompose",
    "GABOR_CLUSTER": "gabor_cluster_decompose",
}


SLOW_METHODS = {"CEEMDAN", "MEMD", "MVMD", "NBEATS_INTERPRETABLE"}


def _make_signal(length: int) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return 0.02 * t + np.sin(2.0 * np.pi * t / 12.0) + 0.2 * np.cos(2.0 * np.pi * t / 6.0)


def _make_panel(length: int) -> np.ndarray:
    t = np.arange(length, dtype=float)
    base = _make_signal(length)
    return np.column_stack(
        [
            base,
            0.8 * base + 0.1 * np.sin(2.0 * np.pi * t / 8.0),
        ]
    )


def _make_gabor_params() -> tuple[dict[str, Any], dict[str, Any]]:
    from detime.methods.gabor_cluster import GaborClusterConfig, GaborClusterModel

    cfg = GaborClusterConfig(win_len=32, hop=16, n_fft=64, n_clusters=6)
    centroids = np.array(
        [
            [0.0, 0.00, 0.0],
            [0.2, 0.12, 0.0],
            [0.4, 0.25, 0.0],
            [0.6, 0.45, 0.0],
            [0.8, 0.70, 0.0],
            [1.0, 1.00, 0.0],
        ],
        dtype=np.float32,
    )
    model = GaborClusterModel(
        centroids=centroids,
        mu=np.zeros(3, dtype=np.float32),
        sigma=np.ones(3, dtype=np.float32),
        cfg=cfg,
    )
    return (
        {"model": model, "trend_freq_thr": 0.15},
        {
            "model": "synthetic_gabor_centroids",
            "win_len": cfg.win_len,
            "hop": cfg.hop,
            "n_fft": cfg.n_fft,
            "n_clusters": cfg.n_clusters,
            "trend_freq_thr": 0.15,
        },
    )


def _case_overrides(length: int) -> dict[str, tuple[dict[str, Any], dict[str, Any], np.ndarray]]:
    signal = _make_signal(length)
    panel = _make_panel(length)
    gabor_params, gabor_public = _make_gabor_params()
    cases: dict[str, tuple[dict[str, Any], dict[str, Any], np.ndarray]] = {
        "SSA": ({"window": 24, "rank": 6, "primary_period": 12}, {"window": 24, "rank": 6, "primary_period": 12}, signal),
        "MSSA": ({"window": 24, "rank": 6, "primary_period": 12}, {"window": 24, "rank": 6, "primary_period": 12}, panel),
        "STD": ({"period": 12}, {"period": 12}, signal),
        "STDR": ({"period": 12}, {"period": 12}, signal),
        "MA_BASELINE": ({"trend_window": 7, "season_period": 12}, {"trend_window": 7, "season_period": 12}, signal),
        "STL": ({"period": 12}, {"period": 12}, signal),
        "ROBUST_STL": ({"period": 12}, {"period": 12}, signal),
        "MSTL": ({"periods": [12, 24]}, {"periods": [12, 24]}, signal),
        "VMD": ({"K": 4, "alpha": 300.0, "primary_period": 12}, {"K": 4, "alpha": 300.0, "primary_period": 12}, signal),
        "WAVELET": ({"wavelet": "db4", "level": 3}, {"wavelet": "db4", "level": 3}, signal),
        "EMD": ({"primary_period": 12, "n_imfs": 4}, {"primary_period": 12, "n_imfs": 4}, signal),
        "CEEMDAN": ({"primary_period": 12, "trials": 4}, {"primary_period": 12, "trials": 4}, signal),
        "MVMD": ({"K": 3, "alpha": 300.0, "primary_period": 12}, {"K": 3, "alpha": 300.0, "primary_period": 12}, panel),
        "MEMD": ({"primary_period": 12}, {"primary_period": 12}, panel),
        "GABOR_CLUSTER": (gabor_params, gabor_public, signal),
    }

    for name in MethodRegistry.list_methods():
        if name.endswith("_BLOCK") and name not in cases:
            params: dict[str, Any] = {
                "primary_period": 12,
                "fit_scope": "full",
                "trend_window": 13,
                "moving_avg": 13,
            }
            if name == "NBEATS_INTERPRETABLE":
                params.update(
                    {
                        "n_epochs": 2,
                        "restarts": 1,
                        "trend_blocks": 1,
                        "seasonality_blocks": 1,
                        "layers": 1,
                        "layer_size": 16,
                    }
                )
            if "WAVELET" in name:
                params.update({"wavelet": "db1", "level": 2, "season_levels": [1]})
            cases[name] = (params, dict(params), signal)
    return cases


def _fallback_case(name: str, length: int) -> tuple[dict[str, Any], dict[str, Any], np.ndarray]:
    cfg = METHOD_EXAMPLE_CONFIGS.get(name, {})
    params = dict(cfg.get("params", {}) or {})
    data = _make_panel(length) if name in {"MSSA", "MVMD", "MEMD"} else _make_signal(length)
    return params, dict(params), data


def _profile(method: str, params: dict[str, Any], data: np.ndarray, backend: str, repeat: int) -> dict[str, Any]:
    samples: list[float] = []
    backend_used = None
    error = None
    captured_stdout = ""
    try:
        for _ in range(repeat):
            stdout_buffer = io.StringIO()
            started = time.perf_counter()
            with contextlib.redirect_stdout(stdout_buffer):
                result = decompose(data, DecompositionConfig(method=method, params=params, backend=backend))
            samples.append((time.perf_counter() - started) * 1000.0)
            backend_used = result.meta.get("backend_used", backend)
            captured_stdout += stdout_buffer.getvalue()
    except Exception as exc:  # pragma: no cover - captures optional backend variability
        error = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"

    return {
        "method": method,
        "backend_requested": backend,
        "backend_used": backend_used,
        "repeat": repeat,
        "mean_ms": round(statistics.fmean(samples), 6) if samples else None,
        "min_ms": round(min(samples), 6) if samples else None,
        "max_ms": round(max(samples), 6) if samples else None,
        "samples_ms": [round(value, 6) for value in samples],
        "error": error,
        "captured_stdout": captured_stdout.strip() or None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a runtime matrix across registered DeTime methods.")
    parser.add_argument("--length", type=int, default=128)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--slow-repeat", type=int, default=2)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args(argv)

    native_ready = native_capabilities()
    cases = _case_overrides(args.length)
    rows: list[dict[str, Any]] = []
    for method in MethodRegistry.list_methods():
        params, public_params, data = cases.get(method, _fallback_case(method, args.length))
        backends = ["python"]
        native_export = NATIVE_METHOD_EXPORTS.get(method)
        if native_export and native_ready.get(native_export):
            backends.append("native")
        repeat = args.slow_repeat if method in SLOW_METHODS else args.repeat
        for backend in backends:
            row = _profile(method, params, data, backend, repeat)
            row["series_shape"] = list(data.shape)
            row["params"] = public_params
            rows.append(row)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package_version": installed_version(),
        "platform": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "machine": platform.machine(),
        },
        "native_capabilities": native_ready,
        "rows": rows,
    }

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = [
        "method",
        "backend_requested",
        "backend_used",
        "repeat",
        "mean_ms",
        "min_ms",
        "max_ms",
        "series_shape",
        "error",
    ]
    with args.csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
