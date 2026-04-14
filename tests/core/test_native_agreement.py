from __future__ import annotations

import numpy as np
import pytest

from detime import DecompositionConfig, decompose, native_capabilities
from detime.serialization import build_result_diagnostics


def _signal(length: int = 120) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return 0.03 * t + np.sin(2.0 * np.pi * t / 12.0) + 0.2 * np.cos(2.0 * np.pi * t / 6.0)


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
