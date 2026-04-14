from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_generate_tutorial_assets_smoke(tmp_path) -> None:
    output_root = tmp_path / "tutorial-assets"
    env = os.environ.copy()
    src_dir = ROOT / "src"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_dir) if not existing else os.pathsep.join([str(src_dir), existing])

    completed = subprocess.run(
        [sys.executable, "scripts/generate_tutorial_assets.py", "--output-root", str(output_root)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "wrote tutorial assets" in completed.stdout
    assert (output_root / "visual-univariate" / "ssa_components.png").exists()
    assert (output_root / "visual-multivariate" / "multivariate_summary.csv").exists()
    assert (output_root / "visual-comparison" / "comparison_summary.csv").exists()
    assert (output_root / "univariate" / "method_snapshot.json").exists()
    assert (output_root / "cli-and-profiling" / "single-file" / "example_series_summary.json").exists()
    assert (output_root / "cli-and-profiling" / "single-file" / "example_series_plot.png").exists()
    assert (output_root / "cli-and-profiling" / "multivariate" / "example_multivariate_summary.json").exists()
    assert (output_root / "cli-and-profiling" / "batch" / "series_a_meta.json").exists()
    assert (output_root / "cli-and-profiling" / "profile" / "ssa_profile_text.txt").exists()
    assert (output_root / "cli-and-profiling" / "profile" / "std_native.txt").exists()
    assert (output_root / "cli-and-profiling" / "machine" / "method_registry_schema.json").exists()
