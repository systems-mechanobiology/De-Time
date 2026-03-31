from __future__ import annotations

import numpy as np
import pytest

from tsdecomp import DecompositionConfig, decompose, native_capabilities


def _shared_multichannel_signal(length: int = 72) -> np.ndarray:
    t = np.arange(length, dtype=float)
    season = np.sin(2.0 * np.pi * t / 12.0)
    x0 = 0.04 * t + 1.0 * season
    x1 = 0.02 * t + 0.7 * season + 0.2 * np.cos(2.0 * np.pi * t / 6.0)
    return np.column_stack([x0, x1])


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
    np.testing.assert_allclose(
        native_result.components["dispersion"],
        py_result.components["dispersion"],
        atol=1e-9,
    )
    np.testing.assert_allclose(
        native_result.components["seasonal_shape"],
        py_result.components["seasonal_shape"],
        atol=1e-9,
    )


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
    np.testing.assert_allclose(
        native_result.components["dispersion"],
        py_result.components["dispersion"],
        atol=1e-9,
    )
    np.testing.assert_allclose(
        native_result.components["seasonal_shape"],
        py_result.components["seasonal_shape"],
        atol=1e-9,
    )
