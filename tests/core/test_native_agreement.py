from __future__ import annotations

import numpy as np
import pytest

from detime import DecompositionConfig, decompose, native_capabilities
from detime.serialization import build_result_diagnostics


def _signal(length: int = 120) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return 0.03 * t + np.sin(2.0 * np.pi * t / 12.0) + 0.2 * np.cos(2.0 * np.pi * t / 6.0)


def _panel(length: int = 96) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return np.column_stack(
        [
            0.04 * t + np.sin(2.0 * np.pi * t / 12.0),
            0.02 * t + 0.7 * np.sin(2.0 * np.pi * t / 12.0) + 0.2 * np.cos(2.0 * np.pi * t / 6.0),
        ]
    )


@pytest.mark.skipif(
    not native_capabilities().get("ssa_decompose", False),
    reason="SSA native kernel is unavailable in this environment.",
)
def test_ssa_native_matches_python_with_documented_tolerance() -> None:
    series = _signal()
    params = {"window": 24, "rank": 6, "primary_period": 12}

    python_result = decompose(series, DecompositionConfig(method="SSA", params=params, backend="python"))
    native_result = decompose(series, DecompositionConfig(method="SSA", params=params, backend="native"))

    np.testing.assert_allclose(native_result.trend, python_result.trend, atol=1e-6)
    np.testing.assert_allclose(native_result.season, python_result.season, atol=1e-6)
    np.testing.assert_allclose(native_result.residual, python_result.residual, atol=1e-6)

    native_diag = build_result_diagnostics(native_result)
    python_diag = build_result_diagnostics(python_result)
    assert native_diag["component_count"] == python_diag["component_count"]
    assert native_diag["quality_metrics"]["residual_ratio"] == pytest.approx(
        python_diag["quality_metrics"]["residual_ratio"],
        abs=1e-6,
    )


@pytest.mark.skipif(
    not native_capabilities().get("ssa_decompose", False),
    reason="SSA native kernel is unavailable in this environment.",
)
def test_ssa_native_fast_mode_is_seeded_and_quality_bounded() -> None:
    series = _signal(length=180)
    params = {"window": 36, "rank": 8, "primary_period": 12, "power_iterations": 24}

    exact_result = decompose(series, DecompositionConfig(method="SSA", params=params, backend="native"))
    fast_a = decompose(
        series,
        DecompositionConfig(method="SSA", params=params, backend="native", speed_mode="fast", seed=123),
    )
    fast_b = decompose(
        series,
        DecompositionConfig(method="SSA", params=params, backend="native", speed_mode="fast", seed=123),
    )

    np.testing.assert_allclose(fast_a.trend, fast_b.trend, atol=1e-9)
    np.testing.assert_allclose(fast_a.season, fast_b.season, atol=1e-9)
    np.testing.assert_allclose(fast_a.residual, fast_b.residual, atol=1e-9)
    np.testing.assert_allclose(fast_a.trend + fast_a.season + fast_a.residual, series, atol=1e-6)

    fast_diag = build_result_diagnostics(fast_a)
    exact_diag = build_result_diagnostics(exact_result)
    assert fast_a.meta["speed_mode"] == "fast"
    assert fast_a.meta["backend_used"] == "native"
    assert fast_diag["quality_metrics"]["residual_ratio"] == pytest.approx(
        exact_diag["quality_metrics"]["residual_ratio"],
        abs=5e-2,
    )


@pytest.mark.skipif(
    not native_capabilities().get("std_decompose", False),
    reason="STD native kernel is unavailable in this environment.",
)
@pytest.mark.parametrize("method_name", ["STD", "STDR"])
def test_std_family_native_matches_python_with_documented_tolerance(method_name: str) -> None:
    series = _signal()
    params = {"period": 12}

    python_result = decompose(series, DecompositionConfig(method=method_name, params=params, backend="python"))
    native_result = decompose(series, DecompositionConfig(method=method_name, params=params, backend="native"))

    np.testing.assert_allclose(native_result.trend, python_result.trend, atol=1e-9)
    np.testing.assert_allclose(native_result.season, python_result.season, atol=1e-9)
    np.testing.assert_allclose(native_result.residual, python_result.residual, atol=1e-9)

    native_diag = build_result_diagnostics(native_result)
    python_diag = build_result_diagnostics(python_result)
    assert native_diag["quality_metrics"]["trend_l2_norm"] == pytest.approx(
        python_diag["quality_metrics"]["trend_l2_norm"],
        abs=1e-9,
    )
    assert native_diag["quality_metrics"]["residual_ratio"] == pytest.approx(
        python_diag["quality_metrics"]["residual_ratio"],
        abs=1e-9,
    )


