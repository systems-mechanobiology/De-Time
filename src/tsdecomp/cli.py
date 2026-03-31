import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from .core import DecompositionConfig
from .registry import MethodRegistry, decompose


def read_series(*args, **kwargs):
    from .io import read_series as _read_series

    return _read_series(*args, **kwargs)


def save_result(*args, **kwargs):
    from .io import save_result as _save_result

    return _save_result(*args, **kwargs)


def plot_components(*args, **kwargs):
    from .viz import plot_components as _plot_components

    return _plot_components(*args, **kwargs)


def plot_error(*args, **kwargs):
    from .viz import plot_error as _plot_error

    return _plot_error(*args, **kwargs)


def run_profile(*args, **kwargs):
    from .profile import run_profile as _run_profile

    return _run_profile(*args, **kwargs)


def write_profile_report(*args, **kwargs):
    from .profile import write_profile_report as _write_profile_report

    return _write_profile_report(*args, **kwargs)


def cmd_merge_results(args):
    from .leaderboard import merge_results

    merge_results(
        input_dirs=args.inputs,
        out_dir=args.out,
        aggregate=args.aggregate,
        plots=args.plots,
    )
    print(f"Done. Merged results saved to {args.out}")


def parse_params(param_list: List[str]) -> Dict[str, Any]:
    """
    Parse list of 'key=value' strings into a dict.
    Supports basic types (int, float, bool, json-list).
    """
    params = {}
    if not param_list:
        return params

    for item in param_list:
        if "=" not in item:
            continue
        key, val = item.split("=", 1)

        try:
            params[key] = json.loads(val)
            continue
        except json.JSONDecodeError:
            pass

        if val.lower() == "true":
            params[key] = True
        elif val.lower() == "false":
            params[key] = False
        else:
            try:
                params[key] = float(val) if "." in val else int(val)
            except ValueError:
                params[key] = val
    return params


def _parse_cols_arg(value: str | None) -> list[str] | None:
    if value is None:
        return None
    cols = [part.strip() for part in value.split(",")]
    cleaned = [item for item in cols if item]
    return cleaned or None


def _read_series_with_info(args):
    cols = _parse_cols_arg(getattr(args, "cols", None))
    try:
        return read_series(
            args.series,
            col=getattr(args, "col", None),
            cols=cols,
            method=args.method,
            return_info=True,
        )
    except TypeError:
        series = read_series(
            args.series,
            col=getattr(args, "col", None),
            cols=cols,
        )
        info = {
            "channel_names": cols or ([args.col] if getattr(args, "col", None) else None),
            "multivariate": np.asarray(series).ndim > 1,
        }
        return series, info


def _build_config(
    method: str,
    params: Dict[str, Any],
    backend: str = "auto",
    speed_mode: str = "exact",
    n_jobs: int = 1,
    profile: bool = False,
    device: str = "cpu",
    channel_names: list[str] | None = None,
):
    return DecompositionConfig(
        method=method,
        params=params,
        backend=backend,
        speed_mode=speed_mode,
        n_jobs=n_jobs,
        profile=profile,
        device=device,
        channel_names=channel_names,
    )


def _annotate_profile(result, backend: str, speed_mode: str, n_jobs: int, runtime_ms: float):
    meta = getattr(result, "meta", None)
    if meta is None:
        meta = {}
        result.meta = meta
    meta.setdefault("backend_requested", backend)
    meta.setdefault("backend_used", backend)
    meta.setdefault("speed_mode", speed_mode)
    meta.setdefault("n_jobs", n_jobs)
    meta["runtime_ms"] = float(runtime_ms)
    return result


def _ensure_plot_supported(series: np.ndarray) -> None:
    if np.asarray(series).ndim > 1:
        raise ValueError(
            "Plotting for multivariate inputs is not supported yet. Re-run without --plot."
        )


def cmd_run(args):
    series, info = _read_series_with_info(args)
    params = parse_params(args.param)

    cfg = _build_config(
        method=args.method,
        params=params,
        backend=args.backend,
        speed_mode=args.speed_mode,
        n_jobs=args.n_jobs,
        profile=args.profile,
        device=args.device,
        channel_names=info.get("channel_names"),
    )

    print(f"Running {args.method} on {args.series}...")
    start = time.perf_counter() if args.profile else None
    res = decompose(series, cfg)
    if start is not None:
        runtime_ms = (time.perf_counter() - start) * 1000.0
        _annotate_profile(res, args.backend, args.speed_mode, args.n_jobs, runtime_ms)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    name = Path(args.series).stem
    save_result(res, out_dir, name)

    if args.plot:
        _ensure_plot_supported(series)
        plot_components(res, series, save_path=out_dir / f"{name}_plot.png")
        plot_error(res, series, save_path=out_dir / f"{name}_error.png")

    print(f"Done. Results saved to {out_dir}")


