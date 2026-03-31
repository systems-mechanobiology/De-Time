from __future__ import annotations

import json

import numpy as np
import pandas as pd

from tsdecomp.core import DecompResult
from tsdecomp.io import read_series, save_result


def test_read_series_with_cols_returns_2d(tmp_path) -> None:
    path = tmp_path / "series.csv"
    df = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0],
            "b": [4.0, 5.0, 6.0],
            "label": ["x", "y", "z"],
        }
    )
    df.to_csv(path, index=False)

    arr = read_series(path, cols=["a", "b"])

    assert arr.shape == (3, 2)
    np.testing.assert_allclose(arr[:, 0], df["a"].values)
    np.testing.assert_allclose(arr[:, 1], df["b"].values)


def test_save_result_writes_wide_csv_and_npz_for_multivariate_components(tmp_path) -> None:
    out_dir = tmp_path / "out"
    result = DecompResult(
        trend=np.asarray([[1.0, 10.0], [2.0, 20.0]], dtype=float),
        season=np.asarray([[0.5, 1.5], [0.25, 1.25]], dtype=float),
        residual=np.asarray([[0.0, 0.1], [0.0, 0.2]], dtype=float),
        components={
            "dispersion": np.asarray([[1.0, 2.0], [1.0, 2.0]], dtype=float),
            "modes": np.asarray(
                [
                    [[1.0, 10.0], [2.0, 20.0]],
                    [[0.5, 1.5], [0.25, 1.25]],
                ],
                dtype=float,
            ),
        },
        meta={
            "n_channels": 2,
            "channel_names": ["a", "b"],
            "input_shape": [2, 2],
            "result_layout": "multivariate",
        },
    )

    save_result(result, out_dir, "demo")

    csv_path = out_dir / "demo_components.csv"
    meta_path = out_dir / "demo_meta.json"

    assert csv_path.exists()
    assert meta_path.exists()

    saved = pd.read_csv(csv_path)
    assert "trend__a" in saved.columns
    assert "trend__b" in saved.columns
    assert "season__a" in saved.columns
    assert "residual__b" in saved.columns
    assert "dispersion__a" in saved.columns
    assert "dispersion__b" in saved.columns

    npz_files = sorted(out_dir.glob("*.npz"))
    assert len(npz_files) == 1
    extra = np.load(npz_files[0])
    assert "modes" in extra.files
    assert extra["modes"].shape == (2, 2, 2)

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["n_channels"] == 2
    assert meta["channel_names"] == ["a", "b"]
    assert meta["result_layout"] == "multivariate"