@pytest.mark.skipif(
    not native_capabilities().get("ma_baseline_decompose", False),
    reason="MA_BASELINE native kernel is unavailable in this environment.",
)
def test_ma_baseline_native_matches_python_path() -> None:
    series = _signal(length=96)
    params = {"trend_window": 9, "season_period": 12}

    python_result = decompose(series, DecompositionConfig(method="MA_BASELINE", params=params, backend="python"))
    native_result = decompose(series, DecompositionConfig(method="MA_BASELINE", params=params, backend="native"))

    np.testing.assert_allclose(native_result.trend, python_result.trend, atol=1e-12)
    np.testing.assert_allclose(native_result.season, python_result.season, atol=1e-12)
    np.testing.assert_allclose(native_result.residual, python_result.residual, atol=1e-12)
    assert native_result.meta["backend_used"] == "native"


@pytest.mark.skipif(
    not native_capabilities().get("mssa_decompose", False),
    reason="MSSA native kernel is unavailable in this environment.",
)
def test_mssa_native_matches_python_exact_path() -> None:
    series = _panel(length=72)
    params = {"window": 18, "rank": 6, "primary_period": 12}

    python_result = decompose(series, DecompositionConfig(method="MSSA", params=params, backend="python"))
    native_result = decompose(series, DecompositionConfig(method="MSSA", params=params, backend="native"))

    np.testing.assert_allclose(native_result.trend, python_result.trend, atol=1e-9)
    np.testing.assert_allclose(native_result.season, python_result.season, atol=1e-9)
    np.testing.assert_allclose(native_result.residual, python_result.residual, atol=1e-9)
    np.testing.assert_allclose(native_result.components["modes"], python_result.components["modes"], atol=1e-9)
    assert native_result.meta["backend_used"] == "native"


@pytest.mark.skipif(
    not native_capabilities().get("vmd_decompose", False),
    reason="VMD native kernel is unavailable in this environment.",
)
def test_vmd_native_tracks_python_backend() -> None:
    series = _signal(length=72)
    params = {"K": 4, "alpha": 300.0, "primary_period": 12}

    python_result = decompose(series, DecompositionConfig(method="VMD", params=params, backend="python"))
    native_result = decompose(series, DecompositionConfig(method="VMD", params=params, backend="native"))

    np.testing.assert_allclose(native_result.trend, python_result.trend, atol=1e-4)
    np.testing.assert_allclose(native_result.season, python_result.season, atol=1e-4)
    np.testing.assert_allclose(native_result.residual, python_result.residual, atol=1e-4)
    assert native_result.meta["trend_index"] == python_result.meta["trend_index"]
    assert native_result.meta["season_indices"] == python_result.meta["season_indices"]


@pytest.mark.skipif(
    not (
        native_capabilities().get("gabor_stft_rfft", False)
        and native_capabilities().get("gabor_istft_rfft", False)
    ),
    reason="Gabor native STFT helpers are unavailable in this environment.",
)
def test_gabor_native_stft_istft_roundtrip() -> None:
    from detime._native import invoke_native
    from detime.methods.gabor_cluster import _make_window

    series = np.linspace(0.0, 1.0, 24)
    window = _make_window(8, "gaussian", None)
    spectrum = invoke_native(
        "gabor_stft_rfft",
        series,
        win_len=8,
        hop=4,
        n_fft=8,
        window=window,
    )
    reconstructed = invoke_native(
        "gabor_istft_rfft",
        spectrum,
        win_len=8,
        hop=4,
        n_fft=8,
        window=window,
        length=series.size,
    )

    assert spectrum.shape == (5, 5)
    np.testing.assert_allclose(reconstructed, series, atol=1e-5)


@pytest.mark.skipif(
    not native_capabilities().get("gabor_cluster_decompose", False),
    reason="Gabor native cluster decomposition is unavailable in this environment.",
)
def test_gabor_cluster_native_decomposes_without_faiss_assignment() -> None:
    from detime.methods.gabor_cluster import GaborClusterConfig, GaborClusterModel

    t = np.arange(48, dtype=float)
    series = 0.01 * t + np.sin(2.0 * np.pi * t / 12.0)
    cfg = GaborClusterConfig(win_len=12, hop=6, n_fft=16, n_clusters=3)
    model = GaborClusterModel(
        centroids=np.array(
            [
                [0.0, 0.0, 0.0],
                [0.5, 0.35, 0.0],
                [1.0, 1.0, 0.0],
            ],
            dtype=np.float32,
        ),
        mu=np.zeros(3, dtype=np.float32),
        sigma=np.ones(3, dtype=np.float32),
        cfg=cfg,
    )

    result = decompose(
        series,
        DecompositionConfig(
            method="GABOR_CLUSTER",
            params={"model": model, "trend_freq_thr": 0.2},
            backend="native",
        ),
    )

    assert result.meta["method"] == "GABOR_CLUSTER"
    assert result.meta["backend_used"] == "native"
    assert result.trend.shape == series.shape
    assert result.components
    np.testing.assert_allclose(result.trend + result.season + result.residual, series, atol=1e-5)