def cmd_batch(args):
    import glob

    files = sorted(glob.glob(args.glob))
    if not files:
        print(f"No files found for glob: {args.glob}")
        return

    params = parse_params(args.param)
    cols = _parse_cols_arg(getattr(args, "cols", None))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(files)} files. Processing...")

    for fpath in files:
        try:
            try:
                series, info = read_series(
                    fpath,
                    col=getattr(args, "col", None),
                    cols=cols,
                    method=args.method,
                    return_info=True,
                )
            except TypeError:
                series = read_series(
                    fpath,
                    col=getattr(args, "col", None),
                    cols=cols,
                )
                info = {
                    "channel_names": cols or ([args.col] if getattr(args, "col", None) else None),
                    "multivariate": np.asarray(series).ndim > 1,
                }
            cfg = _build_config(
                method=args.method,
                params=params,
                backend=args.backend,
                speed_mode=args.speed_mode,
                n_jobs=args.n_jobs,
                profile=args.profile,
                device=args.device,
                channel_names=info.get("channel_names"),
            )
            start = time.perf_counter() if args.profile else None
            res = decompose(series, cfg)
            if start is not None:
                runtime_ms = (time.perf_counter() - start) * 1000.0
                _annotate_profile(res, args.backend, args.speed_mode, args.n_jobs, runtime_ms)
            name = Path(fpath).stem
            save_result(res, out_dir, name)
            if args.plot:
                _ensure_plot_supported(series)
                plot_components(res, series, save_path=out_dir / f"{name}_plot.png")
        except Exception as e:
            print(f"Error processing {fpath}: {e}")


def cmd_eval(args):
    from .metrics import compute_metrics
    import pandas as pd

    truth_dir = Path(args.truth_dir)
    pred_dir = Path(args.pred_dir)

    metrics_list = args.metrics.split(",")
    results = []

    pred_files = sorted(list(pred_dir.glob("*_components.csv")))

    for p_file in pred_files:
        name = p_file.stem.replace("_components", "")
        t_file = truth_dir / f"{name}.csv"
        if not t_file.exists():
            continue

        try:
            y_pred_df = pd.read_csv(p_file)
            y_true_df = pd.read_csv(t_file)

            row = {"file": name}

            if "trend" in y_true_df.columns and "trend" in y_pred_df.columns:
                m = compute_metrics(y_true_df["trend"].values, y_pred_df["trend"].values)
                for k, v in m.items():
                    if k in metrics_list:
                        row[f"trend_{k}"] = v

            if "season" in y_true_df.columns and "season" in y_pred_df.columns:
                m = compute_metrics(y_true_df["season"].values, y_pred_df["season"].values)
                for k, v in m.items():
                    if k in metrics_list:
                        row[f"season_{k}"] = v

            results.append(row)

        except Exception as e:
            print(f"Error evaluating {name}: {e}")

    if results:
        df_res = pd.DataFrame(results)
        print(df_res)
        if args.out_csv:
            df_res.to_csv(args.out_csv, index=False)
    else:
        print("No matching files found or evaluation failed.")


def cmd_validate(args):
    from .bench_config import resolve_methods
    from .leaderboard import validate_runbook

    validate_runbook(
        suite=args.suite,
        methods=resolve_methods(args.methods),
        length=args.length,
        dt=args.dt,
    )
    print("Validation passed.")


def cmd_run_leaderboard(args):
    from .leaderboard import run_leaderboard

    run_leaderboard(
        suite=args.suite,
        methods=args.methods,
        seeds=args.seeds,
        n_samples=args.n_samples,
        length=args.length,
        dt=args.dt,
        out_dir=args.out,
        export_format=args.export,
        aggregate=args.aggregate,
        plots=args.plots,
    )
    print(f"Done. Artifacts saved to {args.out}")


