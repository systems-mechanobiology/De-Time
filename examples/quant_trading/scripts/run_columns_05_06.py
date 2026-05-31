from __future__ import annotations

"""Run Columns 05-06 end to end."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Quant Columns 05 and 06.")
    p.add_argument("--use-bundled-sample", action="store_true", help="Use bundled real samples for offline execution.")
    p.add_argument("--report-dir", default="examples/quant_trading/reports")
    p.add_argument("--method", default="STL")
    p.add_argument("--period", default="63", help="Default period for pair-spread decomposition.")
    p.add_argument("--rotation-period", default="42", help="Period used by the bundled FX rotation tutorial run.")
    p.add_argument("--train-window", type=int, default=180)
    p.add_argument("--step", type=int, default=126)
    p.add_argument("--rotation-train-window", type=int, default=126)
    p.add_argument("--rotation-step", type=int, default=252)
    p.add_argument("--fee-bps", type=float, default=1.0)
    p.add_argument("--slippage-bps", type=float, default=2.0)
    return p.parse_args()


def _run(cmd: list[str]) -> None:
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def _copy_column_outputs(work_report_dir: Path, target_report_dir: Path, prefix: str) -> None:
    target_report_dir.mkdir(parents=True, exist_ok=True)
    for path in work_report_dir.glob(f"{prefix}_*"):
        shutil.copy2(path, target_report_dir / path.name)
    manifest_path = target_report_dir / f"{prefix}_run_manifest.json"
    comparison_path = target_report_dir / f"{prefix}_strategy_comparison.csv"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            manifest["result_file"] = str(comparison_path)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        except Exception:
            pass


def main() -> int:
    args = parse_args()
    target_report_dir = Path(args.report_dir)
    target_report_dir.mkdir(parents=True, exist_ok=True)
    work_report_dir = Path(tempfile.mkdtemp(prefix="detime_quant_columns_05_06_"))
    extra = ["--use-bundled-sample"] if args.use_bundled_sample else []
    shared_costs = [
        "--fee-bps", str(args.fee_bps),
        "--slippage-bps", str(args.slippage_bps),
    ]
    try:
        _run([
            sys.executable,
            "examples/quant_trading/scripts/run_column_05_pairs_spread_decomposition.py",
            "--report-dir", str(work_report_dir),
            "--method", args.method,
            "--period", str(args.period),
            "--train-window", str(args.train_window),
            "--step", str(args.step),
            *shared_costs,
            *extra,
        ])
        _copy_column_outputs(work_report_dir, target_report_dir, "column_05")
        _run([
            sys.executable,
            "examples/quant_trading/scripts/run_column_06_cross_sectional_rotation.py",
            "--report-dir", str(work_report_dir),
            "--method", args.method,
            "--period", str(args.rotation_period),
            "--train-window", str(args.rotation_train_window),
            "--step", str(args.rotation_step),
            *shared_costs,
            *extra,
        ])
        _copy_column_outputs(work_report_dir, target_report_dir, "column_06")
    finally:
        shutil.rmtree(work_report_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
