from __future__ import annotations

import importlib
from importlib.machinery import PathFinder
import os
from pathlib import Path
import subprocess
import sys

import pytest

import detime


def _subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    src_root = str(Path(detime.__file__).resolve().parents[1])
    env["PYTHONPATH"] = src_root
    return env


def test_tsdecomp_import_warns_and_reexports() -> None:
    for name in list(sys.modules):
        if name == "tsdecomp" or name.startswith("tsdecomp."):
            sys.modules.pop(name)

    with pytest.warns(DeprecationWarning, match="tsdecomp"):
        legacy = importlib.import_module("tsdecomp")

    assert legacy.DecompositionConfig is detime.DecompositionConfig
    assert callable(legacy.decompose)
    assert {"DR_TS_REG", "DR_TS_AE", "SL_LIB"}.isdisjoint(set(legacy.MethodRegistry.list_methods()))


def test_removed_legacy_modules_are_not_packaged() -> None:
    legacy = importlib.import_module("tsdecomp")

    for module_name in (
        "tsdecomp.backends",
        "tsdecomp.bench_config",
        "tsdecomp.core",
        "tsdecomp.io",
        "tsdecomp.leaderboard",
        "tsdecomp.metrics",
        "tsdecomp.profile",
        "tsdecomp.registry",
        "tsdecomp.viz",
        "tsdecomp.methods",
    ):
        assert PathFinder.find_spec(module_name, legacy.__path__) is None


def test_dual_cli_entrypoints_help() -> None:
    for module_name in ("detime", "tsdecomp"):
        proc = subprocess.run(
            [sys.executable, "-m", module_name, "--help"],
            check=False,
            capture_output=True,
            text=True,
            env=_subprocess_env(),
        )
        assert proc.returncode == 0, proc.stderr
        assert "usage:" in proc.stdout.lower()


def test_tsdecomp_version_command_emits_notice() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "tsdecomp", "version"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert proc.returncode == 0, proc.stderr
    assert "DeprecationWarning" in proc.stderr
    assert proc.stdout.strip()