def cmd_profile(args):
    report = run_profile(
        series=args.series,
        method=args.method,
        col=args.col,
        cols=args.cols,
        params=parse_params(args.param),
        backend=args.backend,
        speed_mode=args.speed_mode,
        n_jobs=args.n_jobs,
        device=args.device,
        repeat=args.repeat,
        warmup=args.warmup,
    )
    if args.output:
        write_profile_report(report, Path(args.output), fmt=args.format)
        print(f"Profile report written to {args.output}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))


def _add_series_column_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--col", help="Single column name if CSV has multiple columns")
    group.add_argument("--cols", help="Comma-separated column names for multivariate input")


def _cli_identity() -> tuple[str, str]:
    env_brand = os.environ.get("DETIME_CLI_BRAND", "").lower()
    if env_brand == "tsdecomp":
        return "tsdecomp", "tsdecomp CLI (legacy package name, De-Time brand)"
    if env_brand == "detime":
        return "detime", "De-Time CLI (legacy tsdecomp alias supported)"
    argv0 = Path(sys.argv[0]).name.lower()
    if "tsdecomp" in argv0:
        return "tsdecomp", "tsdecomp CLI (legacy De-Time alias supported)"
    return "detime", "De-Time CLI (legacy tsdecomp alias supported)"


def main():
    prog, description = _cli_identity()
    parser = argparse.ArgumentParser(prog=prog, description=description)
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_run = subparsers.add_parser("run", help="Run decomposition on a single file")
    p_run.add_argument("--method", required=True, help="Decomposition method name")
    p_run.add_argument("--series", required=True, help="Path to input series (csv/parquet)")
    _add_series_column_args(p_run)
    p_run.add_argument("--param", action="append", help="Method params as key=value")
    p_run.add_argument("--backend", default="auto", help="Backend preference (auto/native/python/gpu)")
    p_run.add_argument("--speed-mode", default="exact", help="Speed mode (exact/fast)")
    p_run.add_argument("--n-jobs", type=int, default=1, help="Parallel job count")
    p_run.add_argument("--profile", action="store_true", help="Record runtime metadata")
    p_run.add_argument("--device", default="cpu", help="Execution device")
    p_run.add_argument("--out_dir", required=True, help="Output directory")
    p_run.add_argument("--plot", action="store_true", help="Generate plots")
    p_run.set_defaults(func=cmd_run)

    p_batch = subparsers.add_parser("batch", help="Run decomposition on a batch of files")
    p_batch.add_argument("--method", required=True)
    p_batch.add_argument("--glob", required=True, help="Glob pattern for input files")
    _add_series_column_args(p_batch)
    p_batch.add_argument("--param", action="append")
    p_batch.add_argument("--backend", default="auto", help="Backend preference (auto/native/python/gpu)")
    p_batch.add_argument("--speed-mode", default="exact", help="Speed mode (exact/fast)")
    p_batch.add_argument("--n-jobs", type=int, default=1, help="Parallel job count")
    p_batch.add_argument("--profile", action="store_true", help="Record runtime metadata")
    p_batch.add_argument("--device", default="cpu", help="Execution device")
    p_batch.add_argument("--out_dir", required=True)
    p_batch.add_argument("--plot", action="store_true")
    p_batch.set_defaults(func=cmd_batch)

    p_eval = subparsers.add_parser("eval", help="Evaluate decomposition results")
    p_eval.add_argument("--truth_dir", required=True)
    p_eval.add_argument("--pred_dir", required=True)
    p_eval.add_argument("--metrics", default="r2,dtw", help="Comma-separated metrics")
    p_eval.add_argument("--out_csv", help="Output CSV for metrics")
    p_eval.set_defaults(func=cmd_eval)

    p_validate = subparsers.add_parser("validate", help="Validate benchmark config")
    p_validate.add_argument("--suite", default="core", help="Benchmark suite")
    p_validate.add_argument("--methods", default="core", help="Method list or preset")
    p_validate.add_argument("--length", type=int, default=512)
    p_validate.add_argument("--dt", type=float, default=1.0)
    p_validate.set_defaults(func=cmd_validate)

    p_leader = subparsers.add_parser("run_leaderboard", help="Run official leaderboard")
    p_leader.add_argument("--suite", default="core", help="Benchmark suite")
    p_leader.add_argument("--methods", default="core", help="Method list or preset")
    p_leader.add_argument("--seeds", default="0", help="Seed list (e.g., 0,1,2 or 0:5)")
    p_leader.add_argument("--n_samples", type=int, default=50, help="Samples per scenario")
    p_leader.add_argument("--length", type=int, default=512)
    p_leader.add_argument("--dt", type=float, default=1.0)
    p_leader.add_argument("--out", default="artifacts/tscomp_v1_core", help="Output directory")
    p_leader.add_argument("--export", default="leaderboard_csv", help="Export format")
    p_leader.add_argument("--aggregate", action="store_true", help="Aggregate summaries")
    p_leader.add_argument("--plots", action="store_true", help="Generate plots")
    p_leader.set_defaults(func=cmd_run_leaderboard)

    p_merge = subparsers.add_parser("merge_results", help="Merge multiple benchmark results")
    p_merge.add_argument("--inputs", nargs="+", required=True, help="Input directories")
    p_merge.add_argument("--out", required=True, help="Output directory")
    p_merge.add_argument("--aggregate", action="store_true", default=True, help="Aggregate summaries")
    p_merge.add_argument("--plots", action="store_true", default=True, help="Generate plots")
    p_merge.set_defaults(func=cmd_merge_results)

    p_profile = subparsers.add_parser("profile", help="Profile a single decomposition run")
    p_profile.add_argument("--method", required=True, help="Decomposition method name")
    p_profile.add_argument("--series", required=True, help="Path to input series (csv/parquet)")
    _add_series_column_args(p_profile)
    p_profile.add_argument("--param", action="append", help="Method params as key=value")
    p_profile.add_argument("--backend", default="auto", help="Backend preference (auto/native/python/gpu)")
    p_profile.add_argument("--speed-mode", default="exact", help="Speed mode (exact/fast)")
    p_profile.add_argument("--n-jobs", type=int, default=1, help="Parallel job count")
    p_profile.add_argument("--device", default="cpu", help="Execution device")
    p_profile.add_argument("--repeat", type=int, default=5, help="Timed repetitions")
    p_profile.add_argument("--warmup", type=int, default=1, help="Warmup runs")
    p_profile.add_argument("--format", choices=("json", "text"), default="json", help="Report format")
    p_profile.add_argument("--output", help="Optional output file for the profile report")
    p_profile.set_defaults(func=cmd_profile)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
