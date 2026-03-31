"""Evaluation utilities for decomposition benchmarks."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .decomp_methods import (
    DecompConfig,
    DecompMethodName,
    decompose_series,
)
from .scenarios import generate_dataset


def _safe_pearson(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute Pearson correlation between x and y with basic safety checks.
    """

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
    cov = np.mean(x_c * y_c)
    return float(cov / np.sqrt(vx * vy))


def _safe_spearman(x: np.ndarray, y: np.ndarray) -> float:
    """
    Spearman rank correlation implemented via ranking + Pearson.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.size == 0:
        return float("nan")

    def _rankdata(arr: np.ndarray) -> np.ndarray:
        n = arr.size
        order = np.argsort(arr, kind="mergesort")
        ranks = np.empty(n, dtype=float)
        ranks[order] = np.arange(1, n + 1)
        sorted_vals = arr[order]
        i = 0
        while i < n:
            j = i + 1
            while j < n and sorted_vals[j] == sorted_vals[i]:
                j += 1
            if j - i > 1:
                avg_rank = np.mean(ranks[order[i:j]])
                ranks[order[i:j]] = avg_rank
            i = j
        return ranks

    rx = _rankdata(x)
    ry = _rankdata(y)
    return _safe_pearson(rx, ry)


def _max_lag_corr(x: np.ndarray, y: np.ndarray, max_lag: int = 10) -> float:
    """
    Maximum Pearson correlation over lags in [-max_lag, max_lag].
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size == 0 or y.size == 0:
        return float("nan")

    n = min(x.size, y.size)
    x = x[:n]
    y = y[:n]
    if n <= 2:
        return float("nan")

    best = -np.inf
    for lag in range(-max_lag, max_lag + 1):
        if lag == 0:
            xc, yc = x, y
        elif lag > 0:
            xc = x[lag:]
            yc = y[:-lag]
        else:
            k = -lag
            xc = x[:-k]
            yc = y[k:]
        if xc.size < 3:
            continue
        r = _safe_pearson(xc, yc)
        if not np.isnan(r) and r > best:
            best = r
    return float(best if best != -np.inf else np.nan)


