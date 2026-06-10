from __future__ import annotations

import csv
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import detime
from detime import DecompositionConfig, decompose, native_capabilities
from detime._metadata import installed_version


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "assets" / "generated" / "evidence" / "performance_snapshot.json"
DEFAULT_CSV = ROOT / "docs" / "assets" / "generated" / "evidence" / "performance_snapshot.csv"


def _make_signal(length: int = 240) -> np.ndarray:
    t = np.arange(length, dtype=float)
    season = np.sin(2.0 * np.pi * t / 12.0)
    return 0.02 * t + 0.8 * season + 0.2 * np.cos(2.0 * np.pi * t / 6.0)


def _make_panel(length: int = 240) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return np.column_stack(
        [
            0.02 * t + np.sin(2.0 * np.pi * t / 12.0),
            0.015 * t + 0.8 * np.sin(2.0 * np.pi * t / 12.0) + 0.2 * np.cos(2.0 * np.pi * t / 6.0),
            0.01 * t + 0.6 * np.sin(2.0 * np.pi * t / 12.0 + 0.3),
        ]
    )


def _make_gabor_params() -> tuple[dict[str, object], dict[str, object]]:
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
    params = {"model": model, "trend_freq_thr": 0.15}
    public_params = {
        "model": "synthetic_gabor_centroids",
        "win_len": cfg.win_len,
        "hop": cfg.hop,
        "n_fft": cfg.n_fft,
        "n_clusters": cfg.n_clusters,
        "trend_freq_thr": 0.15,
    }
    return params, public_params


def _profile_method(
    method: str,
    params: dict[str, object],
    backend: str,
    *,
    signal: np.ndarray,
    public_params: dict[str, object] | None = None,
    repeat: int = 4,
) -> dict[str, object]:
    samples: list[float] = []
    for _ in range(repeat):
        started = time.perf_counter()
        result = decompose(signal, DecompositionConfig(method=method, params=params, backend=backend))
        samples.append((time.perf_counter() - started) * 1000.0)
    return {
        "method": method,
        "backend_requested": backend,
        "backend_used": result.meta.get("backend_used", backend),
        "samples_ms": [round(sample, 6) for sample in samples],
        "mean_ms": round(statistics.fmean(samples), 6),
        "min_ms": round(min(samples), 6),
        "max_ms": round(max(samples), 6),
        "series_length": signal.shape[0],
        "series_shape": list(signal.shape),
        "params": public_params or params,
    }


def main() -> int:
    gabor_params, gabor_public_params = _make_gabor_params()
    benchmarks = [
        {
            "method": "SSA",
            "params": {"window": 36, "rank": 8, "primary_period": 12},
            "signal": _make_signal(),
            "native_key": "ssa_decompose",
        },
        {
            "method": "STD",
            "params": {"period": 12},
            "signal": _make_signal(),
            "native_key": "std_decompose",
        },
        {
            "method": "STDR",
            "params": {"period": 12},
            "signal": _make_signal(),
            "native_key": "std_decompose",
        },
        {
            "method": "MA_BASELINE",
            "params": {"trend_window": 7, "season_period": 12},
            "signal": _make_signal(),
            "native_key": "ma_baseline_decompose",
        },
        {
            "method": "MSSA",
            "params": {"window": 36, "rank": 8, "primary_period": 12},
            "signal": _make_panel(),
            "native_key": "mssa_decompose",
        },
        {
            "method": "VMD",
            "params": {"K": 5, "alpha": 300.0, "primary_period": 12},
            "signal": _make_signal(),
            "native_key": "vmd_decompose",
        },
        {
            "method": "GABOR_CLUSTER",
            "params": gabor_params,
            "public_params": gabor_public_params,
            "signal": _make_signal(),
            "native_key": "gabor_cluster_decompose",
        },
    ]
    native_ready = native_capabilities()

    runs: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for item in benchmarks:
        method = str(item["method"])
        params = item["params"]
        signal = item["signal"]
        public_params = item.get("public_params")
        python_run = _profile_method(
            method,
            params,
            backend="python",
            signal=signal,
            public_params=public_params,
        )
        runs.append(python_run)

        native_key = str(item["native_key"])
        native_run = None
        if native_ready.get(native_key):
            native_run = _profile_method(
                method,
                params,
                backend="native",
                signal=signal,
                public_params=public_params,
            )
            runs.append(native_run)

        row = {
            "method": method,
            "python_mean_ms": python_run["mean_ms"],
            "native_mean_ms": native_run["mean_ms"] if native_run else None,
            "speedup": round(
                float(python_run["mean_ms"]) / max(float(native_run["mean_ms"]), 1e-12),
                6,
            )
            if native_run
            else None,
        }
        summary_rows.append(row)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package_version": installed_version(),
        "platform": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "machine": platform.machine(),
        },
        "native_capabilities": native_ready,
        "runs": runs,
        "summary": summary_rows,
    }

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with DEFAULT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["method", "python_mean_ms", "native_mean_ms", "speedup"])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
