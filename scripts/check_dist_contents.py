from __future__ import annotations

import argparse
import glob
import sys
import tarfile
import zipfile
from pathlib import PurePosixPath

ALLOWED_TSDECOMP_SDIST = {
    "src/tsdecomp/__init__.py",
    "src/tsdecomp/__main__.py",
    "src/tsdecomp/_compat.py",
    "src/tsdecomp/cli.py",
}

ALLOWED_TSDECOMP_WHEEL = {
    "tsdecomp/__init__.py",
    "tsdecomp/__main__.py",
    "tsdecomp/_compat.py",
    "tsdecomp/cli.py",
}

BANNED_COMMON = {
    "detime/bench_config.py",
    "detime/leaderboard.py",
}

BANNED_SDIST = {
    "src/detime/bench_config.py",
    "src/detime/leaderboard.py",
}


def _normalize_sdist_member(name: str) -> str:
    parts = PurePosixPath(name).parts
    if len(parts) <= 1:
        return ""
    return PurePosixPath(*parts[1:]).as_posix()


def _check_entries(entries: set[str], allowed_tsdecomp: set[str], banned: set[str], label: str) -> list[str]:
    failures: list[str] = []

    for path in sorted(banned):
        if path in entries:
            failures.append(f"{label}: banned path present: {path}")

    tsdecomp_entries = {entry for entry in entries if entry.startswith("tsdecomp/") or entry.startswith("src/tsdecomp/")}
    unexpected = tsdecomp_entries - allowed_tsdecomp
    missing = allowed_tsdecomp - tsdecomp_entries

    for path in sorted(unexpected):
        failures.append(f"{label}: unexpected compatibility file present: {path}")
    for path in sorted(missing):
        failures.append(f"{label}: expected compatibility file missing: {path}")

    return failures


def _inspect_sdist(path: str) -> list[str]:
    with tarfile.open(path, "r:gz") as archive:
        names = {
            normalized
            for normalized in (_normalize_sdist_member(member.name) for member in archive.getmembers())
            if normalized
        }
    return _check_entries(
        names,
        ALLOWED_TSDECOMP_SDIST,
        BANNED_SDIST,
        path,
    )


def _inspect_wheel(path: str) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        names = {name for name in archive.namelist() if not name.endswith("/")}
    return _check_entries(
        names,
        ALLOWED_TSDECOMP_WHEEL,
        BANNED_COMMON,
        path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate built wheel and sdist contents.")
    parser.add_argument("artifacts", nargs="+", help="Paths to built .whl or .tar.gz artifacts")
    args = parser.parse_args(argv)

    expanded_artifacts: list[str] = []
    for pattern in args.artifacts:
        matches = sorted(glob.glob(pattern))
        if matches:
            expanded_artifacts.extend(matches)
        else:
            expanded_artifacts.append(pattern)

    failures: list[str] = []
    for artifact in expanded_artifacts:
        if artifact.endswith(".whl"):
            failures.extend(_inspect_wheel(artifact))
        elif artifact.endswith(".tar.gz"):
            failures.extend(_inspect_sdist(artifact))
        else:
            failures.append(f"{artifact}: unsupported artifact type")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    for artifact in expanded_artifacts:
        print(f"checked {artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
