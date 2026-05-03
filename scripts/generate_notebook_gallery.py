from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import textwrap
import time
import zipfile
from pathlib import Path
from typing import Any

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
DEFAULT_OUTPUT = ROOT / "examples" / "notebooks" / "de_time_method_gallery.ipynb"
DOCS_OUTPUT = ROOT / "docs" / "notebook-gallery.md"
ASSET_DIR = ROOT / "docs" / "assets" / "generated" / "notebooks" / "method-gallery"
ASSET_NOTEBOOK = ASSET_DIR / "de_time_method_gallery.ipynb"
ASSET_SOURCE = ASSET_DIR / "de_time_method_gallery.py"
ASSET_ZIP = ASSET_DIR / "de_time_method_gallery.zip"


METHODS = [
    ("SSA", "Univariate SSA"),
    ("STD", "Seasonal-trend decomposition"),
    ("STDR", "Robust seasonal-trend decomposition"),
    ("MSSA", "Multivariate SSA"),
    ("STL", "Statsmodels STL wrapper"),
    ("MSTL", "Statsmodels MSTL wrapper"),
    ("ROBUST_STL", "Robust STL wrapper"),
    ("EMD", "Empirical mode decomposition"),
    ("CEEMDAN", "Noise-assisted EMD"),
    ("VMD", "Variational mode decomposition"),
    ("WAVELET", "Wavelet decomposition"),
    ("MA_BASELINE", "Moving-average baseline"),
    ("MVMD", "Optional multivariate VMD backend"),
    ("MEMD", "Optional multivariate EMD backend"),
    ("GABOR_CLUSTER", "Experimental Gabor clustering path"),
]


SETUP_CODE = r'''
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display

# Prefer the checkout when this notebook is run inside the repository.
repo_src = Path.cwd() / "src"
if (repo_src / "detime").exists():
    sys.meta_path[:] = [
        finder for finder in sys.meta_path
        if finder.__class__.__module__ != "_de_time_editable"
    ]
    sys.path.insert(0, str(repo_src))

from detime import DecompositionConfig, MethodRegistry, decompose

warnings.filterwarnings("ignore", category=FutureWarning)
plt.rcParams.update(
    {
        "figure.figsize": (7.6, 3.0),
        "figure.dpi": 130,
        "savefig.dpi": 220,
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    }
)

rng = np.random.default_rng(42)
t = np.arange(96, dtype=float)
seasonal = np.sin(2.0 * np.pi * t / 12.0)
slow = 0.018 * t + 0.25 * np.sin(2.0 * np.pi * t / 48.0)
noise = 0.05 * rng.standard_normal(t.shape)
series = slow + seasonal + noise
panel = np.column_stack(
    [
        series,
        0.8 * slow + np.sin(2.0 * np.pi * (t + 2.0) / 12.0) + 0.04 * rng.standard_normal(t.shape),
        1.15 * slow + 0.7 * np.sin(2.0 * np.pi * (t + 4.0) / 12.0) + 0.04 * rng.standard_normal(t.shape),
    ]
)

CASES = {
    "SSA": {"data": series, "config": {"method": "SSA", "params": {"window": 24, "rank": 6, "primary_period": 12}, "backend": "auto", "speed_mode": "exact"}},
    "STD": {"data": series, "config": {"method": "STD", "params": {"period": 12}, "backend": "auto"}},
    "STDR": {"data": series, "config": {"method": "STDR", "params": {"period": 12}, "backend": "auto"}},
    "MSSA": {"data": panel, "config": {"method": "MSSA", "params": {"window": 24, "rank": 6, "primary_period": 12}, "backend": "python", "channel_names": ["a", "b", "c"]}},
    "STL": {"data": series, "config": {"method": "STL", "params": {"period": 12}}},
    "MSTL": {"data": series, "config": {"method": "MSTL", "params": {"periods": [12, 24]}}},
    "ROBUST_STL": {"data": series, "config": {"method": "ROBUST_STL", "params": {"period": 12}}},
    "EMD": {"data": series, "config": {"method": "EMD", "params": {"primary_period": 12, "n_imfs": 4}}},
    "CEEMDAN": {"data": series, "config": {"method": "CEEMDAN", "params": {"primary_period": 12, "trials": 3, "noise_width": 0.03}}},
    "VMD": {"data": series, "config": {"method": "VMD", "params": {"K": 4, "alpha": 300.0, "primary_period": 12}}},
    "WAVELET": {"data": series, "config": {"method": "WAVELET", "params": {"wavelet": "db4", "level": 3}}},
    "MA_BASELINE": {"data": series, "config": {"method": "MA_BASELINE", "params": {"trend_window": 7, "season_period": 12}}},
    "MVMD": {"data": panel, "config": {"method": "MVMD", "params": {"K": 4, "alpha": 300.0, "primary_period": 12}, "channel_names": ["a", "b", "c"]}},
    "MEMD": {"data": panel, "config": {"method": "MEMD", "params": {"primary_period": 12}, "channel_names": ["a", "b", "c"]}},
    "GABOR_CLUSTER": {"data": series, "skip": "requires a trained GaborClusterModel or model_path plus the experimental clustering backend"},
}

GALLERY_RESULTS = []
'''


