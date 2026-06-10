from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from detime import DecompositionConfig, MethodRegistry, decompose


CANONICAL_NEURAL_BLOCKS = {
    "AUTOFORMER_BLOCK",
    "DLINEAR_BLOCK",
    "MOVING_AVERAGE_DECOMPOSITION_BLOCK",
    "NBEATS_INTERPRETABLE",
    "XPATCH_BLOCK",
    "LEDDAM_BLOCK",
    "INPARFORMER_BLOCK",
    "DELELSTM_BLOCK",
    "AMD_BLOCK",
    "ST_MTM_BLOCK",
    "PARSIMONY_BLOCK",
    "TIMES2D_BLOCK",
    "FREQMOE_BLOCK",
    "TIMEKAN_BLOCK",
    "WAVEFORM_BLOCK",
    "WAVELETMIXER_BLOCK",
}

NUMPY_NEURAL_BLOCK_PARAMS = {
    "AUTOFORMER_BLOCK": {"primary_period": 12, "moving_avg": 13},
    "DLINEAR_BLOCK": {"primary_period": 12, "moving_avg": 13},
    "MOVING_AVERAGE_DECOMPOSITION_BLOCK": {"primary_period": 12, "moving_avg": 13},
    "XPATCH_BLOCK": {"trend_window": 13, "season_smooth": 5},
    "LEDDAM_BLOCK": {"kernel_size": 13, "sigma": 1.0},
    "INPARFORMER_BLOCK": {"primary_period": 12, "trend_window": 13, "fit_scope": "full"},
    "DELELSTM_BLOCK": {"primary_period": 12, "alpha": 0.2, "beta": 0.1, "fit_scope": "full"},
    "AMD_BLOCK": {"primary_period": 12, "multiscale_windows": [7, 13, 25], "fit_scope": "full"},
    "ST_MTM_BLOCK": {
        "primary_period": 12,
        "trend_window": 13,
        "season_smooth_window": 5,
        "fit_scope": "full",
    },
    "PARSIMONY_BLOCK": {
        "primary_period": 12,
        "trend_window": 13,
        "num_harmonics": 2,
        "fit_scope": "full",
    },
    "TIMES2D_BLOCK": {
        "primary_period": 12,
        "top_k_periods": 2,
        "num_harmonics": 1,
        "trend_window": 13,
        "fit_scope": "full",
    },
    "FREQMOE_BLOCK": {
        "primary_period": 12,
        "trend_window": 13,
        "num_bands": 3,
        "expert_width": 32,
        "fit_scope": "full",
    },
    "TIMEKAN_BLOCK": {
        "primary_period": 12,
        "trend_window": 13,
        "num_bands": 2,
        "kan_width": 32,
        "fit_scope": "full",
    },
    "WAVEFORM_BLOCK": {"wavelet": "db2", "level": 2, "season_levels": [1, 2]},
    "WAVELETMIXER_BLOCK": {"wavelet": "db2", "level": 2, "season_levels": [1, 2]},
}


def _series(length: int = 96) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return 0.02 * t + np.sin(2.0 * np.pi * t / 12.0) + 0.2 * np.cos(2.0 * np.pi * t / 6.0)


def test_canonical_neural_blocks_are_registered() -> None:
    methods = set(MethodRegistry.list_methods())
    assert CANONICAL_NEURAL_BLOCKS.issubset(methods)

    for name in CANONICAL_NEURAL_BLOCKS:
        metadata = MethodRegistry.get_metadata(name)
        assert metadata["family"] == "NeuralBlock"
        assert metadata["summary"]
        assert metadata["parameter_docs"]
        assert metadata["references"]
        assert metadata["example_config"]["method"] == name


