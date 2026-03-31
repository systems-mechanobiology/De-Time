from __future__ import annotations

import importlib
import runpy
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd

from tsdecomp import DecompResult
from tsdecomp import bench_config
from tsdecomp import metrics
from tsdecomp import viz


def test_bench_config_helpers() -> None:
    assert bench_config.list_suites() == ["core", "full"]
    assert bench_config.get_suite("core")
    assert bench_config.resolve_methods("core") == bench_config.CORE_METHODS
    assert bench_config.resolve_methods("stl,ssa") == ["stl", "ssa"]
    assert bench_config.normalize_periods([12, 12, "24", 1], length=100) == [12, 24, 2]
    assert bench_config.select_primary_period([None, 24, 12]) == 24


def test_metrics_module() -> None:
    x = np.linspace(0.0, 1.0, 32)
    y = x + 0.1

    vals = metrics.compute_metrics(x, y, fs=1.0)
    assert set(vals) == {"r2", "dtw", "spec_corr", "max_lag_corr"}
    assert np.isfinite(vals["dtw"])
    assert np.isfinite(metrics.spectral_correlation(x, y))
    assert np.isfinite(metrics.max_lag_correlation(x, y))


def test_viz_plot_helpers(monkeypatch, tmp_path) -> None:
    saved = []

    class FakeAxis:
        def plot(self, *args, **kwargs):
            return None

        def set_ylabel(self, *args, **kwargs):
            return None

        def legend(self, *args, **kwargs):
            return None

        def grid(self, *args, **kwargs):
            return None

        def set_xlabel(self, *args, **kwargs):
            return None

        def set_title(self, *args, **kwargs):
            return None

        def set_xticks(self, *args, **kwargs):
            return None

        def set_xticklabels(self, *args, **kwargs):
            return None

        def set_yticks(self, *args, **kwargs):
            return None

        def set_yticklabels(self, *args, **kwargs):
            return None

        def imshow(self, *args, **kwargs):
            return np.zeros((1, 1))

    class FakeFigure:
        def suptitle(self, *args, **kwargs):
            return None

        def colorbar(self, *args, **kwargs):
            return None

        def tight_layout(self):
            return None

        def savefig(self, path, dpi=150):
            saved.append(Path(path))

    class FakePyplot:
        @staticmethod
        def subplots(nrows=1, ncols=1, **kwargs):
            fig = FakeFigure()
            count = nrows * ncols
            if count == 1:
                return fig, FakeAxis()
            return fig, [FakeAxis() for _ in range(count)]

        @staticmethod
        def tight_layout():
            return None

        @staticmethod
        def savefig(path, dpi=150):
            saved.append(Path(path))

        @staticmethod
        def close(fig):
            return None

        @staticmethod
        def show():
            return None

    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", FakePyplot)

    result = DecompResult(
        trend=np.ones(8),
        season=np.zeros(8),
        residual=np.zeros(8),
    )
    results = {
        "SSA": result,
        "STD": DecompResult(
            trend=np.full(8, 0.5),
            season=np.full(8, 0.2),
            residual=np.zeros(8),
        ),
    }
    multi_result = DecompResult(
        trend=np.ones((8, 2)),
        season=np.zeros((8, 2)),
        residual=np.zeros((8, 2)),
        meta={"channel_names": ["x0", "x1"]},
    )

    viz.plot_components(result, series=np.ones(8), save_path=tmp_path / "components.png")
    viz.plot_error(result, series=np.ones(8), save_path=tmp_path / "error.png")
    viz.plot_component_overlay(
        results,
        component="trend",
        series=np.ones(8),
        save_path=tmp_path / "trend_overlay.png",
    )
    viz.plot_method_comparison(
        results,
        series=np.ones(8),
        save_path=tmp_path / "comparison.png",
    )
    viz.plot_multivariate_components(
        multi_result,
        series=np.ones((8, 2)),
        save_path=tmp_path / "multivariate.png",
    )

    assert saved


def test_leaderboard_helpers_with_fake_benchmark_backend(monkeypatch, tmp_path) -> None:
    fake_pkg = types.ModuleType("synthetic_ts_bench")
    fake_decomp = types.ModuleType("synthetic_ts_bench.decomp_methods")

    def make_scenario(scenario_id, length, random_seed):
        return types.SimpleNamespace(scenario_id=scenario_id, length=length, random_seed=random_seed, dt=1.0)

    def generate_series(cfg):
        x = np.arange(cfg.length, dtype=float)
        trend = 0.01 * x
        season = np.sin(2.0 * np.pi * x / 12.0)
        return {"y": trend + season, "trend": trend, "season": season, "meta": {"seed": cfg.random_seed}}

    def decompose_series(y, method, config, fs, meta):
        y = np.asarray(y, dtype=float)
        trend = np.full_like(y, np.mean(y))
        season = y - trend
        residual = np.zeros_like(y)
        return types.SimpleNamespace(trend=trend, season=season, residual=residual)

    fake_pkg.make_scenario = make_scenario
    fake_pkg.generate_series = generate_series
    fake_decomp.decompose_series = decompose_series
    monkeypatch.setitem(sys.modules, "synthetic_ts_bench", fake_pkg)
    monkeypatch.setitem(sys.modules, "synthetic_ts_bench.decomp_methods", fake_decomp)

    import tsdecomp.leaderboard as leaderboard

    leaderboard = importlib.reload(leaderboard)

    assert leaderboard.parse_seeds("1:4") == [1, 2, 3]
    assert leaderboard.derive_sample_seed(1, "trend_only_linear", 0) == leaderboard.derive_sample_seed(1, "trend_only_linear", 0)
    metrics_out = leaderboard.compute_leaderboard_metrics(
        np.ones(8),
        np.ones(8),
        np.ones(8),
        np.ones(8),
        fs=1.0,
    )
    assert "metric_T_r2" in metrics_out

    leaderboard.validate_runbook("core", ["stl"], length=32, dt=1.0)
    df = leaderboard.run_benchmark(
        suite="core",
        methods=["stl"],
        seeds=[0],
        n_samples=1,
        length=32,
        dt=1.0,
    )
    assert not df.empty

    csv_path = tmp_path / "leaderboard.csv"
    leaderboard.export_leaderboard_csv(df, csv_path)
    assert csv_path.exists()

    scenario_summary = leaderboard.aggregate_by_scenario(df)
    tier_summary = leaderboard.aggregate_by_tier(scenario_summary)
    overall = leaderboard.aggregate_overall(tier_summary)
    assert not scenario_summary.empty
    assert not tier_summary.empty
    assert not overall.empty

    leaderboard.write_env_artifacts(tmp_path, "0.1.0", "deadbeef")
    assert (tmp_path / "env" / "runtime_env.json").exists()


def test_examples_run(monkeypatch, tmp_path) -> None:
    root = Path(__file__).resolve().parents[1]
    profile_script = root / "examples" / "profile_and_cli.py"

    monkeypatch.chdir(root)
    runpy.run_path(str(profile_script), run_name="__main__")

    assert (root / "examples" / "data" / "example_series.csv").exists()
    assert pd.read_csv(root / "examples" / "data" / "example_multivariate.csv").shape[1] == 2