def _dtw_distance(x: np.ndarray, y: np.ndarray) -> float:
    """
    Simple DTW distance (Euclidean cost) with O(T^2) DP.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n, m = x.size, y.size
    if n == 0 or m == 0:
        return float("nan")

    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = (x[i - 1] - y[j - 1]) ** 2
            D[i, j] = cost + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])

    return float(np.sqrt(D[n, m]))


def compute_time_domain_metrics(
    true: np.ndarray,
    est: np.ndarray,
    prefix: str = "T",
    max_lag: int = 10,
) -> Dict[str, float]:
    """
    Compute error, bias, correlation, and DTW-style metrics for a component.
    """

    true_arr = np.asarray(true, dtype=float).reshape(-1)
    est_arr = np.asarray(est, dtype=float).reshape(-1)
    metrics: Dict[str, float] = {}

    keys = [
        f"{prefix}_rmse",
        f"{prefix}_mae",
        f"{prefix}_bias",
        f"{prefix}_r2",
        f"{prefix}_pearson",
        f"{prefix}_spearman",
        f"{prefix}_maxlag_corr",
        f"{prefix}_dtw",
    ]

    if true_arr.shape != est_arr.shape or true_arr.size == 0:
        for key in keys:
            metrics[key] = float("nan")
        return metrics

    diff = est_arr - true_arr
    rmse = float(np.sqrt(np.mean(diff**2)))
    mae = float(np.mean(np.abs(diff)))
    bias = float(np.mean(diff))

    centered_true = true_arr - np.mean(true_arr)
    sse = float(np.sum(diff**2))
    sst = float(np.sum(centered_true**2))
    r2 = float(1.0 - sse / sst) if sst > 1e-12 else float("nan")

    pearson = _safe_pearson(true_arr, est_arr)
    spearman = _safe_spearman(true_arr, est_arr)
    maxlag_corr = _max_lag_corr(true_arr, est_arr, max_lag=max_lag)
    dtw = _dtw_distance(true_arr, est_arr)

    metrics[f"{prefix}_rmse"] = rmse
    metrics[f"{prefix}_mae"] = mae
    metrics[f"{prefix}_bias"] = bias
    metrics[f"{prefix}_r2"] = r2
    metrics[f"{prefix}_pearson"] = pearson
    metrics[f"{prefix}_spearman"] = spearman
    metrics[f"{prefix}_maxlag_corr"] = maxlag_corr
    metrics[f"{prefix}_dtw"] = dtw

    return metrics


def compute_freq_metrics(
    true: np.ndarray,
    est: np.ndarray,
    fs: float = 1.0,
    prefix: str = "S",
    n_peaks: int = 1,
) -> Dict[str, float]:
    """
    Compare dominant frequencies in the power spectra of true and estimated components.
    """

    true_arr = np.asarray(true, dtype=float).reshape(-1)
    est_arr = np.asarray(est, dtype=float).reshape(-1)

    metrics = {
        f"{prefix}_dom_freq_true": float("nan"),
        f"{prefix}_dom_freq_est": float("nan"),
        f"{prefix}_dom_freq_abs_err": float("nan"),
        f"{prefix}_spectral_corr": float("nan"),
    }

    if true_arr.shape != est_arr.shape or true_arr.size < 2:
        return metrics

    sample_spacing = 1.0 / fs if fs > 0 else 1.0
    n = true_arr.size
    freqs = np.fft.rfftfreq(n, d=sample_spacing)

    fft_true = np.fft.rfft(true_arr - true_arr.mean())
    fft_est = np.fft.rfft(est_arr - est_arr.mean())
    mag_true = np.abs(fft_true)
    mag_est = np.abs(fft_est)

    if mag_true.size <= 1 or mag_est.size <= 1:
        return metrics

    mag_true_no_dc = mag_true.copy()
    mag_est_no_dc = mag_est.copy()
    mag_true_no_dc[0] = 0.0
    mag_est_no_dc[0] = 0.0

    idx_true = int(np.argmax(mag_true_no_dc))
    idx_est = int(np.argmax(mag_est_no_dc))
    dom_true = float(freqs[idx_true])
    dom_est = float(freqs[idx_est])
    dom_err = float(abs(dom_true - dom_est))

    spectral_corr = _safe_pearson(mag_true_no_dc[1:], mag_est_no_dc[1:])

    metrics[f"{prefix}_dom_freq_true"] = dom_true
    metrics[f"{prefix}_dom_freq_est"] = dom_est
    metrics[f"{prefix}_dom_freq_abs_err"] = dom_err
    metrics[f"{prefix}_spectral_corr"] = spectral_corr
    return metrics


def compute_event_metrics(
    true_events: np.ndarray,
    est_residual: np.ndarray,
    threshold: float = 2.0,
) -> Dict[str, float]:
    """
    Approximate event detection metrics using residual thresholding.
    """

    true_events = np.asarray(true_events, dtype=float).reshape(-1)
    est_residual = np.asarray(est_residual, dtype=float).reshape(-1)
    if true_events.shape != est_residual.shape:
        raise ValueError("Event and residual arrays must align.")

    eps = 1e-8
    true_mask = np.abs(true_events) > eps
    resid_std = np.std(est_residual)
    if resid_std <= 1e-12:
        pred_mask = np.zeros_like(true_mask, dtype=bool)
    else:
        thresh = threshold * resid_std
        pred_mask = np.abs(est_residual) > thresh

    tp = int(np.logical_and(true_mask, pred_mask).sum())
    fp = int(np.logical_and(~true_mask, pred_mask).sum())
    fn = int(np.logical_and(true_mask, ~pred_mask).sum())

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return {
        "event_precision": float(precision),
        "event_recall": float(recall),
        "event_f1": float(f1),
    }


def evaluate_decomposition_on_series(
    true_series: Dict[str, Any],
    method: DecompMethodName,
    method_config: Optional[DecompConfig] = None,
    fs: float = 1.0,
) -> Dict[str, Any]:
    """
    Evaluate one decomposition method on one synthetic series with known ground truth.
    """

    y = np.asarray(true_series["y"], dtype=float).reshape(-1)
    result = decompose_series(
        y,
        method=method,
        config=method_config,
        fs=fs,
        meta=true_series.get("meta", {}),
    )

    metrics: Dict[str, Any] = {
        "method": method,
        "length": len(y),
        "fs": fs,
        "method_config": dict(method_config or {}),
        "residual_std": float(np.std(result.residual)),
    }

    meta = true_series.get("meta", {})
    metrics["scenario_name"] = meta.get("scenario_name", "")
    metrics["global_seed"] = meta.get("global_seed")
    metrics["index_within_scenario"] = meta.get("index_within_scenario")

    if "trend" in true_series:
        metrics.update(
            compute_time_domain_metrics(true_series["trend"], result.trend, prefix="T")
        )
    if "season" in true_series:
        season_true = true_series["season"]
        metrics.update(
            compute_time_domain_metrics(season_true, result.season, prefix="S")
        )
        metrics.update(
            compute_freq_metrics(season_true, result.season, fs=fs, prefix="S")
        )

    if "events" in true_series and np.any(np.abs(true_series["events"]) > 1e-8):
        metrics.update(
            compute_event_metrics(true_series["events"], result.residual)
        )

    return metrics


def evaluate_methods_on_scenarios(
    scenario_names: List[str],
    methods: List[Tuple[DecompMethodName, Optional[DecompConfig]]],
    n_per_scenario: int = 50,
    length: int = 512,
    base_seed: int = 0,
    fs: float = 1.0,
) -> pd.DataFrame:
    """
    Generate synthetic data for scenarios, run methods, and aggregate metrics.
    """

    dataset = generate_dataset(
        scenario_names=scenario_names,
        n_per_scenario=n_per_scenario,
        length=length,
        base_seed=base_seed,
        save_dir=None,
    )

    records: List[Dict[str, Any]] = []
    for series_idx, series in enumerate(dataset):
        scenario_name = series.get("meta", {}).get("scenario_name", "")
        sample_idx = series.get("meta", {}).get("index_within_scenario", series_idx)

        for method_name, method_cfg in methods:
            metrics = evaluate_decomposition_on_series(
                true_series=series,
                method=method_name,
                method_config=method_cfg,
                fs=fs,
            )
            metrics["method"] = method_name
            metrics["sample_index"] = sample_idx
            metrics.setdefault("scenario_name", scenario_name)
            metrics.setdefault("global_seed", series.get("meta", {}).get("global_seed"))
            metrics["series_idx"] = series_idx
            records.append(metrics)

    if not records:
        return pd.DataFrame()
    return pd.DataFrame.from_records(records)
