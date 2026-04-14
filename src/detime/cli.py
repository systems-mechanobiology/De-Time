import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from .core import DecompositionConfig
from ._metadata import (
    CANONICAL_IMPORT,
    DISTRIBUTION_NAME,
    LEGACY_COMPATIBILITY_SERIES,
    LEGACY_EARLIEST_REMOVAL,
    LEGACY_IMPORT,
    PRODUCT_NAME,
    installed_version,
)
from .recommend import recommend_methods
from .registry import decompose
from .schemas import available_schemas, get_schema
from .serialization import normalize_fields

PACKAGE_VERSION = installed_version()


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


def format_profile_report(*args, **kwargs):
    from .profile import format_profile_report as _format_profile_report

    return _format_profile_report(*args, **kwargs)


def parse_params(param_list: List[str]) -> Dict[str, Any]:
    """Parse list of ``key=value`` strings into a dictionary."""
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


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


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
    save_result(
        res,
        out_dir,
        name,
        output_mode=getattr(args, "output_mode", "full"),
        fields=normalize_fields(getattr(args, "fields", None)),
    )

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
            save_result(
                res,
                out_dir,
                name,
                output_mode=getattr(args, "output_mode", "full"),
                fields=normalize_fields(getattr(args, "fields", None)),
            )
            if args.plot:
                _ensure_plot_supported(series)
                plot_components(res, series, save_path=out_dir / f"{name}_plot.png")
        except Exception as exc:
            print(f"Error processing {fpath}: {exc}")


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
        print(format_profile_report(report, fmt=args.format), end="")


def cmd_version(_args):
    print(PACKAGE_VERSION)


def cmd_schema(args):
    schema = get_schema(args.name)
    text = _json_dump(schema)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(f"Schema written to {args.output}")
        return
    print(text)


def _recommend_request_from_args(args) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        "prefer": args.prefer,
        "allow_optional_backends": args.allow_optional_backends,
        "require_native": args.require_native,
        "top_k": args.top_k,
    }

    if args.series:
        try:
            series, info = read_series(
                args.series,
                col=args.col,
                cols=_parse_cols_arg(args.cols),
                method="MSSA" if args.channels and args.channels > 1 else None,
                return_info=True,
            )
        except TypeError:
            series = read_series(
                args.series,
                col=args.col,
                cols=_parse_cols_arg(args.cols),
            )
            info = {"multivariate": np.asarray(series).ndim > 1}
        arr = np.asarray(series)
        request["length"] = int(arr.shape[0]) if arr.ndim > 0 else 1
        request["channels"] = int(arr.shape[1]) if arr.ndim > 1 else 1
        if args.channels:
            request["channels"] = int(args.channels)
        return request

    if args.length is None:
        raise ValueError("Provide either --series or --length for recommendation.")
    request["length"] = int(args.length)
    request["channels"] = int(args.channels or 1)
    return request


def cmd_recommend(args):
    response = recommend_methods(_recommend_request_from_args(args))
    payload = response.model_dump(mode="json")
    if args.format == "json":
        print(_json_dump(payload))
        return

    for item in payload["recommendations"]:
        reason_codes = ", ".join(item["reason_codes"])
        print(f"{item['rank']}. {item['method']} ({item['score']:.2f})")
        print(f"   {item['summary']}")
        print(f"   reasons: {reason_codes}")


def _add_series_column_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--col", help="Single column name if CSV has multiple columns")
    group.add_argument("--cols", help="Comma-separated column names for multivariate input")


