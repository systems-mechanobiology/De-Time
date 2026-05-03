from __future__ import annotations

import argparse
from pathlib import Path
import sys
import textwrap

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "examples" / "notebooks" / "de_time_method_gallery.ipynb"


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


def _code_cell(source: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(textwrap.dedent(source).strip() + "\n")


def _markdown_cell(source: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(textwrap.dedent(source).strip() + "\n")


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

            This notebook is a GitHub-visible onboarding gallery for De-Time.
            It runs the retained method surface on compact synthetic data, plots
            components when the local environment has the needed dependencies,
            and reports skipped methods explicitly when optional upstream
            packages are unavailable.

            The gallery uses the same public objects as the docs:
            `DecompositionConfig`, `decompose`, and `MethodRegistry`.
            """
        ),
        _code_cell(
            """
            import warnings

            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            from IPython.display import display

            from detime import DecompositionConfig, MethodRegistry, decompose

            warnings.filterwarnings("ignore", category=FutureWarning)
            plt.rcParams.update({"figure.figsize": (7.2, 2.8), "axes.grid": True})
            """
        ),
        _code_cell(
            """
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
            """
        ),
        _code_cell(
            """
            def _plot_vector(values):
                arr = np.asarray(values, dtype=float)
                if arr.ndim == 2:
                    return arr[:, 0]
                return arr


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

                fig, ax = plt.subplots()
                ax.plot(original, label="input", color="#0f172a", linewidth=1.6)
                ax.plot(trend, label="trend", color="#2563eb", linewidth=1.4)
                ax.plot(season, label="season", color="#0f766e", linewidth=1.2)
                ax.plot(residual, label="residual", color="#f97316", linewidth=1.0, alpha=0.85)
                ax.set_title(f"{name} decomposition")
                ax.set_xlabel("time step")
                ax.legend(loc="upper right", ncol=2, fontsize=8)
                plt.show()
            """
        ),
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
    path = write_notebook(args.output, execute=not args.no_execute)
    print(f"wrote notebook gallery: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
