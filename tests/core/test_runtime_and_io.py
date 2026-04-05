from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import detime
import detime._native as native_mod
import detime.backends as backends
import detime.io as io_mod
import detime.metrics as metrics
import detime.viz as viz
from detime import DecompResult, DecompositionConfig


def test_detime_public_import_surface() -> None:
    assert detime.DecompositionConfig.__name__ == "DecompositionConfig"
    assert callable(detime.decompose)
    assert isinstance(detime.native_capabilities(), dict)


def test_public_registry_excludes_migrated_benchmark_methods() -> None:
    removed = {"DR_TS_REG", "DR_TS_AE", "SL_LIB"}

    assert removed.isdisjoint(set(detime.MethodRegistry.list_methods()))

    for method in removed:
        with pytest.raises(ValueError, match="de-time-bench"):
            detime.MethodRegistry.get_spec(method)


def test_native_helpers_and_backend_resolution(monkeypatch) -> None:
    fake_module = SimpleNamespace(
        ssa_decompose=lambda y: y,
        std_decompose=lambda y: y,
        capabilities=lambda: {"ssa_decompose": True, "std_decompose": True},
        ping=lambda value: value + 1,
    )
    monkeypatch.setattr(native_mod, "_MODULE", fake_module)
    monkeypatch.setattr(native_mod, "_IMPORT_ERROR", None)

    assert native_mod.native_extension_available() is True
    assert native_mod.native_capabilities()["ssa_decompose"] is True
    assert native_mod.has_native_method("std_decompose") is True
    assert native_mod.invoke_native("ping", 1) == 2

    runtime = backends.RuntimeOptions(backend="auto", speed_mode="exact")
    assert backends.resolve_backend("SSA", runtime, native_methods=("ssa_decompose",)) == "native"

    tuple_result = backends.result_from_native_payload((np.ones(3), np.zeros(3), np.zeros(3)), method="X")
    assert tuple_result.meta["method"] == "X"

    mapping_result = backends.result_from_native_payload(
        {"trend": [1, 2], "season": [0, 0], "residual": [0, 0], "components": {"x": [1, 2]}},
        method="Y",
    )
    assert np.asarray(mapping_result.components["x"]).shape == (2,)

    with pytest.raises(ValueError):
        backends.runtime_options_from_config(
            DecompositionConfig(method="SSA", params={}, backend="bad")
        )


def test_native_invoke_errors_when_module_missing(monkeypatch) -> None:
    monkeypatch.setattr(native_mod, "_MODULE", None)
    monkeypatch.setattr(native_mod, "_IMPORT_ERROR", RuntimeError("missing native"))
    assert native_mod.native_capabilities() == {}
    assert isinstance(native_mod.native_import_error(), RuntimeError)
    with pytest.raises(RuntimeError, match="Native extension is not available"):
        native_mod.invoke_native("ssa_decompose", np.arange(3.0))


def test_native_helpers_cover_fallback_capabilities_and_missing_exports(monkeypatch) -> None:
    fake_module = SimpleNamespace(ssa_decompose=lambda y: y)
    monkeypatch.setattr(native_mod, "_MODULE", fake_module)
    monkeypatch.setattr(native_mod, "_IMPORT_ERROR", None)

    caps = native_mod.native_capabilities()
    assert caps["ssa_decompose"] is True
    assert caps["std_decompose"] is False
    assert native_mod.native_import_error() is None

    with pytest.raises(AttributeError, match="does not export"):
        native_mod.invoke_native("std_decompose", np.arange(3.0))


