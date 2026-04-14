from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from detime import DecompositionConfig, decompose

try:
    import pysdkit  # noqa: F401
except Exception as exc:  # pragma: no cover - depends on optional extra
    pytestmark = pytest.mark.skip(reason=f"optional multivariate backend unavailable: {exc}")

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_SCRIPT = ROOT / "examples" / "optional_multivariate_backends.py"


def _panel(length: int = 96) -> np.ndarray:
    t = np.arange(length, dtype=float)
    season = np.sin(2.0 * np.pi * t / 12.0)
    return np.column_stack(
        [
            0.03 * t + 0.9 * season,
            -0.01 * t + 0.6 * np.sin(2.0 * np.pi * t / 12.0 + 0.35) + 0.15 * np.cos(2.0 * np.pi * t / 6.0),
            0.02 * t + 0.5 * np.sin(2.0 * np.pi * t / 12.0 - 0.2) + 0.1 * np.cos(2.0 * np.pi * t / 4.0),
        ]
    )


@pytest.mark.parametrize(
    ("method_name", "component_name"),
    [
        ("MVMD", "modes"),
        ("MEMD", "imfs"),
    ],
)
def test_optional_multivariate_python_smoke(method_name: str, component_name: str) -> None:
    panel = _panel()
    result = decompose(
        panel,
        DecompositionConfig(
            method=method_name,
            params={"primary_period": 12},
            backend="python",
            channel_names=["x0", "x1", "x2"],
        ),
    )

    assert result.meta["backend_used"] == "python"
    assert component_name in result.components
    component_stack = np.asarray(result.components[component_name], dtype=float)
    assert component_stack.ndim == 3
    assert component_stack.shape[1:] == panel.shape
    assert result.trend.shape == panel.shape
    assert result.season.shape == panel.shape
    assert result.residual.shape == panel.shape
    assert np.isfinite(component_stack).all()
    assert np.isfinite(result.trend).all()
    assert np.isfinite(result.season).all()
    assert np.isfinite(result.residual).all()


@pytest.mark.parametrize("method_name", ["MVMD", "MEMD"])
def test_optional_multivariate_cli_smoke(tmp_path: Path, method_name: str) -> None:
    csv_path = tmp_path / "optional_panel.csv"
    pd.DataFrame(_panel(), columns=["x0", "x1", "x2"]).to_csv(csv_path, index=False)
    out_dir = tmp_path / method_name.lower()
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "detime",
            "run",
            "--method",
            method_name,
            "--series",
            str(csv_path),
            "--cols",
            "x0,x1,x2",
            "--param",
            "primary_period=12",
            "--out_dir",
            str(out_dir),
            "--output-mode",
            "summary",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout

    payload = json.loads((out_dir / "optional_panel_summary.json").read_text(encoding="utf-8"))
    assert payload["mode"] == "summary"
    assert payload["meta"]["method"] == method_name
    assert payload["meta"]["backend_used"] == "python"


def test_optional_multivariate_example_script_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, str(EXAMPLE_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "MVMD backend:" in completed.stdout
    assert "MEMD backend:" in completed.stdout