@pytest.mark.parametrize("method, params", sorted(NUMPY_NEURAL_BLOCK_PARAMS.items()))
def test_numpy_neural_blocks_reconstruct_signal(
    method: str,
    params: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if method in {"WAVEFORM_BLOCK", "WAVELETMIXER_BLOCK"}:
        from detime.methods.neural_blocks import neural_block_portfolio

        class FakeWavelet:
            def __init__(self, name: str):
                self.name = name
                self.dec_len = 2

        fake_pywt = SimpleNamespace(
            Wavelet=FakeWavelet,
            dwt_max_level=lambda length, dec_len: 2,
            wavedec=lambda arr, wavelet, level: [
                np.asarray(arr, dtype=float),
                np.zeros_like(np.asarray(arr, dtype=float)),
                np.zeros_like(np.asarray(arr, dtype=float)),
            ],
            waverec=lambda coeffs, wavelet: np.sum(np.asarray(coeffs), axis=0),
        )
        monkeypatch.setattr(neural_block_portfolio, "pywt", fake_pywt)
        monkeypatch.setattr(neural_block_portfolio, "_HAS_PYWT", True)

    y = _series()
    result = decompose(y, DecompositionConfig(method=method, params=params))

    assert result.meta["method"] == method
    assert result.trend.shape == y.shape
    assert result.season.shape == y.shape
    assert result.residual.shape == y.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, y, rtol=1e-8, atol=1e-8)


def test_nbeats_interpretable_smoke_when_torch_is_available() -> None:
    pytest.importorskip("torch")
    y = _series(32)

    result = decompose(
        y,
        DecompositionConfig(
            method="NBEATS_INTERPRETABLE",
            params={
                "degree_of_polynomial": 2,
                "num_harmonics": 2,
                "trend_blocks": 1,
                "seasonality_blocks": 1,
                "layers": 1,
                "layer_size": 8,
                "n_epochs": 1,
                "patience": 1,
                "restarts": 1,
                "device": "cpu",
                "seed": 1,
            },
        ),
    )

    assert result.meta["method"] == "NBEATS_INTERPRETABLE"
    assert result.trend.shape == y.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, y, rtol=1e-6, atol=1e-6)


def test_forecasting_block_edge_cases() -> None:
    from detime.methods.neural_blocks import forecasting_blocks

    empty = forecasting_blocks.autoformer_block_decompose(np.array([], dtype=float), {"moving_avg": "bad"})
    assert empty.trend.shape == (0,)
    assert empty.meta["moving_avg"] == 1
    assert empty.meta["window_source"] == "moving_avg"

    y = np.arange(6, dtype=float)
    result = forecasting_blocks.dlinear_block_decompose(y, {"period": 4})
    assert result.meta["window_source"] == "period"
    assert result.meta["moving_avg"] == 5
    np.testing.assert_allclose(result.trend + result.season + result.residual, y)


def test_xpatch_block_edge_cases() -> None:
    from detime.methods.neural_blocks import xpatch_block

    empty = xpatch_block.xpatch_block_decompose(np.array([], dtype=float), {})
    assert empty.trend.shape == (0,)
    assert empty.meta["ma_type"] == "ema"

    y = np.linspace(0.0, 1.0, 8)
    result = xpatch_block.xpatch_block_decompose(
        y,
        {
            "ma_type": "dema",
            "trend_window": 4,
            "season_smooth": 4,
            "alpha": "bad",
            "beta": np.inf,
        },
    )
    assert result.meta["ma_type"] == "dema"
    assert result.meta["trend_window"] == 5.0
    assert result.meta["season_smooth"] == 5.0
    np.testing.assert_allclose(result.trend + result.season + result.residual, y)


def test_leddam_block_edge_cases() -> None:
    from detime.methods.neural_blocks import leddam_block

    empty = leddam_block.leddam_block_decompose(np.array([], dtype=float), {"kernel_size": "bad"})
    assert empty.trend.shape == (0,)
    assert empty.meta["kernel_size"] == 1

    singleton_kernel = leddam_block.leddam_block_decompose(np.arange(5, dtype=float), {"kernel_size": 1})
    np.testing.assert_allclose(singleton_kernel.trend, np.arange(5, dtype=float))

    invalid_sigma = leddam_block.leddam_block_decompose(
        np.arange(5, dtype=float),
        {"kernel_size": 3, "sigma": 0.0},
    )
    assert invalid_sigma.components["kernel"].shape == (3,)
    np.testing.assert_allclose(invalid_sigma.components["kernel"].sum(), 1.0)