HELPER_CODE = r'''
def _plot_vector(values):
    arr = np.asarray(values, dtype=float)
    if arr.ndim == 2:
        return arr[:, 0]
    return arr


def _style_gallery_axis(ax, title):
    ax.set_facecolor("#ffffff")
    ax.grid(True, axis="y", alpha=0.22, color="#94a3b8", linewidth=0.8)
    ax.grid(False, axis="x")
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(colors="#334155")
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color="#0f172a")


def run_gallery_case(name):
    case = CASES[name]
    metadata = MethodRegistry.get_metadata(name)
    print(f"{name}: {metadata['summary']}")
    if "skip" in case:
        row = {
            "method": name,
            "status": "skipped",
            "reason": case["skip"],
            "input_mode": metadata["input_mode"],
            "output_shape": "",
            "residual_rmse": np.nan,
        }
        GALLERY_RESULTS.append(row)
        display(pd.DataFrame([row]))
        return

    data = case["data"]
    cfg = DecompositionConfig(**case["config"])
    try:
        result = decompose(data, cfg)
    except Exception as exc:
        row = {
            "method": name,
            "status": "skipped",
            "reason": f"{type(exc).__name__}: {exc}",
            "input_mode": metadata["input_mode"],
            "output_shape": "",
            "residual_rmse": np.nan,
        }
        GALLERY_RESULTS.append(row)
        display(pd.DataFrame([row]))
        return

    original = _plot_vector(data)
    trend = _plot_vector(result.trend)
    season = _plot_vector(result.season)
    residual = _plot_vector(result.residual)
    reconstruction = trend + season + residual
    rmse = float(np.sqrt(np.mean((original - reconstruction) ** 2)))

    row = {
        "method": name,
        "status": "ran",
        "reason": "",
        "input_mode": metadata["input_mode"],
        "output_shape": str(np.asarray(result.trend).shape),
        "residual_rmse": round(rmse, 8),
    }
    GALLERY_RESULTS.append(row)
    display(pd.DataFrame([row]))

    fig, ax = plt.subplots(facecolor="#f8fafc")
    ax.plot(original, label="input", color="#0f172a", linewidth=1.6)
    ax.plot(trend, label="trend", color="#2563eb", linewidth=1.4)
    ax.plot(season, label="season", color="#0f766e", linewidth=1.2)
    ax.plot(residual, label="residual", color="#f97316", linewidth=1.0, alpha=0.85)
    _style_gallery_axis(ax, f"{name} decomposition")
    ax.set_xlabel("time step")
    ax.legend(loc="upper right", ncol=2, fontsize=8, frameon=True, framealpha=0.92)
    fig.tight_layout()
    plt.show()
'''


def _dedent(source: str) -> str:
    return textwrap.dedent(source).strip() + "\n"


def _prefer_repo_source() -> None:
    """Avoid stale local editable wheels when regenerating docs assets."""
    import sys

    sys.meta_path[:] = [
        finder for finder in sys.meta_path
        if finder.__class__.__module__ != "_de_time_editable"
    ]
    src = str(SRC_DIR)
    if src not in sys.path:
        sys.path.insert(0, src)


