from __future__ import annotations

import sys
import builtins
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

from tsdecomp import DecompResult
from tsdecomp.methods import (
    ceemdan,
    dr_ts_ae,
    dr_ts_reg,
    emd,
    gabor_cluster,
    ma_baseline,
    sl_lib,
    ssa,
    std_multi,
    stl,
    vmd,
    wavelet,
)


def test_ma_baseline_decompose() -> None:
    y = np.arange(20, dtype=float)
    result = ma_baseline.ma_decompose(y, {"trend_window": 5, "season_period": 4})
    assert result.trend.shape == y.shape
    assert result.season.shape == y.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, y)


def test_stl_family_with_fake_statsmodels(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSTL:
        def __init__(self, y, period, **kwargs):
            self.y = np.asarray(y, dtype=float)
            self.period = period
            self.kwargs = kwargs

        def fit(self):
            return SimpleNamespace(
                trend=np.full_like(self.y, 1.0),
                seasonal=np.full_like(self.y, 2.0),
                resid=self.y - 3.0,
            )

    class FakeMSTL:
        def __init__(self, y, periods, **kwargs):
            self.y = np.asarray(y, dtype=float)
            self.periods = periods
            self.kwargs = kwargs

        def fit(self):
            seasonals = np.column_stack(
                [
                    np.full_like(self.y, 0.5),
                    np.full_like(self.y, 1.5),
                ]
            )
            return SimpleNamespace(
                trend=np.full_like(self.y, 1.0),
                seasonal=seasonals,
                resid=self.y - 3.0,
            )

    seasonal = ModuleType("statsmodels.tsa.seasonal")
    seasonal.STL = FakeSTL
    seasonal.MSTL = FakeMSTL
    monkeypatch.setitem(sys.modules, "statsmodels", ModuleType("statsmodels"))
    monkeypatch.setitem(sys.modules, "statsmodels.tsa", ModuleType("statsmodels.tsa"))
    monkeypatch.setitem(sys.modules, "statsmodels.tsa.seasonal", seasonal)

    y = np.arange(12, dtype=float)
    stl_result = stl.stl_decompose(y, {"period": 4})
    robust_result = stl.robuststl_decompose(y, {"period": 4})
    mstl_result = stl.mstl_decompose(y, {"periods": [4, 6]})

    assert stl_result.meta["method"] == "STL"
    assert robust_result.meta["method"] == "ROBUST_STL"
    assert mstl_result.meta["method"] == "MSTL"
    np.testing.assert_allclose(mstl_result.trend + mstl_result.season + mstl_result.residual, y)


def test_wavelet_decompose_with_fake_pywt(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeWavelet:
        def __init__(self, name: str):
            self.name = name
            self.dec_len = 4

    fake_pywt = SimpleNamespace(
        Wavelet=FakeWavelet,
        dwt_max_level=lambda length, dec_len: 3,
        wavedec=lambda y, wavelet, level: [
            np.full(8, 0.5),
            np.full(8, 0.25),
            np.full(8, 0.1),
        ],
        waverec=lambda coeffs, wavelet: np.sum(np.asarray(coeffs), axis=0),
    )
    monkeypatch.setattr(wavelet, "_HAS_PYWT", True)
    monkeypatch.setattr(wavelet, "pywt", fake_pywt)

    y = np.linspace(0, 1, 8)
    result = wavelet.wavelet_decompose(y, {"wavelet": "db4", "level": 2})
    assert result.meta["method"] == "WAVELET"
    assert result.trend.shape == y.shape


def test_emd_ceemdan_and_vmd_with_fake_backends(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeEMD:
        def emd(self, y, max_imf=None):
            arr = np.asarray(y, dtype=float)
            return np.vstack([0.6 * arr, 0.3 * arr, 0.1 * arr])

    class FakeCEEMDAN:
        def __call__(self, y):
            arr = np.asarray(y, dtype=float)
            return np.vstack([0.5 * arr, 0.25 * arr, 0.25 * arr])

    def fake_vmd(y, alpha, tau, K, DC, init, tol):
        arr = np.asarray(y, dtype=float)
        modes = np.vstack([0.5 * arr, 0.3 * arr, 0.2 * arr])
        omega = np.array([[0.01, 0.2, 0.4]])
        return modes, None, omega

    monkeypatch.setattr(emd, "_HAS_PYEMD", True)
    monkeypatch.setattr(emd, "EMD", FakeEMD, raising=False)
    monkeypatch.setattr(ceemdan, "_HAS_CEEMDAN", True)
    monkeypatch.setattr(ceemdan, "CEEMDAN", FakeCEEMDAN, raising=False)
    monkeypatch.setattr(vmd, "_HAS_VMD", True)
    monkeypatch.setattr(vmd, "VMD", fake_vmd, raising=False)

    y = np.sin(np.linspace(0, 2 * np.pi, 24))
    emd_result = emd.emd_decompose(y, {"primary_period": 12, "n_imfs": 3})
    ceemdan_result = ceemdan.ceemdan_decompose(y, {"primary_period": 12})
    vmd_result = vmd.vmd_decompose(y, {"primary_period": 12, "K": 3})

    assert emd_result.meta["method"] == "EMD"
    assert ceemdan_result.meta["method"] == "CEEMDAN"
    assert vmd_result.meta["method"] == "VMD"


def test_dr_wrappers_and_std_multi_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_backend(y, config, fs, meta=None):
        arr = np.asarray(y, dtype=float)
        return SimpleNamespace(
            trend=0.5 * arr,
            season=0.25 * arr,
            residual=0.25 * arr,
            extra={"source": "fake"},
        )

    monkeypatch.setattr(dr_ts_ae, "_load_python_backend", lambda: fake_backend)
    monkeypatch.setattr(sl_lib, "_load_python_backend", lambda: fake_backend)
    monkeypatch.setattr(dr_ts_reg, "_load_python_backend", lambda: fake_backend)
    monkeypatch.setattr(std_multi, "ssa_decompose", lambda y, params: DecompResult(
        trend=np.asarray(y, dtype=float),
        season=np.zeros_like(y, dtype=float),
        residual=np.zeros_like(y, dtype=float),
        meta={"method": "SSA_FALLBACK"},
    ))
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "fasttimes":
            raise ImportError("forced missing fasttimes")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    y = np.arange(24, dtype=float)
    assert dr_ts_ae.dr_ts_ae_wrapper(y, {}).meta["method"] == "DR_TS_AE"
    assert sl_lib.sl_lib_wrapper(y, {}).meta["method"] == "SL_LIB"
    assert dr_ts_reg.dr_ts_reg_wrapper(y, {"backend": "python", "period": 6}).meta["method"] == "DR_TS_REG"
    assert std_multi.std_multi_decompose(y, {}).meta["method"] == "SSA_FALLBACK"
    assert std_multi.std_full_ablation_decompose(y, {}).meta["method"] == "SSA_FALLBACK"


def test_ssa_and_dr_ts_reg_native_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    native_payload = {
        "trend": np.array([1.0, 2.0]),
        "season": np.array([0.5, 0.5]),
        "residual": np.array([0.1, 0.2]),
        "meta": {"method": "NATIVE"},
    }

    monkeypatch.setattr(ssa, "resolve_backend", lambda *args, **kwargs: "native")
    monkeypatch.setattr(ssa, "invoke_native", lambda *args, **kwargs: native_payload)
    monkeypatch.setattr(dr_ts_reg, "resolve_backend", lambda *args, **kwargs: "native")
    monkeypatch.setattr(dr_ts_reg, "invoke_native", lambda *args, **kwargs: native_payload)

    ssa_result = ssa.ssa_decompose(np.array([1.0, 2.0]), {"__tsdecomp_runtime__": {"backend": "auto"}})
    reg_result = dr_ts_reg.dr_ts_reg_wrapper(
        np.array([1.0, 2.0]),
        {"period": 2, "__tsdecomp_runtime__": {"backend": "auto"}},
    )
    np.testing.assert_allclose(ssa_result.trend, native_payload["trend"])
    np.testing.assert_allclose(reg_result.trend, native_payload["trend"])


def test_gabor_cluster_python_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gabor_cluster, "_HAS_FAISS", True)
    monkeypatch.setattr(
        gabor_cluster,
        "_assign_clusters_faiss",
        lambda feats, model: np.array([0, 0, 1, 1, 0, 1, 0, 1, 1], dtype=int),
    )

    cfg = gabor_cluster.GaborClusterConfig(
        win_len=4,
        hop=2,
        n_fft=4,
        n_clusters=2,
    )
    model = gabor_cluster.GaborClusterModel(
        centroids=np.array([[0.0, 0.0, 0.1], [0.0, 0.8, 0.2]], dtype=np.float32),
        mu=np.zeros(3, dtype=np.float32),
        sigma=np.ones(3, dtype=np.float32),
        cfg=cfg,
    )
    y = np.linspace(0.0, 1.0, 8)
    result = gabor_cluster.gabor_cluster_decompose(
        y,
        {
            "__tsdecomp_runtime__": {"backend": "python"},
            "model": model,
            "max_clusters": 2,
        },
    )
    assert result.meta["method"] == "GABOR_CLUSTER"
    assert result.meta["backend_used"] == "python"
    assert result.trend.shape == y.shape