def test_backend_runtime_helpers_cover_legacy_keys_and_profile_metadata(monkeypatch) -> None:
    cfg, runtime = backends.split_runtime_params(
        {
            "alpha": 1,
            backends.LEGACY_RUNTIME_KEY: {
                "backend": "python",
                "speed_mode": "fast",
                "profile": True,
                "device": "cuda",
                "n_jobs": 3,
                "seed": 7,
            },
        }
    )
    assert cfg == {"alpha": 1}
    assert runtime.backend == "python"
    assert runtime.speed_mode == "fast"
    assert runtime.profile is True
    assert runtime.device == "cuda"
    assert runtime.n_jobs == 3
    assert runtime.seed == 7

    with pytest.raises(ValueError, match="Unsupported speed_mode"):
        backends._normalize_speed_mode("warp")

    with pytest.raises(ValueError, match="GPU backend"):
        backends.resolve_backend("SSA", backends.RuntimeOptions(backend="gpu"))

    monkeypatch.setattr(backends, "native_extension_available", lambda: True)
    monkeypatch.setattr(backends, "has_native_method", lambda name: True)
    monkeypatch.setattr(backends, "native_import_error", lambda: None)
    assert (
        backends.resolve_backend(
            "SSA",
            backends.RuntimeOptions(backend="native"),
            native_methods=("ssa_decompose",),
        )
        == "native"
    )

    native_payload = {
        "trend": [1, 1],
        "season": [0, 0],
        "residual": [0, 0],
        "meta": {"method": "OTHER"},
    }
    converted = backends.result_from_native_payload(native_payload, method="SSA")
    assert converted.meta["method"] == "SSA"
    assert converted.meta["native_method"] == "OTHER"

    existing = DecompResult(trend=np.zeros(2), season=np.zeros(2), residual=np.zeros(2))
    assert backends.result_from_native_payload(existing, method="SSA") is existing

    with pytest.raises(TypeError, match="Unsupported native payload"):
        backends.result_from_native_payload(object(), method="SSA")

    profiled = backends.finalize_result(
        DecompResult(trend=np.zeros(2), season=np.zeros(2), residual=np.zeros(2)),
        method="SSA",
        runtime=backends.RuntimeOptions(backend="python", profile=True),
        backend_used="python",
        started_at=time.perf_counter() - 0.01,
    )
    assert profiled.meta["backend_requested"] == "python"
    assert profiled.meta["backend_used"] == "python"
    assert profiled.meta["speed_mode"] == "exact"
    assert profiled.meta["runtime_ms"] >= 0.0


def test_io_helpers_cover_edge_cases(tmp_path) -> None:
    assert io_mod._normalize_cols("a, b, ,c") == ["a", "b", "c"]
    assert io_mod._normalize_cols([" a ", "b", ""]) == ["a", "b"]
    assert io_mod._default_channel_names({}, 2) == ["ch0", "ch1"]

    csv_path = tmp_path / "frame.csv"
    pd.DataFrame({"label": ["x", "y"], "value": [1.0, 2.0]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="either 'col' or 'cols'"):
        io_mod.read_series(csv_path, col="value", cols="value")
    with pytest.raises(ValueError, match="Column 'missing'"):
        io_mod.read_series(csv_path, col="missing")

    arr, info = io_mod.read_series(csv_path, return_info=True)
    assert arr.shape == (2,)
    assert info["channel_names"] == ["value"]

    df = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})
    multi_path = tmp_path / "panel.csv"
    df.to_csv(multi_path, index=False)
    arr2, info2 = io_mod.read_series(multi_path, method="MSSA", return_info=True)
    assert arr2.shape == (2, 2)
    assert info2["multivariate"] is True

    with pytest.raises(ValueError, match="Unsupported file format"):
        io_mod._load_frame(tmp_path / "bad.txt")

    with pytest.raises(ValueError, match="must be 1D or 2D"):
        io_mod._flatten_component("bad", np.zeros((2, 2, 2)), ["a", "b"])

    bad_result = DecompResult(
        trend=np.zeros((4, 2)),
        season=np.zeros((4, 2)),
        residual=np.zeros((4, 2)),
        components={"bad": np.zeros((2, 2, 2, 2))},
    )
    with pytest.raises(ValueError, match="Unsupported component shape"):
        io_mod.save_result(bad_result, tmp_path / "out", "bad")


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


def test_benchmark_modules_raise_import_error() -> None:
    with pytest.raises(ImportError, match="de-time-bench"):
        importlib.import_module("detime.bench_config")
    with pytest.raises(ImportError, match="de-time-bench"):
        importlib.import_module("detime.leaderboard")
