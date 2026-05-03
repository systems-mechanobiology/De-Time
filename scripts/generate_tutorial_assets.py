from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
DEFAULT_OUTPUT_ROOT = ROOT / "docs" / "assets" / "generated" / "tutorials"

def _prefer_repo_source() -> None:
    """Prefer the checkout over stale local editable wheels during docs generation."""
    sys.meta_path[:] = [
        finder for finder in sys.meta_path
        if finder.__class__.__module__ != "_de_time_editable"
    ]
    src = str(SRC_DIR)
    if src not in sys.path:
        sys.path.insert(0, src)


_prefer_repo_source()

from detime import DecompositionConfig, decompose  # noqa: E402


def _reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    src_path = str(SRC_DIR)
    env["PYTHONPATH"] = src_path if not existing else os.pathsep.join([src_path, existing])
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


def _run_command(command: list[str], stdout_path: Path | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=_command_env(),
        text=True,
        capture_output=True,
        check=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout = completed.stdout.replace("\r\n", "\n")
    if completed.stderr:
        stdout = stdout.rstrip() + ("\n\n[stderr]\n" if stdout else "[stderr]\n") + completed.stderr
    stdout = re.sub(
        r"[A-Za-z]:[^\n]*?(docs[\\/]+assets[\\/]+generated[\\/]+tutorials[^\n]*)",
        r"\1",
        stdout,
    )
    stdout = stdout.replace("\\", "/")
    if stdout_path is not None:
        _write_text(stdout_path, stdout)
    return stdout


def _python_script(script: str, *args: str) -> list[str]:
    bootstrap = (
        "import runpy, sys; "
        "sys.meta_path[:] = [finder for finder in sys.meta_path "
        "if finder.__class__.__module__ != '_de_time_editable']; "
        f"sys.path.insert(0, {str(SRC_DIR)!r}); "
        "script = sys.argv[1]; "
        "script_args = sys.argv[2:]; "
        "sys.argv = [script, *script_args]; "
        "runpy.run_path(script, run_name='__main__')"
    )
    return [sys.executable, "-c", bootstrap, str(ROOT / script), *args]


def _detime_cli(*args: str) -> list[str]:
    bootstrap = (
        "import sys; "
        "sys.meta_path[:] = [finder for finder in sys.meta_path "
        "if finder.__class__.__module__ != '_de_time_editable']; "
        f"sys.path.insert(0, {str(SRC_DIR)!r}); "
        "from detime.cli import main; "
        "sys.argv = ['detime', *sys.argv[1:]]; "
        "main()"
    )
    return [sys.executable, "-c", bootstrap, *args]


def _load_series(path: Path, column_names: list[str]) -> np.ndarray:
    frame = pd.read_csv(path)
    return frame[column_names].to_numpy(dtype=float)


def _write_dataframe(path: Path, records: list[dict[str, Any]]) -> None:
    pd.DataFrame.from_records(records).to_csv(path, index=False)


def _generate_univariate_snapshot(out_dir: Path) -> None:
    frame = pd.read_csv(ROOT / "examples" / "data" / "example_series.csv")
    series = frame["value"].to_numpy(dtype=float)
    records: list[dict[str, Any]] = []
    jobs = {
        "SSA": DecompositionConfig(
            method="SSA",
            params={"window": 24, "rank": 6, "primary_period": 12},
        ),
        "STD": DecompositionConfig(
            method="STD",
            params={"period": 12},
        ),
    }
    for method, config in jobs.items():
        result = decompose(series, config)
        reconstruction = np.asarray(result.trend) + np.asarray(result.season) + np.asarray(result.residual)
        records.append(
            {
                "method": method,
                "backend_used": result.meta.get("backend_used"),
                "trend_mean": float(np.mean(result.trend)),
                "trend_std": float(np.std(result.trend)),
                "season_std": float(np.std(result.season)),
                "residual_rms": float(np.sqrt(np.mean(np.square(result.residual)))),
                "residual_peak_abs": float(np.max(np.abs(result.residual))),
                "reconstruction_max_abs_error": float(np.max(np.abs(series - reconstruction))),
            }
        )
    _write_dataframe(out_dir / "method_snapshot.csv", records)
    _write_json(out_dir / "method_snapshot.json", records)


def generate_tutorial_assets(output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    output_root = output_root.resolve()
    visual_univariate = output_root / "visual-univariate"
    visual_multivariate = output_root / "visual-multivariate"
    visual_comparison = output_root / "visual-comparison"
    univariate = output_root / "univariate"
    multivariate = output_root / "multivariate"
    cli_root = output_root / "cli-and-profiling"
    single_run = cli_root / "single-file"
    multi_run = cli_root / "multivariate"
    batch_run = cli_root / "batch"
    profile_run = cli_root / "profile"
    machine_run = cli_root / "machine"

    for directory in (
        visual_univariate,
        visual_multivariate,
        visual_comparison,
        univariate,
        multivariate,
        single_run,
        multi_run,
        batch_run,
        profile_run,
        machine_run,
    ):
        _reset_dir(directory)

    _run_command(
        _python_script("examples/visual_univariate_walkthrough.py", "--out-dir", str(visual_univariate)),
        stdout_path=visual_univariate / "run_stdout.txt",
    )
    _run_command(
        _python_script("examples/visual_multivariate_walkthrough.py", "--out-dir", str(visual_multivariate)),
        stdout_path=visual_multivariate / "run_stdout.txt",
    )
    _run_command(
        _python_script("examples/visual_method_comparison.py", "--out-dir", str(visual_comparison)),
        stdout_path=visual_comparison / "run_stdout.txt",
    )

    _run_command(
        _python_script("examples/univariate_quickstart.py"),
        stdout_path=univariate / "python_example_stdout.txt",
    )
    _run_command(
        _python_script("examples/multivariate_mssa.py"),
        stdout_path=multivariate / "python_example_stdout.txt",
    )
    _generate_univariate_snapshot(univariate)

    _run_command(
        _detime_cli(
            "run",
            "--method",
            "SSA",
            "--series",
            "examples/data/example_series.csv",
            "--col",
            "value",
            "--param",
            "window=24",
            "--param",
            "rank=6",
            "--param",
            "primary_period=12",
            "--out_dir",
            str(single_run),
            "--output-mode",
            "summary",
            "--plot",
        ),
        stdout_path=single_run / "command_stdout.txt",
    )
    _run_command(
        _detime_cli(
            "run",
            "--method",
            "MSSA",
            "--series",
            "examples/data/example_multivariate.csv",
            "--cols",
            "x0,x1",
            "--param",
            "window=24",
            "--param",
            "rank=8",
            "--param",
            "primary_period=12",
            "--out_dir",
            str(multi_run),
            "--output-mode",
            "summary",
        ),
        stdout_path=multi_run / "command_stdout.txt",
    )
    _run_command(
        _detime_cli(
            "batch",
            "--method",
            "STD",
            "--glob",
            "examples/data/batch/*.csv",
            "--col",
            "value",
            "--param",
            "period=12",
            "--out_dir",
            str(batch_run),
            "--output-mode",
            "meta",
        ),
        stdout_path=batch_run / "command_stdout.txt",
    )

    _run_command(
        _detime_cli(
            "profile",
            "--method",
            "SSA",
            "--series",
            "examples/data/example_series.csv",
            "--col",
            "value",
            "--param",
            "window=24",
            "--param",
            "rank=6",
            "--param",
            "primary_period=12",
            "--repeat",
            "5",
            "--warmup",
            "1",
            "--format",
            "text",
        ),
        stdout_path=profile_run / "ssa_profile_text.txt",
    )
    _run_command(
        _detime_cli(
            "profile",
            "--method",
            "MSSA",
            "--series",
            "examples/data/example_multivariate.csv",
            "--cols",
            "x0,x1",
            "--param",
            "window=24",
            "--param",
            "primary_period=12",
            "--repeat",
            "3",
            "--format",
            "json",
        ),
        stdout_path=profile_run / "mssa_profile.json",
    )
    _run_command(
        _detime_cli(
            "profile",
            "--method",
            "STD",
            "--series",
            "examples/data/example_series.csv",
            "--col",
            "value",
            "--param",
            "period=12",
            "--backend",
            "native",
            "--repeat",
            "10",
            "--warmup",
            "2",
            "--format",
            "text",
            "--output",
            str(profile_run / "std_native.txt"),
        ),
        stdout_path=profile_run / "std_native_stdout.txt",
    )

    _run_command(
        _detime_cli("schema", "--name", "method-registry"),
        stdout_path=machine_run / "method_registry_schema.json",
    )
    _run_command(
        _detime_cli(
            "recommend",
            "--length",
            "192",
            "--channels",
            "3",
            "--prefer",
            "accuracy",
            "--format",
            "text",
        ),
        stdout_path=machine_run / "recommend_text.txt",
    )
    _run_command(
        _detime_cli(
            "recommend",
            "--length",
            "192",
            "--channels",
            "3",
            "--prefer",
            "accuracy",
            "--format",
            "json",
        ),
        stdout_path=machine_run / "recommend.json",
    )

    print(f"wrote tutorial assets to {output_root}")
    return output_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate reproducible tutorial assets for the docs site.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory that will receive generated tutorial artifacts.",
    )
    args = parser.parse_args()
    generate_tutorial_assets(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