def _code_cell(source: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(_dedent(source))


def _markdown_cell(source: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(_dedent(source))


def _case_code(name: str) -> str:
    if name == "GABOR_CLUSTER":
        return f'case = CASES["{name}"]\nprint(case["skip"])'
    return f'case = CASES["{name}"]\nrun_gallery_case("{name}")'


def build_notebook() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    nb.metadata.update(
        {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        }
    )

    cells: list[nbformat.NotebookNode] = [
        _markdown_cell(
            """
            # De-Time Method Gallery

            This notebook is a runnable onboarding gallery for the retained
            De-Time method surface. Each section uses the public
            `DecompositionConfig`, `decompose`, and `MethodRegistry` objects.
            """
        ),
        _code_cell(SETUP_CODE),
        _code_cell(HELPER_CODE),
    ]

    for method, title in METHODS:
        cells.extend(
            [
                _markdown_cell(f"## `{method}` - {title}"),
                _code_cell(f'run_gallery_case("{method}")'),
            ]
        )

    cells.extend(
        [
            _markdown_cell("## Summary"),
            _code_cell(
                """
                summary = pd.DataFrame(GALLERY_RESULTS)
                display(summary)
                ran = int((summary["status"] == "ran").sum())
                skipped = int((summary["status"] == "skipped").sum())
                print(f"Methods run: {ran}; skipped with explicit reason: {skipped}")
                """
            ),
        ]
    )
    nb.cells = cells
    return nb


def write_notebook(path: Path, *, execute: bool) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    notebook = build_notebook()
    if execute:
        client = NotebookClient(
            notebook,
            timeout=180,
            kernel_name="python3",
            allow_errors=False,
            resources={"metadata": {"path": str(ROOT)}},
        )
        client.execute()
    nbformat.write(notebook, path)
    return path


def _plot_vector(values: Any):
    import numpy as np

    arr = np.asarray(values, dtype=float)
    if arr.ndim == 2:
        return arr[:, 0]
    return arr


def _render_case_asset(name: str, case: dict[str, Any], asset_dir: Path) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    _prefer_repo_source()
    from detime import DecompositionConfig, MethodRegistry, decompose

    metadata = MethodRegistry.get_metadata(name)
    if "skip" in case:
        return {
            "method": name,
            "status": "skipped",
            "stdout": case["skip"],
            "image": None,
            "input_mode": metadata["input_mode"],
            "shape": "",
            "residual_rmse": "",
        }

    np.random.seed(42)
    try:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            result = decompose(case["data"], DecompositionConfig(**case["config"]))
    except Exception as exc:
        return {
            "method": name,
            "status": "skipped",
            "stdout": f"{type(exc).__name__}: {exc}",
            "image": None,
            "input_mode": metadata["input_mode"],
            "shape": "",
            "residual_rmse": "",
        }

    original = _plot_vector(case["data"])
    trend = _plot_vector(result.trend)
    season = _plot_vector(result.season)
    residual = _plot_vector(result.residual)
    rmse = float(np.sqrt(np.mean((original - trend - season - residual) ** 2)))
    image_name = f"{name.lower()}.png"
    image_path = asset_dir / image_name

    fig, ax = plt.subplots(figsize=(8.8, 3.2), facecolor="#f8fafc", layout="constrained")
    ax.set_facecolor("#ffffff")
    ax.plot(original, label="input", color="#111827", linewidth=1.7)
    ax.plot(trend, label="trend", color="#2563eb", linewidth=1.55)
    ax.plot(season, label="season", color="#0f766e", linewidth=1.3)
    ax.plot(residual, label="residual", color="#f97316", linewidth=1.05, alpha=0.9)
    ax.set_title(f"{name} decomposition", loc="left", fontsize=13, fontweight="bold", color="#0f172a")
    ax.set_xlabel("time step")
    ax.grid(True, axis="y", alpha=0.22, color="#94a3b8")
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", ncol=2, fontsize=8, frameon=True, framealpha=0.92)
    fig.savefig(image_path, dpi=220, bbox_inches="tight")
    plt.close(fig)

    stdout = "\n".join(
        [
            f"{name}: {metadata['summary']}",
            f"status: ran",
            f"input mode: {metadata['input_mode']}",
            f"trend shape: {np.asarray(result.trend).shape}",
            f"backend: {result.meta.get('backend_used', 'python')}",
            f"residual RMSE: {rmse:.8f}",
        ]
    )
    return {
        "method": name,
        "status": "ran",
        "stdout": stdout,
        "image": image_name,
        "input_mode": metadata["input_mode"],
        "shape": str(np.asarray(result.trend).shape),
        "residual_rmse": f"{rmse:.8f}",
    }


def _runtime_namespace() -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    exec(_dedent(SETUP_CODE), namespace)
    return namespace


def _write_source() -> Path:
    lines = [
        "# Generated from scripts/generate_notebook_gallery.py.",
        _dedent(SETUP_CODE),
        _dedent(HELPER_CODE),
        "",
    ]
    for method, _ in METHODS:
        lines.append(f'run_gallery_case("{method}")')
    lines.extend(
        [
            "",
            "summary = pd.DataFrame(GALLERY_RESULTS)",
            "print(summary)",
        ]
    )
    ASSET_SOURCE.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return ASSET_SOURCE


def _write_zip() -> Path:
    with zipfile.ZipFile(ASSET_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(ASSET_NOTEBOOK, ASSET_NOTEBOOK.name)
        archive.write(ASSET_SOURCE, ASSET_SOURCE.name)
    return ASSET_ZIP


def write_markdown_gallery() -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    namespace = _runtime_namespace()
    cases: dict[str, dict[str, Any]] = namespace["CASES"]
    start = time.perf_counter()
    rows = [_render_case_asset(method, cases[method], ASSET_DIR) for method, _ in METHODS]
    elapsed = time.perf_counter() - start

    lines = [
        "# De-Time Method Gallery",
        "",
        '<div class="gallery-note">',
        '  <strong>Note</strong><br>',
        '  <a href="#download-gallery">Go to the end</a> to download the full notebook, Python source, or zipped example.',
        "</div>",
        "",
        "This gallery follows the same pattern as a Sphinx-Gallery example page:",
        "short explanation, executable code blocks, printed output, figures, and",
        "download links. The examples use compact synthetic data so they run quickly",
        "in docs builds and local checkouts.",
        "",
        "Regenerate this page and its assets with `python scripts/generate_notebook_gallery.py`.",
        "",
        "## Imports and synthetic data",
        "",
        "```python",
        _dedent(SETUP_CODE).strip(),
        "```",
        "",
        "```python",
        _dedent(HELPER_CODE).strip(),
        "```",
        "",
    ]

    for (method, title), row in zip(METHODS, rows):
        lines.extend(
            [
                f"## {title}",
                "",
                "```python",
                _case_code(method),
                "```",
                "",
                "Out:",
                "",
                '<div class="gallery-out">',
                "<pre>",
                row["stdout"],
                "</pre>",
                "</div>",
                "",
            ]
        )
        if row["image"]:
            lines.extend(
                [
                    f"![{method} decomposition](assets/generated/notebooks/method-gallery/{row['image']})",
                    "",
                ]
            )

    ran = sum(1 for row in rows if row["status"] == "ran")
    skipped = len(rows) - ran
    lines.extend(
        [
            "## Summary",
            "",
            "| Method | Status | Input mode | Trend shape | Residual RMSE |",
            "|---|---|---|---|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['method']}` | {row['status']} | `{row['input_mode']}` | `{row['shape']}` | {row['residual_rmse'] or 'n/a'} |"
        )
    lines.extend(
        [
            "",
            f"Total running time of the gallery script: {elapsed:.3f} seconds.",
            "",
            f"Methods run: {ran}; skipped with explicit reason: {skipped}.",
            "",
            '<a id="download-gallery"></a>',
            "",
            "## Downloads",
            "",
            '<div class="download-grid">',
            '  <a class="download-card" href="../assets/generated/notebooks/method-gallery/de_time_method_gallery.ipynb">Download Jupyter notebook: <code>de_time_method_gallery.ipynb</code></a>',
            '  <a class="download-card" href="../assets/generated/notebooks/method-gallery/de_time_method_gallery.py">Download Python source code: <code>de_time_method_gallery.py</code></a>',
            '  <a class="download-card" href="../assets/generated/notebooks/method-gallery/de_time_method_gallery.zip">Download zipped example: <code>de_time_method_gallery.zip</code></a>',
            "</div>",
            "",
            "The GitHub-rendered notebook is also available at",
            "[examples/notebooks/de_time_method_gallery.ipynb](https://github.com/systems-mechanobiology/De-Time/blob/main/examples/notebooks/de_time_method_gallery.ipynb).",
            "",
        ]
    )
    DOCS_OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    return DOCS_OUTPUT


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the De-Time notebook method gallery.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Notebook output path.",
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Write the notebook without executing cells.",
    )
    args = parser.parse_args()

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    notebook_path = write_notebook(args.output, execute=not args.no_execute)
    shutil.copy2(notebook_path, ASSET_NOTEBOOK)
    _write_source()
    markdown_path = write_markdown_gallery()
    _write_zip()
    print(f"wrote notebook gallery: {notebook_path}")
    print(f"wrote docs gallery: {markdown_path}")
    print(f"wrote gallery assets: {ASSET_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
