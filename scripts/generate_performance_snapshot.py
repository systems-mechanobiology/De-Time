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


def _profile_method(method: str, params: dict[str, object], backend: str, repeat: int = 4) -> dict[str, object]:
    samples: list[float] = []
    signal = _make_signal()
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
        "params": params,
    }


def main() -> int:
    methods = {
        "SSA": {"window": 36, "rank": 8, "primary_period": 12},
        "STD": {"period": 12},
        "STDR": {"period": 12},
    }
    native_ready = native_capabilities()
    native_name_map = {
        "SSA": "ssa_decompose",
        "STD": "std_decompose",
        "STDR": "std_decompose",
    }

    runs: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for method, params in methods.items():
        python_run = _profile_method(method, params, backend="python")
        runs.append(python_run)

        native_key = native_name_map[method]
        native_run = None
        if native_ready.get(native_key):
            native_run = _profile_method(method, params, backend="native")
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
