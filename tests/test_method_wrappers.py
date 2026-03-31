from __future__ import annotations

import types
from pathlib import Path

import numpy as np

from tsdecomp import DecompositionConfig, decompose
from tsdecomp.methods import ceemdan as ceemdan_mod
from tsdecomp.methods import dr_ts_ae as dr_ts_ae_mod
from tsdecomp.methods import emd as emd_mod
from tsdecomp.methods import gabor_cluster as gabor_mod
from tsdecomp.methods import sl_lib as sl_lib_mod
from tsdecomp.methods import vmd as vmd_mod
from tsdecomp.methods import wavelet as wavelet_mod


def test_ma_baseline_reconstructs_signal() -> None:
    x = np.arange(48, dtype=float)
    series = 0.05 * x + np.sin(2.0 * np.pi * x / 12.0)

    result = decompose(
        series,
        DecompositionConfig(
            method="MA_BASELINE",
            params={"trend_window": 5, "season_period": 12},
        ),
    )

    np.testing.assert_allclose(
        result.trend + result.season + result.residual,
        series,
        atol=1e-9,
    )


def test_ssa_python_backend_smoke() -> None:
    x = np.arange(60, dtype=float)
    series = 0.02 * x + np.sin(2.0 * np.pi * x / 12.0)

    result = decompose(
        series,
        DecompositionConfig(
            method="SSA",
            params={"window": 18, "rank": 6, "primary_period": 12},
            backend="python",
        ),
    )

    np.testing.assert_allclose(
        result.trend + result.season + result.residual,
        series,
        atol=1e-6,
    )
    assert result.meta["backend_used"] == "python"


def test_stl_family_with_fake_statsmodels(monkeypatch) -> None:
    import tsdecomp.methods.stl as stl_mod

    class FakeSTL:
        def __init__(self, y, period, robust=False, **kwargs):
            self.y = np.asarray(y, dtype=float)
            self.period = period
            self.robust = robust
            self.kwargs = kwargs

        def fit(self):
            trend = np.full_like(self.y, np.mean(self.y))
            seasonal = self.y - trend
            return types.SimpleNamespace(trend=trend, seasonal=seasonal, resid=np.zeros_like(self.y))

    class FakeMSTL:
        def __init__(self, y, periods, **kwargs):
            self.y = np.asarray(y, dtype=float)
            self.periods = periods
            self.kwargs = kwargs

        def fit(self):
            trend = np.full_like(self.y, np.mean(self.y))
            half = 0.5 * (self.y - trend)
            seasonal = np.column_stack([half, half])
            return types.SimpleNamespace(trend=trend, seasonal=seasonal, resid=np.zeros_like(self.y))

    fake_seasonal = types.SimpleNamespace(STL=FakeSTL, MSTL=FakeMSTL)
    monkeypatch.setitem(__import__("sys").modules, "statsmodels", types.ModuleType("statsmodels"))
    monkeypatch.setitem(__import__("sys").modules, "statsmodels.tsa", types.ModuleType("statsmodels.tsa"))
    monkeypatch.setitem(__import__("sys").modules, "statsmodels.tsa.seasonal", fake_seasonal)

    x = np.arange(24, dtype=float)
    series = np.sin(2.0 * np.pi * x / 12.0)

    stl_res = stl_mod.stl_decompose(series, {"period": 12})
    mstl_res = stl_mod.mstl_decompose(series, {"periods": [12, 6]})
    robust_res = stl_mod.robuststl_decompose(series, {"period": 12})

    for result in (stl_res, mstl_res, robust_res):
        np.testing.assert_allclose(
            result.trend + result.season + result.residual,
            series,
            atol=1e-9,
        )


