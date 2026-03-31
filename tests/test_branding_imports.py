from __future__ import annotations

import subprocess
import sys

import detime


def test_detime_public_import_surface() -> None:
    assert detime.DecompositionConfig.__name__ == "DecompositionConfig"
    assert callable(detime.decompose)
    assert isinstance(detime.native_capabilities(), dict)


def test_dual_cli_entrypoints_help() -> None:
    for module_name in ("detime", "tsdecomp"):
        proc = subprocess.run(
            [sys.executable, "-m", module_name, "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        assert "usage:" in proc.stdout.lower()
