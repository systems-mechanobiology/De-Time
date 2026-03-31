from __future__ import annotations

import numpy as np

from tsdecomp import DecompositionConfig, decompose


def _signal() -> np.ndarray:
    t = np.arange(48, dtype=float)
    x0 = np.sin(2.0 * np.pi * t / 12.0) + 0.05 * t
    x1 = 0.8 * np.sin(2.0 * np.pi * t / 12.0 + 0.2) + 0.03 * t
    return np.column_stack([x0, x1])


def _assert_optional_backend_or_result(method: str, components_key: str) -> None:
    series = _signal()
    try:
        result = decompose(
            series,
            DecompositionConfig(method=method, params={"K": 3, "period": 12}),
        )
    except ImportError as exc:
        assert "de-time[multivar]" in str(exc)
        return

    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape
    assert components_key in result.components
    assert result.components[components_key].ndim == 3
    assert result.components[components_key].shape[1:] == series.shape


def test_mvmd_optional_backend_behavior() -> None:
    _assert_optional_backend_or_result("MVMD", "modes")


def test_memd_optional_backend_behavior() -> None:
    _assert_optional_backend_or_result("MEMD", "imfs")