def test_wavelet_decompose_with_fake_pywt(monkeypatch) -> None:
    class FakeWavelet:
        dec_len = 2

        def __init__(self, name):
            self.name = name

    class FakePywt:
        Wavelet = FakeWavelet

        @staticmethod
        def dwt_max_level(length, dec_len):
            return 3

        @staticmethod
        def wavedec(y, wavelet, level):
            n = len(y)
            return [
                np.full(max(2, n // 8), 1.0),
                np.full(max(2, n // 4), 0.5),
                np.full(max(2, n // 2), 0.25),
            ]

        @staticmethod
        def waverec(coeffs, wavelet):
            target = 32
            fill = sum(float(np.mean(c)) for c in coeffs if c is not None)
            return np.full(target, fill, dtype=float)

    monkeypatch.setattr(wavelet_mod, "_HAS_PYWT", True)
    monkeypatch.setattr(wavelet_mod, "pywt", FakePywt)

    series = np.linspace(0.0, 1.0, 32)
    result = wavelet_mod.wavelet_decompose(series, {"wavelet": "db4", "level": 2})

    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape


def test_emd_with_fake_backend(monkeypatch) -> None:
    class FakeEMD:
        def emd(self, y, max_imf=None):
            y = np.asarray(y, dtype=float)
            return np.vstack(
                [
                    0.6 * np.sin(2.0 * np.pi * np.arange(y.size) / 12.0),
                    0.05 * np.arange(y.size, dtype=float),
                    y - 0.6 * np.sin(2.0 * np.pi * np.arange(y.size) / 12.0) - 0.05 * np.arange(y.size, dtype=float),
                ]
            )

    monkeypatch.setattr(emd_mod, "_HAS_PYEMD", True)
    monkeypatch.setattr(emd_mod, "EMD", FakeEMD, raising=False)

    x = np.arange(36, dtype=float)
    series = 0.05 * x + np.sin(2.0 * np.pi * x / 12.0)
    result = emd_mod.emd_decompose(series, {"primary_period": 12})

    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape


def test_ceemdan_with_fake_backend(monkeypatch) -> None:
    class FakeCEEMDAN:
        def __init__(self):
            self.trials = None
            self.noise_width = None

        def __call__(self, y):
            y = np.asarray(y, dtype=float)
            return np.vstack(
                [
                    0.5 * np.sin(2.0 * np.pi * np.arange(y.size) / 12.0),
                    0.02 * np.arange(y.size, dtype=float),
                    y - 0.5 * np.sin(2.0 * np.pi * np.arange(y.size) / 12.0) - 0.02 * np.arange(y.size, dtype=float),
                ]
            )

    monkeypatch.setattr(ceemdan_mod, "_HAS_CEEMDAN", True)
    monkeypatch.setattr(ceemdan_mod, "CEEMDAN", FakeCEEMDAN, raising=False)

    x = np.arange(36, dtype=float)
    series = 0.02 * x + np.sin(2.0 * np.pi * x / 12.0)
    result = ceemdan_mod.ceemdan_decompose(series, {"primary_period": 12, "trials": 4})

    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape


def test_vmd_with_fake_backend(monkeypatch) -> None:
    def fake_vmd(y, alpha, tau, K, DC, init, tol):
        y = np.asarray(y, dtype=float)
        modes = np.vstack(
            [
                0.03 * np.arange(y.size, dtype=float),
                np.sin(2.0 * np.pi * np.arange(y.size) / 12.0),
                y - 0.03 * np.arange(y.size, dtype=float) - np.sin(2.0 * np.pi * np.arange(y.size) / 12.0),
            ]
        )
        omega = np.array([[0.0, 0.4, 1.2]])
        return modes, None, omega

    monkeypatch.setattr(vmd_mod, "_HAS_VMD", True)
    monkeypatch.setattr(vmd_mod, "VMD", fake_vmd, raising=False)

    x = np.arange(48, dtype=float)
    series = 0.03 * x + np.sin(2.0 * np.pi * x / 12.0)
    result = vmd_mod.vmd_decompose(series, {"primary_period": 12, "seasonal_num_modes": 1})

    np.testing.assert_allclose(
        result.trend + result.season + result.residual,
        series,
        atol=1e-9,
    )


def test_dr_ts_ae_and_sl_lib_wrappers_with_fake_backends(monkeypatch) -> None:
    def fake_import_module(name):
        def fake_decompose(y, config, fs, meta):
            y = np.asarray(y, dtype=float)
            trend = np.full_like(y, np.mean(y))
            season = y - trend
            residual = np.zeros_like(y)
            return types.SimpleNamespace(
                trend=trend,
                season=season,
                residual=residual,
                extra={"backend_module": name},
            )

        return types.SimpleNamespace(
            dr_ts_ae_decompose=fake_decompose,
            sl_lib_decompose=fake_decompose,
        )

    monkeypatch.setattr(dr_ts_ae_mod, "import_module", fake_import_module)
    monkeypatch.setattr(sl_lib_mod, "import_module", fake_import_module)

    series = np.linspace(0.0, 1.0, 24)
    ae_result = dr_ts_ae_mod.dr_ts_ae_wrapper(series, {"primary_period": 12})
    sl_result = sl_lib_mod.sl_lib_wrapper(series, {})

    assert ae_result.meta["backend_module"] == "synthetic_ts_bench.dr_ts_ae"
    assert sl_result.meta["backend_module"] == "synthetic_ts_bench.sl_lib"


def test_gabor_cluster_python_backend_with_fake_faiss(monkeypatch) -> None:
    class FakeIndexFlatL2:
        def __init__(self, d):
            self.d = d

        def add(self, arr):
            self.arr = arr

        def search(self, feats, k):
            labels = np.zeros((feats.shape[0], 1), dtype=np.int64)
            dist = np.zeros((feats.shape[0], 1), dtype=np.float32)
            return dist, labels

    monkeypatch.setattr(gabor_mod, "_HAS_FAISS", True)
    monkeypatch.setattr(
        gabor_mod,
        "faiss",
        types.SimpleNamespace(IndexFlatL2=FakeIndexFlatL2),
        raising=False,
    )

    cfg = gabor_mod.GaborClusterConfig(win_len=8, hop=4, n_fft=8, n_clusters=1)
    model = gabor_mod.GaborClusterModel(
        centroids=np.zeros((1, 3), dtype=np.float32),
        mu=np.zeros(3, dtype=np.float32),
        sigma=np.ones(3, dtype=np.float32),
        cfg=cfg,
    )
    x = np.arange(32, dtype=float)
    series = np.sin(2.0 * np.pi * x / 8.0)

    result = gabor_mod.gabor_cluster_decompose(
        series,
        {"model": model, "max_clusters": 1, "trend_freq_thr": 0.5},
    )

    np.testing.assert_allclose(
        result.trend + result.season + result.residual,
        series,
        atol=1e-6,
    )


def test_example_data_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "examples" / "data" / "example_series.csv").exists()
    assert (root / "examples" / "data" / "example_multivariate.csv").exists()
