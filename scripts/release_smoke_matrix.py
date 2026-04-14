from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

import detime
import tsdecomp
from detime import DecompositionConfig, decompose
from detime._metadata import installed_version


ROOT = Path(__file__).resolve().parents[1]


def _run_command(command: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=dict(os.environ),
    )
    result = {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }
    if proc.returncode != 0:
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def main() -> int:
    report: dict[str, object] = {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "package_version": installed_version(),
        "imports": {
            "detime": detime.__name__,
            "tsdecomp": tsdecomp.__name__,
        },
    }

    series = np.sin(np.linspace(0.0, 2.0 * np.pi, 48)) + np.linspace(0.0, 1.0, 48)
    result = decompose(
        series,
        DecompositionConfig(method="MA_BASELINE", params={"window": 4}, backend="python"),
    )
    report["python_api"] = {
        "trend_shape": list(np.asarray(result.trend).shape),
        "backend_used": result.meta.get("backend_used", "python"),
    }

    report["commands"] = [
        _run_command([sys.executable, "-m", "detime", "version"]),
        _run_command([sys.executable, "-m", "tsdecomp", "version"]),
        _run_command([sys.executable, "-m", "detime", "schema", "--name", "config"]),
    ]

    with tempfile.TemporaryDirectory(prefix="detime-smoke-") as tmp:
        out_dir = Path(tmp) / "run"
        example_series = ROOT / "examples" / "data" / "example_series.csv"
        report["commands"].append(
            _run_command(
                [
                    sys.executable,
                    "-m",
                    "detime",
                    "run",
                    "--method",
                    "STD",
                    "--series",
                    str(example_series),
                    "--col",
                    "value",
                    "--param",
                    "period=12",
                    "--out_dir",
                    str(out_dir),
                    "--output-mode",
                    "summary",
                ]
            )
        )
        summary_path = out_dir / "example_series_summary.json"
        if not summary_path.exists():
            raise RuntimeError(f"Expected summary artifact missing: {summary_path}")
        report["artifact"] = json.loads(summary_path.read_text(encoding="utf-8"))

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
