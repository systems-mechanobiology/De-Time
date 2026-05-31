from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


def _run(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=10).strip()
    except Exception:
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record local hardware and Python environment metadata.")
    parser.add_argument("--output", default=os.environ.get("OUTPUT", "examples/quant_trading/reports/hardware_probe.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    payload: dict[str, object] = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "hostname": platform.node(),
        "disk_free_gb": round(shutil.disk_usage(".").free / (1024**3), 3),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "nvidia_smi": _run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
    }
    try:
        import numpy as np
        import pandas as pd

        payload["numpy_version"] = np.__version__
        payload["pandas_version"] = pd.__version__
    except Exception as exc:
        payload["numpy_pandas_error"] = str(exc)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"hardware probe written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
