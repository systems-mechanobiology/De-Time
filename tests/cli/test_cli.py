from __future__ import annotations

from argparse import Namespace

import numpy as np
import pytest

import detime.cli as cli
from detime.core import DecompResult


class FakeConfig:
    model_fields = {
        "method": object(),
        "params": object(),
        "backend": object(),
        "speed_mode": object(),
        "n_jobs": object(),
        "profile": object(),
        "device": object(),
    }

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_backend_selection_passes_flags(monkeypatch, tmp_path):
    captured = {}

    def fake_read_series(series, col=None, cols=None):
        captured["read_cols"] = cols
        return np.asarray([1.0, 2.0, 3.0], dtype=float)

    def fake_decompose(series, cfg):
        captured["cfg"] = cfg
        return DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", None)},
        )

    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    monkeypatch.setattr(cli, "read_series", fake_read_series)
    monkeypatch.setattr(cli, "decompose", fake_decompose)
    monkeypatch.setattr(cli, "save_result", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_components", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_error", lambda *args, **kwargs: None)

    args = Namespace(
        method="SSA",
        series="input.csv",
        col=None,
        cols=None,
        param=["window=8"],
        backend="native",
        speed_mode="fast",
        n_jobs=4,
        profile=True,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        plot=False,
    )

    cli.cmd_run(args)

    cfg = captured["cfg"]
    assert cfg.backend == "native"
    assert cfg.speed_mode == "fast"
    assert cfg.n_jobs == 4
    assert cfg.profile is True
    assert cfg.method == "SSA"
    assert cfg.params == {"window": 8}
    assert captured["read_cols"] is None


def test_profile_command_writes_report(monkeypatch, tmp_path, capsys):
    report_path = tmp_path / "profile.json"
    monkeypatch.setattr(
        cli,
        "run_profile",
        lambda **kwargs: {
            "method": kwargs["method"],
            "backend_requested": kwargs["backend"],
            "backend_used": kwargs["backend"],
            "speed_mode": kwargs["speed_mode"],
            "repeat": kwargs["repeat"],
            "warmup": kwargs["warmup"],
            "samples_ms": [1.0, 2.0],
            "summary": {
                "min_ms": 1.0,
                "mean_ms": 1.5,
                "median_ms": 1.5,
                "p95_ms": 2.0,
                "stdev_ms": 0.5,
            },
        },
    )

    import sys

    old_argv = sys.argv
    sys.argv = [
        "detime",
        "profile",
        "--method",
        "SSA",
        "--series",
        "input.csv",
        "--backend",
        "native",
        "--speed-mode",
        "fast",
        "--repeat",
        "2",
        "--warmup",
        "1",
        "--output",
        str(report_path),
    ]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert "Profile report written" in captured.out
    assert report_path.exists()


def test_run_command_accepts_multivariate_cols(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    captured = {}

    def fake_read_series(series, col=None, cols=None):
        captured["col"] = col
        captured["cols"] = cols
        return np.column_stack(
            [
                np.asarray([1.0, 2.0, 3.0], dtype=float),
                np.asarray([4.0, 5.0, 6.0], dtype=float),
            ]
        )

    monkeypatch.setattr(cli, "read_series", fake_read_series)
    monkeypatch.setattr(
        cli,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", "auto"), "n_channels": series.shape[1]},
        ),
    )
    monkeypatch.setattr(cli, "save_result", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_components", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_error", lambda *args, **kwargs: None)

    args = Namespace(
        method="MSSA",
        series="input.csv",
        col=None,
        cols="a,b",
        param=["window=8"],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        profile=False,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        plot=False,
    )

    cli.cmd_run(args)

    assert captured["col"] is None
    assert captured["cols"] == ["a", "b"]


def test_run_command_rejects_multivariate_plotting(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    monkeypatch.setattr(
        cli,
        "read_series",
        lambda series, col=None, cols=None: np.column_stack(
            [
                np.asarray([1.0, 2.0, 3.0], dtype=float),
                np.asarray([4.0, 5.0, 6.0], dtype=float),
            ]
        ),
    )
    monkeypatch.setattr(
        cli,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", "auto"), "result_layout": "multivariate"},
        ),
    )
    monkeypatch.setattr(cli, "save_result", lambda *args, **kwargs: None)

    args = Namespace(
        method="MSSA",
        series="input.csv",
        col=None,
        cols="a,b",
        param=["window=8"],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        profile=False,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        plot=True,
    )

    with pytest.raises((ValueError, NotImplementedError), match="plot|multivariate|2D"):
        cli.cmd_run(args)


def test_run_command_passes_output_mode_and_fields(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    monkeypatch.setattr(
        cli,
        "read_series",
        lambda series, col=None, cols=None: np.asarray([1.0, 2.0, 3.0], dtype=float),
    )
    monkeypatch.setattr(
        cli,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": "python"},
        ),
    )
    captured = {}
    monkeypatch.setattr(
        cli,
        "save_result",
        lambda result, out_dir, name, **kwargs: captured.update(
            {"out_dir": out_dir, "name": name, **kwargs}
        ),
    )

    args = Namespace(
        method="SSA",
        series="input.csv",
        col=None,
        cols=None,
        param=[],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        profile=False,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        output_mode="summary",
        fields="meta,diagnostics",
        plot=False,
    )

    cli.cmd_run(args)

    assert captured["output_mode"] == "summary"
    assert captured["fields"] == ["meta", "diagnostics"]


def test_schema_command_prints_json(capsys):
    import sys

    old_argv = sys.argv
    sys.argv = ["detime", "schema", "--name", "config"]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert '"title"' in captured.out
    assert "DecompositionConfig" in captured.out


def test_recommend_command_outputs_json(capsys):
    import sys

    old_argv = sys.argv
    sys.argv = [
        "detime",
        "recommend",
        "--length",
        "128",
        "--channels",
        "2",
        "--prefer",
        "accuracy",
    ]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert '"recommendations"' in captured.out
    assert "MSSA" in captured.out
