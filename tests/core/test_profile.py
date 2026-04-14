from __future__ import annotations

import numpy as np

import detime.profile as profile
from detime.core import DecompResult


class FakeConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_profile_output_structure(monkeypatch, tmp_path):
    monkeypatch.setattr(profile, "DecompositionConfig", FakeConfig)
    monkeypatch.setattr(
        profile,
        "read_series",
        lambda series, col=None, cols=None: np.asarray([1.0, 2.0, 3.0], dtype=float),
    )
    monkeypatch.setattr(
        profile,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", "auto")},
        ),
    )

    ticks = iter([1.0, 1.01, 2.0, 2.03, 3.0, 3.04, 4.0, 4.05, 5.0, 5.06, 6.0, 6.07])
    monkeypatch.setattr(profile.time, "perf_counter", lambda: next(ticks))

    report = profile.run_profile(
        series="input.csv",
        method="SSA",
        params={"window": 8},
        backend="native",
        speed_mode="fast",
        n_jobs=2,
        repeat=3,
        warmup=1,
    )

    assert report["method"] == "SSA"
    assert report["backend_requested"] == "native"
    assert report["backend_used"] == "native"
    assert report["repeat"] == 3
    assert report["warmup"] == 1
    assert len(report["samples_ms"]) == 3
    assert set(report["summary"]) == {"min_ms", "mean_ms", "median_ms", "p95_ms", "stdev_ms"}

    json_text = profile.format_profile_report(report, fmt="json")
    assert '"method": "SSA"' in json_text

    out_file = tmp_path / "profile.txt"
    profile.write_profile_report(report, out_file, fmt="text")
    text = out_file.read_text(encoding="utf-8")
    assert "backend_requested=native" in text


def test_profile_supports_multivariate_cols(monkeypatch):
    captured = {}
    monkeypatch.setattr(profile, "DecompositionConfig", FakeConfig)

    def fake_read_series(series, col=None, cols=None):
        captured["col"] = col
        captured["cols"] = cols
        return np.column_stack(
            [
                np.asarray([1.0, 2.0, 3.0], dtype=float),
                np.asarray([4.0, 5.0, 6.0], dtype=float),
            ]
        )

    monkeypatch.setattr(profile, "read_series", fake_read_series)
    monkeypatch.setattr(
        profile,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", "auto"), "n_channels": series.shape[1]},
        ),
    )

    ticks = iter([10.0, 10.01, 11.0, 11.03, 12.0, 12.05])
    monkeypatch.setattr(profile.time, "perf_counter", lambda: next(ticks))

    report = profile.run_profile(
        series="input.csv",
        method="MSSA",
        params={"window": 8},
        col=None,
        cols=["a", "b"],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        repeat=2,
        warmup=0,
    )

    assert captured["col"] is None
    assert captured["cols"] == ["a", "b"]
    assert report["backend_requested"] == "python"
    assert report["backend_used"] == "python"
    assert report["repeat"] == 2
    assert len(report["samples_ms"]) == 2
