from __future__ import annotations

import builtins
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

from detime import DecompResult
from detime.methods import ceemdan, emd, ma_baseline, memd, mvmd, stl, vmd, wavelet
import detime.methods.gabor_cluster as gabor_mod


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
    monkeypatch.setitem(__import__("sys").modules, "statsmodels", ModuleType("statsmodels"))
    monkeypatch.setitem(__import__("sys").modules, "statsmodels.tsa", ModuleType("statsmodels.tsa"))
    monkeypatch.setitem(__import__("sys").modules, "statsmodels.tsa.seasonal", seasonal)

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

    monkeypatch.setattr(mvmd, "import_module", fake_import)

    t = np.arange(48, dtype=float)
    y = np.column_stack(
        [
            np.sin(2.0 * np.pi * t / 12.0) + 0.05 * t,
            0.8 * np.sin(2.0 * np.pi * t / 12.0 + 0.2) + 0.03 * t,
        ]
    )

    mvmd_result = mvmd.mvmd_decompose(y, {"primary_period": 12})
    memd_result = memd.memd_decompose(y, {"primary_period": 12})

    assert mvmd_result.trend.shape == y.shape
    assert mvmd_result.components["modes"].ndim == 3
    assert memd_result.components["imfs"].ndim == 3


def test_std_multi_falls_back_to_ssa(monkeypatch) -> None:
    import detime.methods.std_multi as std_multi_mod

    y = np.arange(24, dtype=float)
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


def test_gabor_cluster_python_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gabor_mod, "_HAS_FAISS", True)
    monkeypatch.setattr(
        gabor_mod,
        "_assign_clusters_faiss",
        lambda feats, model: np.array([0, 0, 1, 1, 0, 1, 0, 1, 1], dtype=int),
    )

    cfg = gabor_mod.GaborClusterConfig(
        win_len=4,
        hop=2,
        n_fft=4,
        n_clusters=2,
    )
    model = gabor_mod.GaborClusterModel(
        centroids=np.array([[0.0, 0.0, 0.1], [0.0, 0.8, 0.2]], dtype=np.float32),
        mu=np.zeros(3, dtype=np.float32),
        sigma=np.ones(3, dtype=np.float32),
        cfg=cfg,
    )
    y = np.linspace(0.0, 1.0, 8)
    result = gabor_mod.gabor_cluster_decompose(
        y,
        {
            "__detime_runtime__": {"backend": "python"},
            "model": model,
            "max_clusters": 2,
        },
    )
    assert result.meta["method"] == "GABOR_CLUSTER"
    assert result.meta["backend_used"] == "python"
    assert result.trend.shape == y.shape
