from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ASSET_DIR = SRC / "detime" / "schema_assets"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detime.schemas import SCHEMA_FILENAMES, build_schema_bundle, write_schema_assets


def _check_schema_assets() -> int:
    bundle = build_schema_bundle()
    failures: list[str] = []
    for name, filename in SCHEMA_FILENAMES.items():
        path = ASSET_DIR / filename
        if not path.exists():
            failures.append(f"missing schema asset: {path}")
            continue
        actual = json.loads(path.read_text(encoding="utf-8"))
        if actual != bundle[name]:
            failures.append(f"stale schema asset: {path}")
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"schema assets match generated bundle in {ASSET_DIR}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify packaged schema assets.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the checked-in schema assets do not match the live Pydantic models.",
    )
    args = parser.parse_args()
    if args.check:
        return _check_schema_assets()
    written = write_schema_assets(ASSET_DIR)
    for name, path in written.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
