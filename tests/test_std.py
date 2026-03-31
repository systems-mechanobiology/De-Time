from __future__ import annotations

import numpy as np

from tsdecomp import DecompositionConfig, decompose
from tsdecomp.registry import MethodRegistry


def test_std_method_is_registered() -> None:
    assert "STD" in MethodRegistry.list_methods()
    assert "STDR" in MethodRegistry.list_methods()


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


def test_stdr_keeps_same_trend_and_dispersion_shape_metadata() -> None:
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
