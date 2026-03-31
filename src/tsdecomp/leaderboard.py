"""Runbook-aligned leaderboard pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd

from .bench_config import (
    BENCHMARK_VERSION,
    CORE_METHODS,
    DEFAULT_METHOD_CONFIGS,
    SCENARIO_PERIODS,
    SCENARIO_TIER,
    get_suite,
    normalize_periods,
    resolve_methods,
    select_primary_period,
)
from .metrics import r2_score, spectral_correlation

try:  # pragma: no cover - optional accelerator
    from numba import njit
except ImportError:  # pragma: no cover - fallback
    njit = None

LEADERBOARD_COLUMNS = [
    "suite_version",
    "suite",
    "package_version",
    "git_commit",
    "scenario_id",
    "scenario_tier",
    "seed",
    "draw_id",
    "length",
    "dt",
    "method",
    "status",
    "error_type",
    "error_message",
    "scenario_periods_json",
    "method_config_json",
    "metric_T_r2",
    "metric_T_dtw",
    "metric_S_spectral_corr",
    "metric_S_maxlag_corr",
    "metric_S_r2",
]

PRIMARY_METRICS = [
    "metric_T_r2",
    "metric_T_dtw",
    "metric_S_spectral_corr",
    "metric_S_maxlag_corr",
]


def parse_seeds(seeds: str | Sequence[int]) -> List[int]:
    if isinstance(seeds, str):
        spec = seeds.strip()
        if not spec:
            return []
        if ":" in spec:
            parts = [p for p in spec.split(":") if p.strip()]
            if len(parts) not in {2, 3}:
                raise ValueError(f"Invalid seed range '{seeds}'. Use start:end[:step].")
            start = int(parts[0])
            end = int(parts[1])
            step = int(parts[2]) if len(parts) == 3 else 1
            return list(range(start, end, step))
        return [int(val.strip()) for val in spec.split(",") if val.strip()]
    return [int(val) for val in seeds]


def _hash_to_seed(text: str) -> int:
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little") % (2**32 - 1)


def derive_sample_seed(base_seed: int, scenario_id: str, draw_id: int) -> int:
    return _hash_to_seed(f"{base_seed}:{scenario_id}:{draw_id}")


def derive_method_seed(base_seed: int, scenario_id: str, draw_id: int, method: str) -> int:
    return _hash_to_seed(f"{base_seed}:{scenario_id}:{draw_id}:{method}")


def _safe_json_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def _truncate(text: str, limit: int = 200) -> str:
    if text is None:
        return ""
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.size == 0:
        return float("nan")
    x_c = x - x.mean()
    y_c = y - y.mean()
    vx = np.mean(x_c**2)
    vy = np.mean(y_c**2)
    if vx <= 1e-12 or vy <= 1e-12:
        return float("nan")
    return float(np.mean(x_c * y_c) / np.sqrt(vx * vy))


def _max_lag_corr(x: np.ndarray, y: np.ndarray, max_lag: int = 10) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.size < 3:
        return float("nan")
    best = -np.inf
    for lag in range(-max_lag, max_lag + 1):
        if lag == 0:
            xc, yc = x, y
        elif lag > 0:
            xc, yc = x[lag:], y[:-lag]
        else:
            k = -lag
            xc, yc = x[:-k], y[k:]
        if xc.size < 3:
            continue
        val = _safe_corr(xc, yc)
        if np.isfinite(val) and val > best:
            best = val
    return float(best if best != -np.inf else np.nan)


def _dtw_distance_numpy(x: np.ndarray, y: np.ndarray) -> float:
    n = x.size
    m = y.size
    if n == 0 or m == 0:
        return float("nan")
    prev = np.full(m + 1, np.inf, dtype=float)
    curr = np.full(m + 1, np.inf, dtype=float)
    prev[0] = 0.0
    for i in range(1, n + 1):
        curr[0] = np.inf
        xi = x[i - 1]
        for j in range(1, m + 1):
            cost = (xi - y[j - 1]) ** 2
            curr[j] = cost + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev
    return float(np.sqrt(prev[m]))


if njit:  # pragma: no cover - jit in tests is optional

    @njit
    def _dtw_distance_numba(x: np.ndarray, y: np.ndarray) -> float:
        n = x.size
        m = y.size
        if n == 0 or m == 0:
            return np.nan
        prev = np.empty(m + 1, dtype=np.float64)
        curr = np.empty(m + 1, dtype=np.float64)
        for j in range(m + 1):
            prev[j] = np.inf
            curr[j] = np.inf
        prev[0] = 0.0
        for i in range(1, n + 1):
            curr[0] = np.inf
            xi = x[i - 1]
            for j in range(1, m + 1):
                cost = (xi - y[j - 1]) ** 2
                a = prev[j]
                b = curr[j - 1]
                c = prev[j - 1]
                if b < a:
                    a = b
                if c < a:
                    a = c
                curr[j] = cost + a
            for j in range(m + 1):
                prev[j] = curr[j]
        return np.sqrt(prev[m])

    def dtw_distance(x: np.ndarray, y: np.ndarray) -> float:
        return float(_dtw_distance_numba(x, y))

else:

    def dtw_distance(x: np.ndarray, y: np.ndarray) -> float:
        return _dtw_distance_numpy(x, y)


def compute_leaderboard_metrics(
    true_trend: np.ndarray,
    est_trend: np.ndarray,
    true_season: np.ndarray,
    est_season: np.ndarray,
    fs: float,
) -> Dict[str, float]:
    metrics: Dict[str, float] = {
        "metric_T_r2": float("nan"),
        "metric_T_dtw": float("nan"),
        "metric_S_spectral_corr": float("nan"),
        "metric_S_maxlag_corr": float("nan"),
        "metric_S_r2": float("nan"),
    }
    if true_trend.shape == est_trend.shape and true_trend.size > 0:
        metrics["metric_T_r2"] = float(r2_score(true_trend, est_trend))
        metrics["metric_T_dtw"] = float(dtw_distance(true_trend, est_trend))
    if true_season.shape == est_season.shape and true_season.size > 0:
        metrics["metric_S_r2"] = float(r2_score(true_season, est_season))
        metrics["metric_S_spectral_corr"] = float(
            spectral_correlation(true_season, est_season, fs=fs)
        )
        metrics["metric_S_maxlag_corr"] = float(_max_lag_corr(true_season, est_season))
    return metrics


def build_method_config(
    method: str,
    scenario_periods: Sequence[int],
    length: int,
) -> Tuple[Dict[str, Any], List[int]]:
    base_cfg = dict(DEFAULT_METHOD_CONFIGS.get(method, {}))
    periods = normalize_periods(scenario_periods, length)
    primary = select_primary_period(periods)

    if method in {"stl", "robuststl"}:
        if primary is None:
            raise ValueError(f"Method '{method}' requires a primary period.")
        base_cfg["period"] = primary
    elif method == "mstl":
        if not periods:
            raise ValueError("MSTL requires seasonal periods.")
        base_cfg["periods"] = periods
    elif method in {"ssa", "emd", "ceemdan", "vmd"}:
        if primary is not None:
            base_cfg["primary_period"] = primary
    elif method == "ma_baseline":
        if primary is not None:
            base_cfg["season_period"] = primary

    cfg = {k: v for k, v in base_cfg.items() if v is not None}
    return cfg, periods


def _method_meta_from_periods(periods: Sequence[int]) -> Dict[str, Any]:
    meta: Dict[str, Any] = {"cycles": [{"params": {"periods": list(periods)}}]}
    primary = select_primary_period(periods)
    if primary is not None:
        meta["primary_period"] = primary
    return meta


def _series_from_scenario(
    scenario_id: str,
    length: int,
    dt: float,
    seed: int,
) -> Dict[str, Any]:
    from synthetic_ts_bench import generate_series, make_scenario

    cfg = make_scenario(scenario_id, length=length, random_seed=seed)
    cfg.dt = dt
    series = generate_series(cfg)
    meta = series.get("meta", {})
    meta["scenario_id"] = scenario_id
    series["meta"] = meta
    return series


def _package_version() -> str:
    try:
        from importlib import metadata

        for dist_name in ("de-time", "tsdecomp"):
            try:
                return metadata.version(dist_name)
            except Exception:
                continue
        raise RuntimeError("distribution metadata not found")
    except Exception:
        pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
        if pyproject.exists():
            for line in pyproject.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version"):
                    _, val = line.split("=", 1)
                    return val.strip().strip('"').strip("'")
        return "0.0.0+local"


def _git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def _runtime_env() -> Dict[str, Any]:
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "executable": sys.executable,
        "threads": {
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
        },
    }


def _decompose_series(*args: Any, **kwargs: Any) -> Any:
    from synthetic_ts_bench.decomp_methods import decompose_series

    return decompose_series(*args, **kwargs)


def write_env_artifacts(out_dir: Path, package_version: str, git_commit: str) -> None:
    env_dir = out_dir / "env"
    env_dir.mkdir(parents=True, exist_ok=True)
    (env_dir / "git_commit.txt").write_text(f"{git_commit}\n", encoding="utf-8")
    (env_dir / "package_version.txt").write_text(
        f"{package_version}\n", encoding="utf-8"
    )
    (env_dir / "runtime_env.json").write_text(
        _safe_json_dumps(_runtime_env()), encoding="utf-8"
    )
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"],
            stderr=subprocess.STDOUT,
        )
        (env_dir / "pip_freeze.txt").write_bytes(out)
    except Exception as exc:  # pragma: no cover - env-specific
        (env_dir / "pip_freeze.txt").write_text(
            f"pip freeze failed: {exc}\n", encoding="utf-8"
        )


def validate_runbook(
    suite: str,
    methods: Sequence[str],
    length: int,
    dt: float,
) -> None:
    if length <= 1:
        raise ValueError("length must be > 1.")
    if dt <= 0:
        raise ValueError("dt must be > 0.")
    scenarios = get_suite(suite)
    if not scenarios:
        raise ValueError(f"Suite '{suite}' has no scenarios.")
    missing_periods = [s for s in scenarios if s not in SCENARIO_PERIODS]
    if missing_periods:
        raise ValueError(f"Missing SCENARIO_PERIODS for: {missing_periods}")
    missing_tiers = [s for s in scenarios if s not in SCENARIO_TIER]
    if missing_tiers:
        raise ValueError(f"Missing SCENARIO_TIER for: {missing_tiers}")

    for method in methods:
        if method not in DEFAULT_METHOD_CONFIGS:
            raise ValueError(f"Unknown method '{method}'.")
    period_fields = {
        "stl": "period",
        "robuststl": "period",
        "mstl": "periods",
        "ma_baseline": "season_period",
    }
    for method, field in period_fields.items():
        if method not in DEFAULT_METHOD_CONFIGS:
            continue
        val = DEFAULT_METHOD_CONFIGS[method].get(field)
        if val is not None and val != []:
            raise ValueError(
                f"{method} config sets '{field}' directly; period injection must be dynamic."
            )


def run_benchmark(
    suite: str,
    methods: Sequence[str],
    seeds: Sequence[int],
    n_samples: int,
    length: int,
    dt: float,
) -> pd.DataFrame:
    scenarios = get_suite(suite)
    package_version = _package_version()
    git_commit = _git_commit()
    fs = 1.0 / dt if dt else 1.0

    records: List[Dict[str, Any]] = []
    for seed in seeds:
        for scenario_id in scenarios:
            scenario_periods = SCENARIO_PERIODS.get(scenario_id, [])
            tier = SCENARIO_TIER.get(scenario_id, 0)
            for draw_id in range(n_samples):
                sample_seed = derive_sample_seed(seed, scenario_id, draw_id)
                series = _series_from_scenario(
                    scenario_id, length=length, dt=dt, seed=sample_seed
                )
                true_trend = np.asarray(series.get("trend", []), dtype=float)
                true_season = np.asarray(series.get("season", []), dtype=float)

                for method in methods:
                    method_seed = derive_method_seed(seed, scenario_id, draw_id, method)
                    np.random.seed(method_seed)
                    status = "ok"
                    error_type = ""
                    error_message = ""
                    metrics: Dict[str, Any] = {
                        "metric_T_r2": float("nan"),
                        "metric_T_dtw": float("nan"),
                        "metric_S_spectral_corr": float("nan"),
                        "metric_S_maxlag_corr": float("nan"),
                        "metric_S_r2": float("nan"),
                    }
                    method_cfg: Dict[str, Any] = {}
                    periods_used: List[int] = []
                    try:
                        method_cfg, periods_used = build_method_config(
                            method, scenario_periods, length
                        )
                        meta = _method_meta_from_periods(periods_used)
                        result = _decompose_series(
                            np.asarray(series["y"], dtype=float),
                            method=method,
                            config=method_cfg,
                            fs=fs,
                            meta=meta,
                        )
                        metrics = compute_leaderboard_metrics(
                            true_trend,
                            np.asarray(result.trend, dtype=float),
                            true_season,
                            np.asarray(result.season, dtype=float),
                            fs=fs,
                        )
                    except Exception as exc:
                        status = "error"
                        error_type = exc.__class__.__name__
                        error_message = _truncate(str(exc))

                    record = {
                        "suite_version": BENCHMARK_VERSION,
                        "suite": suite,
                        "package_version": package_version,
                        "git_commit": git_commit,
                        "scenario_id": scenario_id,
                        "scenario_tier": tier,
                        "seed": int(seed),
                        "draw_id": int(draw_id),
                        "length": int(length),
                        "dt": float(dt),
                        "method": method,
                        "status": status,
                        "error_type": error_type,
                        "error_message": error_message,
                        "scenario_periods_json": _safe_json_dumps(periods_used),
                        "method_config_json": _safe_json_dumps(method_cfg),
                    }
                    record.update(metrics)
                    records.append(record)

    df = pd.DataFrame.from_records(records)
    if not df.empty:
        df = df.sort_values(
            ["scenario_id", "seed", "draw_id", "method"], kind="mergesort"
        ).reset_index(drop=True)
    return df


def export_leaderboard_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    for col in LEADERBOARD_COLUMNS:
        if col not in out.columns:
            out[col] = np.nan
    out = out[LEADERBOARD_COLUMNS]
    out.to_csv(path, index=False)


def aggregate_by_scenario(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    metrics = [c for c in df.columns if c.startswith("metric_")]
    df = df.copy()
    df["is_ok"] = df["status"] == "ok"
    group_cols = ["scenario_id", "method"]
    summary = df.groupby(group_cols)[metrics].mean().reset_index()
    std = df.groupby(group_cols)[metrics].std().reset_index()
    coverage = df.groupby(group_cols)["is_ok"].mean().reset_index(name="coverage")
    summary = summary.merge(std, on=group_cols, suffixes=("_mean", "_std"))
    summary = summary.merge(coverage, on=group_cols)
    summary["scenario_tier"] = summary["scenario_id"].map(SCENARIO_TIER)
    return summary


def aggregate_by_tier(scenario_summary: pd.DataFrame) -> pd.DataFrame:
    if scenario_summary.empty:
        return scenario_summary
    metric_mean_cols = [c for c in scenario_summary.columns if c.endswith("_mean")]
    metric_std_cols = [c for c in scenario_summary.columns if c.endswith("_std")]
    group_cols = ["scenario_tier", "method"]
    means = (
        scenario_summary.groupby(group_cols)[metric_mean_cols]
        .mean()
        .reset_index()
    )
    stds = (
        scenario_summary.groupby(group_cols)[metric_mean_cols]
        .std()
        .reset_index()
    )
    stds = stds.rename(
        columns={col: col.replace("_mean", "_std") for col in metric_mean_cols}
    )
    coverage = (
        scenario_summary.groupby(group_cols)["coverage"]
        .mean()
        .reset_index()
    )
    merged = means.merge(stds, on=group_cols).merge(coverage, on=group_cols)
    return merged


def aggregate_overall(tier_summary: pd.DataFrame) -> pd.DataFrame:
    if tier_summary.empty:
        return tier_summary
    metric_cols = [c for c in tier_summary.columns if c.endswith("_mean")]
    group_cols = ["method"]
    means = tier_summary.groupby(group_cols)[metric_cols].mean().reset_index()
    coverage = tier_summary.groupby(group_cols)["coverage"].mean().reset_index()
    merged = means.merge(coverage, on=group_cols)
    return merged


def plot_heatmaps(
    scenario_summary: pd.DataFrame,
    out_dir: Path,
) -> None:
    if scenario_summary.empty:
        return
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = [
        ("metric_T_r2_mean", "heatmap_T_r2.png", "Trend R2 (higher is better)"),
        ("metric_T_dtw_mean", "heatmap_T_dtw.png", "Trend DTW (lower is better)"),
        (
            "metric_S_spectral_corr_mean",
            "heatmap_S_spectral.png",
            "Seasonal spectral corr",
        ),
        (
            "metric_S_maxlag_corr_mean",
            "heatmap_S_maxlag.png",
            "Seasonal max-lag corr",
        ),
    ]

    for metric, filename, title in metrics:
        if metric not in scenario_summary.columns:
            continue
        pivot = scenario_summary.pivot_table(
            index="scenario_id", columns="method", values=metric
        )
        data = pivot.values.astype(float)
        fig, ax = plt.subplots(
            figsize=(max(6, data.shape[1] * 0.8), max(4, data.shape[0] * 0.6))
        )
        im = ax.imshow(data, aspect="auto", interpolation="nearest")
        ax.set_xticks(np.arange(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
        ax.set_yticks(np.arange(pivot.shape[0]))
        ax.set_yticklabels(pivot.index)
        ax.set_title(title)
        fig.colorbar(im, ax=ax, shrink=0.8)
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=150)
        plt.close(fig)


def run_leaderboard(
    suite: str = "core",
    methods: str | Sequence[str] = "core",
    seeds: str | Sequence[int] = "0",
    n_samples: int = 50,
    length: int = 512,
    dt: float = 1.0,
    out_dir: str | Path = "artifacts/tscomp_v1_core",
    export_format: str = "leaderboard_csv",
    aggregate: bool = False,
    plots: bool = False,
) -> pd.DataFrame:
    method_list = resolve_methods(methods)
    seed_list = parse_seeds(seeds)
    validate_runbook(suite, method_list, length, dt)

    out_root = Path(out_dir)
    raw_dir = out_root / "raw"
    summary_dir = out_root / "summary"
    figures_dir = out_root / "figures"
    logs_dir = out_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    df = run_benchmark(
        suite=suite,
        methods=method_list,
        seeds=seed_list,
        n_samples=n_samples,
        length=length,
        dt=dt,
    )

    package_version = _package_version()
    git_commit = _git_commit()
    write_env_artifacts(out_root, package_version, git_commit)

    if export_format == "leaderboard_csv":
        raw_name = f"leaderboard_{suite}_official_raw.csv"
        raw_path = raw_dir / raw_name
        export_leaderboard_csv(df, raw_path)
        export_leaderboard_csv(df, out_root / "leaderboard.csv")

    if aggregate:
        summary_dir.mkdir(parents=True, exist_ok=True)
        scenario_summary = aggregate_by_scenario(df)
        scenario_summary.to_csv(
            summary_dir / f"{suite}_by_scenario.csv", index=False
        )
        tier_summary = aggregate_by_tier(scenario_summary)
        tier_summary.to_csv(summary_dir / f"{suite}_by_tier.csv", index=False)
        overall = aggregate_overall(tier_summary)
        overall.to_csv(summary_dir / f"{suite}_overall.csv", index=False)
        if plots:
            figures_dir.mkdir(parents=True, exist_ok=True)
            plot_heatmaps(scenario_summary, figures_dir)
    elif plots:
        scenario_summary = aggregate_by_scenario(df)
        figures_dir.mkdir(parents=True, exist_ok=True)
        plot_heatmaps(scenario_summary, figures_dir)

    if not df.empty:
        errors = df[df["status"] == "error"]
        if not errors.empty:
            error_path = logs_dir / "errors.jsonl"
            with error_path.open("w", encoding="utf-8") as f:
                for _, row in errors.iterrows():
                    payload = {
                        "scenario_id": row["scenario_id"],
                        "method": row["method"],
                        "seed": int(row["seed"]),
                        "draw_id": int(row["draw_id"]),
                        "error_type": row["error_type"],
                        "error_message": row["error_message"],
                    }
                    f.write(_safe_json_dumps(payload) + "\n")
    log_path = logs_dir / "run.log"
    total_rows = int(df.shape[0]) if not df.empty else 0
    error_rows = int((df["status"] == "error").sum()) if not df.empty else 0
    log_lines = [
        f"suite={suite}",
        f"methods={','.join(method_list)}",
        f"seeds={','.join(str(s) for s in seed_list)}",
        f"n_samples={n_samples}",
        f"length={length}",
        f"dt={dt}",
        f"rows={total_rows}",
        f"errors={error_rows}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return df


def merge_results(
    input_dirs: Sequence[str | Path],
    out_dir: str | Path,
    export_format: str = "leaderboard_csv",
    aggregate: bool = True,
    plots: bool = True,
) -> pd.DataFrame:
    """Merge leaderboard results from multiple run directories."""
    dfs = []
    for d in input_dirs:
        path = Path(d)
        # Try raw first, then root leaderboard.csv
        raw_csv = path / "raw" / f"leaderboard_csv_official_raw.csv"  # heuristic pattern
        # Actually standard name is leaderboard_{suite}_official_raw.csv or just leaderboard.csv
        # Let's search for *raw.csv in raw/ or leaderboard.csv in root
        candidates = list((path / "raw").glob("*_raw.csv"))
        if not candidates:
            candidates = [path / "leaderboard.csv"]
        
        found = False
        for c in candidates:
            if c.exists():
                try:
                    df_part = pd.read_csv(c)
                    dfs.append(df_part)
                    found = True
                    break
                except Exception:
                    pass
        if not found:
            print(f"Warning: No valid leaderboard csv found in {d}")

    if not dfs:
        raise ValueError("No results found to merge.")

    df = pd.concat(dfs, ignore_index=True)
    # Deduplicate if overlapping seeds/methods
    subset_cols = ["scenario_id", "seed", "draw_id", "method"]
    df = df.drop_duplicates(subset=subset_cols, keep="last")
    
    out_root = Path(out_dir)
    raw_dir = out_root / "raw"
    summary_dir = out_root / "summary"
    figures_dir = out_root / "figures"
    logs_dir = out_root / "logs"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if export_format == "leaderboard_csv":
        export_leaderboard_csv(df, out_root / "leaderboard.csv")
        # Try to infer suite from first record or default to 'merged'
        suite = df["suite"].iloc[0] if "suite" in df.columns else "core"
        export_leaderboard_csv(df, raw_dir / f"leaderboard_{suite}_merged_raw.csv")

    if aggregate:
        suite = df["suite"].iloc[0] if "suite" in df.columns else "core"
        scenario_summary = aggregate_by_scenario(df)
        scenario_summary.to_csv(
            summary_dir / f"{suite}_by_scenario.csv", index=False
        )
        tier_summary = aggregate_by_tier(scenario_summary)
        tier_summary.to_csv(summary_dir / f"{suite}_by_tier.csv", index=False)
        overall = aggregate_overall(tier_summary)
        overall.to_csv(summary_dir / f"{suite}_overall.csv", index=False)
        if plots:
            plot_heatmaps(scenario_summary, figures_dir)
            
    return df
