from __future__ import annotations

"""Validation and comparison helpers for tutorial backtests."""

import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

from .backtest import BacktestResult, backtest_weights


def compare_weight_strategies(
    prices: pd.DataFrame,
    weights_by_name: Mapping[str, pd.DataFrame],
    *,
    fee_bps: float = 5.0,
    slippage_bps: float = 2.0,
    periods_per_year: int = 252,
) -> tuple[pd.DataFrame, dict[str, BacktestResult]]:
    results: dict[str, BacktestResult] = {}
    rows: list[dict[str, float | str]] = []
    for name, weights in weights_by_name.items():
        result = backtest_weights(prices, weights, fee_bps=fee_bps, slippage_bps=slippage_bps, periods_per_year=periods_per_year)
        results[str(name)] = result
        row: dict[str, float | str] = {"strategy": str(name)}
        row.update(result.stats)
        rows.append(row)
    table = pd.DataFrame(rows).set_index("strategy").sort_values("sharpe", ascending=False) if rows else pd.DataFrame()
    return table, results


def compare_backtest_results(results: Mapping[str, BacktestResult]) -> pd.DataFrame:
    rows = []
    for name, result in results.items():
        row = dict(result.stats)
        row["strategy"] = str(name)
        rows.append(row)
    return pd.DataFrame(rows).set_index("strategy") if rows else pd.DataFrame()


def signal_alignment_audit(prices: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [{
            "index_match": bool(weights.index.equals(prices.index)),
            "columns_match": bool(list(weights.columns) == list(prices.columns)),
            "has_nonfinite_weight": bool(~np.isfinite(weights.to_numpy(dtype=float)).all()),
            "first_price_date": prices.index.min(),
            "last_price_date": prices.index.max(),
        }]
    )


def turnover_report(weights_by_name: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, weights in weights_by_name.items():
        turnover = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1))
        rows.append({"strategy": str(name), "average_turnover": float(turnover.mean()), "median_turnover": float(turnover.median()), "max_turnover": float(turnover.max()), "average_gross_exposure": float(weights.abs().sum(axis=1).mean())})
    return pd.DataFrame(rows).set_index("strategy") if rows else pd.DataFrame()


def write_run_manifest(output_path: str | Path, *, command: str, dataset: str, strategies: list[str], status: str = "completed", failure_reason: str | None = None, result_file: str | None = None) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": f"quant_tutorial_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "dataset": dataset,
        "strategies": strategies,
        "status": status,
        "failure_reason": failure_reason,
        "result_file": result_file,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def write_run_audit(
    report_dir: str | Path,
    *,
    data_manifest: pd.DataFrame,
    audit: pd.DataFrame,
    strategy_stats: pd.DataFrame,
    prefix: str = "column_01_02",
) -> dict[str, Path]:
    out = Path(report_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "manifest": out / f"{prefix}_market_data_manifest.csv",
        "data_audit": out / f"{prefix}_data_audit.csv",
        "strategy_stats": out / f"{prefix}_strategy_stats.csv",
        "run_manifest": out / f"{prefix}_run_manifest.json",
    }
    data_manifest.to_csv(paths["manifest"], index=False)
    audit.to_csv(paths["data_audit"], index=False)
    strategy_stats.to_csv(paths["strategy_stats"])
    write_run_manifest(paths["run_manifest"], command="python examples/quant_trading/scripts/run_columns_01_02.py", dataset="market_ohlcv", strategies=list(strategy_stats.index), result_file=str(paths["strategy_stats"]))
    return paths


def train_test_date_split(index: pd.Index, *, test_fraction: float = 0.35) -> tuple[pd.Timestamp, pd.Timestamp]:
    split_loc = int(len(index) * (1.0 - float(test_fraction)))
    split_loc = min(max(split_loc, 1), len(index) - 1)
    return pd.Timestamp(index[0]), pd.Timestamp(index[split_loc])


def subset_after(prices: pd.DataFrame, weights: pd.DataFrame, split_date: str | pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    split = pd.Timestamp(split_date)
    return prices.loc[prices.index >= split], weights.loc[weights.index >= split]


def benchmark_status(**kwargs) -> dict[str, object]:
    payload = {k: int(v) if isinstance(v, (int, np.integer)) else v for k, v in kwargs.items()}
    payload["safe_for_primary_claims"] = all(str(k).endswith("completed") or v for k, v in payload.items())
    return payload


def audit_backtest_inputs(prices: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    """Pass/fail table for common price/weight alignment issues."""

    finite = bool(np.isfinite(weights.fillna(0.0).to_numpy(dtype=float)).all())
    gross = weights.abs().sum(axis=1).replace([np.inf, -np.inf], np.nan)
    return pd.DataFrame(
        [
            {"check": "index_match", "passed": bool(weights.index.equals(prices.index)), "detail": "weights and prices share the same index"},
            {"check": "columns_match", "passed": bool(list(weights.columns) == list(prices.columns)), "detail": "weights and prices share the same columns"},
            {"check": "finite_weights", "passed": finite, "detail": "weights contain only finite values"},
            {"check": "gross_exposure_reasonable", "passed": bool(gross.max(skipna=True) <= 3.0), "detail": f"max gross exposure={float(gross.max(skipna=True)):.3f}"},
        ]
    )


def train_validation_test_split(frame: pd.DataFrame, *, train_end: str, validation_end: str) -> dict[str, pd.DataFrame]:
    train_end_ts = pd.Timestamp(train_end)
    validation_end_ts = pd.Timestamp(validation_end)
    return {
        "train": frame.loc[frame.index < train_end_ts],
        "validation": frame.loc[(frame.index >= train_end_ts) & (frame.index < validation_end_ts)],
        "test": frame.loc[frame.index >= validation_end_ts],
    }


def write_run_audit(
    report_dir: str | Path,
    *,
    data_manifest: pd.DataFrame | None = None,
    audit: pd.DataFrame | None = None,
    strategy_stats: pd.DataFrame | None = None,
    prefix: str = "column_01_02",
) -> dict[str, Path]:
    """Persist whatever audit tables are available for a notebook or script run."""

    out = Path(report_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    if data_manifest is not None:
        paths["manifest"] = out / f"{prefix}_market_data_manifest.csv"
        data_manifest.to_csv(paths["manifest"], index=False)
    if audit is not None:
        paths["data_audit"] = out / f"{prefix}_data_audit.csv"
        audit.to_csv(paths["data_audit"], index=False)
    if strategy_stats is not None:
        paths["strategy_stats"] = out / f"{prefix}_strategy_stats.csv"
        strategy_stats.to_csv(paths["strategy_stats"])
        paths["run_manifest"] = out / f"{prefix}_run_manifest.json"
        write_run_manifest(
            paths["run_manifest"],
            command="python examples/quant_trading/scripts/run_columns_01_02.py",
            dataset="market_ohlcv",
            strategies=list(strategy_stats.index),
            result_file=str(paths["strategy_stats"]),
        )
    return paths
