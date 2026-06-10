from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = ROOT / "site"
DEFAULT_OUT_DIR = ROOT / "dist-hf-space"


README = """---
title: DeTime
colorFrom: blue
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
---

# DeTime

DeTime is a time-series decomposition Python package and CLI workflow layer for
reproducible trend, oscillation, residual, component, and metadata extraction.

- Canonical documentation: https://systems-mechanobiology.github.io/DeTime/
- Source code: https://github.com/systems-mechanobiology/DeTime
- Python import: `detime`
- Distribution name: `de-time`

This Hugging Face Space is a static mirror of the DeTime documentation site.
The GitHub Pages URL remains the canonical documentation URL for search engines.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a Hugging Face Static Space from the built MkDocs site.")
    parser.add_argument("--site-dir", type=Path, default=DEFAULT_SITE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    site_dir = args.site_dir.resolve()
    out_dir = args.out_dir.resolve()
    if not (site_dir / "index.html").exists():
        raise SystemExit(f"Build the docs first; missing {site_dir / 'index.html'}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(site_dir, out_dir)
    (out_dir / "README.md").write_text(README, encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