def _cli_identity() -> tuple[str, str]:
    env_brand = os.environ.get("DETIME_CLI_BRAND", "").lower()
    if env_brand == LEGACY_IMPORT:
        return (
            LEGACY_IMPORT,
            (
                f"{LEGACY_IMPORT} CLI is deprecated, supported only through "
                f"{LEGACY_COMPATIBILITY_SERIES}, and may be removed in {LEGACY_EARLIEST_REMOVAL}. "
                f"Install {DISTRIBUTION_NAME} and use {CANONICAL_IMPORT}."
            ),
        )
    if env_brand == CANONICAL_IMPORT:
        return CANONICAL_IMPORT, f"{PRODUCT_NAME} CLI for reproducible time-series decomposition."
    argv0 = Path(sys.argv[0]).name.lower()
    if LEGACY_IMPORT in argv0:
        return (
            LEGACY_IMPORT,
            (
                f"{LEGACY_IMPORT} CLI is deprecated, supported only through "
                f"{LEGACY_COMPATIBILITY_SERIES}, and may be removed in {LEGACY_EARLIEST_REMOVAL}. "
                f"Install {DISTRIBUTION_NAME} and use {CANONICAL_IMPORT}."
            ),
        )
    return CANONICAL_IMPORT, f"{PRODUCT_NAME} CLI for reproducible time-series decomposition."


def _emit_deprecation_notice(prog: str) -> None:
    if prog != LEGACY_IMPORT:
        return
    warnings.warn(
        (
            f"The '{LEGACY_IMPORT}' CLI is deprecated, supported only through "
            f"{LEGACY_COMPATIBILITY_SERIES}, and may be removed in {LEGACY_EARLIEST_REMOVAL}. "
            f"Use '{CANONICAL_IMPORT}' instead."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    print(
        (
            f"DeprecationWarning: '{LEGACY_IMPORT}' is a legacy CLI alias supported only through "
            f"{LEGACY_COMPATIBILITY_SERIES}. Use '{CANONICAL_IMPORT}' instead."
        ),
        file=sys.stderr,
    )


def main():
    prog, description = _cli_identity()
    _emit_deprecation_notice(prog)
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
    p_run.add_argument(
        "--output-mode",
        choices=("full", "summary", "meta"),
        default="full",
        help="Artifact mode: full writes CSV/meta artifacts; summary/meta write lightweight JSON payloads.",
    )
    p_run.add_argument(
        "--fields",
        help="Optional comma-separated top-level fields to retain in the serialized payload view.",
    )
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
    p_batch.add_argument(
        "--output-mode",
        choices=("full", "summary", "meta"),
        default="full",
    )
    p_batch.add_argument(
        "--fields",
        help="Optional comma-separated top-level fields to retain in the serialized payload view.",
    )
    p_batch.add_argument("--plot", action="store_true")
    p_batch.set_defaults(func=cmd_batch)

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

    p_version = subparsers.add_parser("version", help="Print the installed De-Time version")
    p_version.set_defaults(func=cmd_version)

    p_schema = subparsers.add_parser("schema", help="Print or save packaged JSON schemas")
    p_schema.add_argument("--name", required=True, choices=available_schemas())
    p_schema.add_argument("--output", help="Optional output path")
    p_schema.set_defaults(func=cmd_schema)

    p_recommend = subparsers.add_parser("recommend", help="Recommend methods for a workflow")
    p_recommend.add_argument("--series", help="Optional path to input series (csv/parquet)")
    _add_series_column_args(p_recommend)
    p_recommend.add_argument("--length", type=int, help="Series length when no file is supplied")
    p_recommend.add_argument("--channels", type=int, default=1, help="Channel count for recommendation")
    p_recommend.add_argument(
        "--prefer",
        choices=("speed", "balanced", "accuracy"),
        default="balanced",
        help="Optimization preference for recommendation scoring.",
    )
    p_recommend.add_argument(
        "--allow-optional-backends",
        action="store_true",
        help="Allow methods that depend on optional multivariate backends.",
    )
    p_recommend.add_argument(
        "--require-native",
        action="store_true",
        help="Only keep native-backed methods in the recommendation result.",
    )
    p_recommend.add_argument("--top-k", type=int, default=5, help="Maximum number of suggestions to print")
    p_recommend.add_argument("--format", choices=("json", "text"), default="json")
    p_recommend.set_defaults(func=cmd_recommend)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
