from __future__ import annotations

import numpy as np
import pytest

from detime import DecompositionConfig, decompose, native_capabilities
from detime.registry import MethodRegistry


def _shared_multichannel_signal(length: int = 72) -> np.ndarray:
    t = np.arange(length, dtype=float)
    season = np.sin(2.0 * np.pi * t / 12.0)
    x0 = 0.04 * t + 1.0 * season
    x1 = 0.02 * t + 0.7 * season + 0.2 * np.cos(2.0 * np.pi * t / 6.0)
    return np.column_stack([x0, x1])


def test_flagship_methods_are_registered() -> None:
    methods = set(MethodRegistry.list_methods())
    assert {"SSA", "STD", "STDR", "MSSA"}.issubset(methods)
    assert "DR_TS_REG" not in methods


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


def test_std_decomposition_exposes_dispersion_component() -> None:
    base = np.array([0.0, 1.0, 0.0, -1.0], dtype=float)
    y = np.concatenate(
        [
            10.0 + 1.0 * base,
            20.0 + 2.0 * base,
            30.0 + 0.5 * base,
        ]
    )

    result = decompose(
        y,
        DecompositionConfig(method="STD", params={"period": 4}),
    )

    np.testing.assert_allclose(result.trend[:4], np.full(4, 10.0))
    np.testing.assert_allclose(result.trend[4:8], np.full(4, 20.0))
    np.testing.assert_allclose(result.trend[8:], np.full(4, 30.0))
    np.testing.assert_allclose(result.residual, np.zeros_like(y), atol=1e-10)
    np.testing.assert_allclose(result.trend + result.season + result.residual, y, atol=1e-10)
    assert "dispersion" in result.components
    assert "seasonal_shape" in result.components
    np.testing.assert_allclose(result.components["dispersion"][:4], np.full(4, np.sqrt(2.0)))
    assert result.meta["method"] == "STD"
    assert result.meta["period"] == 4


def test_stdr_keeps_shared_shape_metadata() -> None:
    base = np.array([0.0, 1.0, 0.0, -1.0], dtype=float)
    y = np.concatenate(
        [
            10.0 + 1.0 * base,
            20.0 + 2.0 * base,
            30.0 + np.array([0.0, 0.5, 0.5, -1.0], dtype=float),
        ]
    )

    result = decompose(
        y,
        DecompositionConfig(method="STDR", params={"period": 4}),
    )

    assert result.meta["method"] == "STDR"
    assert "average_seasonal_shape" in result.components
    assert np.linalg.norm(result.residual) > 0.0


def test_univariate_method_rejects_2d_input() -> None:
    series = _shared_multichannel_signal()

    with pytest.raises((TypeError, ValueError), match="1D|2D|univariate|multivariate"):
        decompose(
            series,
            DecompositionConfig(method="SSA", params={"window": 18, "rank": 4}),
        )


def test_std_channelwise_accepts_2d_input() -> None:
    series = _shared_multichannel_signal()

    result = decompose(
        series,
        DecompositionConfig(method="STD", params={"period": 12}),
    )

    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, series, atol=1e-9)
    assert result.components["dispersion"].shape == series.shape
    assert result.components["seasonal_shape"].shape == series.shape
    assert result.meta["n_channels"] == series.shape[1]
    assert result.meta["input_shape"] == list(series.shape)
    assert result.meta["result_layout"] == "multivariate"


def test_mssa_requires_2d_input() -> None:
    series = _shared_multichannel_signal()[:, 0]

    with pytest.raises((TypeError, ValueError), match="2D|multivariate"):
        decompose(
            series,
            DecompositionConfig(method="MSSA", params={"window": 18, "rank": 4, "primary_period": 12}),
        )


def test_mssa_smoke_on_shared_season_signal() -> None:
    series = _shared_multichannel_signal()
    true_season = np.sin(2.0 * np.pi * np.arange(series.shape[0], dtype=float) / 12.0)

    result = decompose(
        series,
        DecompositionConfig(
            method="MSSA",
            params={"window": 18, "rank": 6, "primary_period": 12},
        ),
    )

    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, series, atol=1e-6)
    assert any(key in result.components for key in ("modes", "reconstructed_components", "rc_list"))
    assert "singular_values" in result.meta
    assert result.meta["window"] == 18
    assert result.meta["rank"] == 6
    assert result.meta["n_channels"] == series.shape[1]

    corr0 = np.corrcoef(result.season[:, 0], true_season)[0, 1]
    corr1 = np.corrcoef(result.season[:, 1], true_season)[0, 1]
    assert abs(corr0) > 0.4
    assert abs(corr1) > 0.4


@pytest.mark.skipif(
    not native_capabilities().get("std_decompose", False),
    reason="STD native kernel is unavailable in this environment.",
)
def test_std_native_matches_python_1d() -> None:
    series = _shared_multichannel_signal()[:, 0]

    py_result = decompose(
        series,
        DecompositionConfig(method="STD", params={"period": 12}, backend="python"),
    )
    native_result = decompose(
        series,
        DecompositionConfig(method="STD", params={"period": 12}, backend="native"),
    )

    np.testing.assert_allclose(native_result.trend, py_result.trend, atol=1e-9)
    np.testing.assert_allclose(native_result.season, py_result.season, atol=1e-9)
    np.testing.assert_allclose(native_result.residual, py_result.residual, atol=1e-9)


@pytest.mark.skipif(
    not native_capabilities().get("std_decompose", False),
    reason="STD native kernel is unavailable in this environment.",
)
def test_std_native_matches_python_channelwise_2d() -> None:
    series = _shared_multichannel_signal()

    py_result = decompose(
        series,
        DecompositionConfig(method="STD", params={"period": 12}, backend="python"),
    )
    native_result = decompose(
        series,
        DecompositionConfig(method="STD", params={"period": 12}, backend="native"),
    )

    np.testing.assert_allclose(native_result.trend, py_result.trend, atol=1e-9)
    np.testing.assert_allclose(native_result.season, py_result.season, atol=1e-9)
    np.testing.assert_allclose(native_result.residual, py_result.residual, atol=1e-9)
