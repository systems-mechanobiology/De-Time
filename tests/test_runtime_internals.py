from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from tsdecomp import DecompResult, DecompositionConfig
import tsdecomp._native as native_mod
import tsdecomp.backends as backends
import tsdecomp.io as io_mod
import tsdecomp.methods.dr_ts_reg as dr_ts_reg_mod
import tsdecomp.methods.memd as memd_mod
import tsdecomp.methods.mvmd as mvmd_mod
import tsdecomp.methods.std_multi as std_multi_mod
import tsdecomp.methods.utils as utils_mod


def _series(length: int = 72) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)


def _panel(length: int = 72) -> np.ndarray:
    y = _series(length)
    return np.column_stack([y, 0.8 * y + 0.2 * np.cos(2.0 * np.pi * np.arange(length) / 6.0)])


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
    with pytest.raises(RuntimeError, match="Native extension is not available"):
        native_mod.invoke_native("ssa_decompose", np.arange(3.0))


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


def test_utils_helpers() -> None:
    y = _series()
    assert utils_mod.dominant_frequency(y, fs=1.0) > 0.0
    assert utils_mod.ensure_period_list([12, 12.4, "bad"], None, len(y)) == [12]
    assert utils_mod.ensure_period_list(None, None, 50) == [5]

    modes = np.vstack([np.ones(5), 2.0 * np.ones(5)])
    np.testing.assert_allclose(utils_mod.aggregate_modes(modes, [0, 1]), 3.0 * np.ones(5))
    np.testing.assert_allclose(utils_mod.aggregate_modes(modes, []), np.zeros(5))


def test_dr_ts_reg_python_and_native_paths(monkeypatch) -> None:
    y = _series()

    def fake_python_backend(y_arr, config, fs, meta):
        arr = np.asarray(y_arr, dtype=float)
        trend = np.full_like(arr, np.mean(arr))
        season = arr - trend
        residual = np.zeros_like(arr)
        return SimpleNamespace(trend=trend, season=season, residual=residual, extra={"solver": "python_fake"})

    monkeypatch.setattr(
        dr_ts_reg_mod,
        "import_module",
        lambda name: SimpleNamespace(dr_ts_reg_decompose=fake_python_backend),
    )

    py_result = dr_ts_reg_mod.dr_ts_reg_wrapper(
        y,
        backends.inject_runtime_params({"period": 12}, backends.RuntimeOptions(backend="python")),
    )
    assert py_result.meta["solver"] == "python_fake"

    monkeypatch.setattr(dr_ts_reg_mod, "resolve_backend", lambda *args, **kwargs: "native")
    monkeypatch.setattr(
        dr_ts_reg_mod,
        "invoke_native",
        lambda name, *args, **kwargs: {
            "trend": np.full_like(y, np.mean(y)),
            "season": y - np.mean(y),
            "residual": np.zeros_like(y),
            "meta": {"method": "DR_TS_REG_NATIVE"},
        },
    )

    native_result = dr_ts_reg_mod.dr_ts_reg_wrapper(
        y,
        backends.inject_runtime_params({"period": 12}, backends.RuntimeOptions(backend="native")),
    )
    assert native_result.meta["backend_used"] == "native"


def test_mvmd_and_memd_success_paths(monkeypatch) -> None:
    class FakeMVMD:
        def fit_transform(self, x):
            arr = np.asarray(x, dtype=float)
            return np.stack([0.5 * arr, 0.5 * arr], axis=0)

    class FakeMEMD:
        def fit_transform(self, x):
            arr = np.asarray(x, dtype=float)
            return {"imfs": np.stack([0.6 * arr, 0.4 * arr], axis=0)}

    def fake_import(name: str):
        module = ModuleType(name)
        if "MEMD" in name or name.endswith("memd"):
            module.MEMD = FakeMEMD
        if "MVMD" in name or name.endswith("mvmd"):
            module.MVMD = FakeMVMD
        if name in {"pysdkit", "PySDKit"}:
            module.MVMD = FakeMVMD
            module.MEMD = FakeMEMD
        return module

    monkeypatch.setattr(mvmd_mod, "import_module", fake_import)
    y = _panel()

    mvmd_result = mvmd_mod.mvmd_decompose(
        y,
        backends.inject_runtime_params({"primary_period": 12}, backends.RuntimeOptions(backend="python")),
    )
    memd_result = memd_mod.memd_decompose(
        y,
        backends.inject_runtime_params({"primary_period": 12}, backends.RuntimeOptions(backend="python")),
    )

    assert mvmd_result.trend.shape == y.shape
    assert mvmd_result.components["modes"].ndim == 3
    assert memd_result.components["imfs"].ndim == 3


def test_std_multi_falls_back_to_ssa(monkeypatch) -> None:
    y = _series()
    import builtins

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "fasttimes":
            raise ImportError("fasttimes unavailable in tests")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(
        std_multi_mod,
        "ssa_decompose",
        lambda arr, params: DecompResult(
            trend=np.asarray(arr, dtype=float),
            season=np.zeros_like(arr),
            residual=np.zeros_like(arr),
            meta={"method": "SSA_FALLBACK"},
        ),
    )
    result = std_multi_mod.std_multi_decompose(y, {"window": 12})
    assert result.meta["method"] == "SSA_FALLBACK"
