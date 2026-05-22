from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_generated_method_matrix_and_config_reference_exist() -> None:
    matrix = (ROOT / "docs" / "method-matrix.md").read_text(encoding="utf-8")
    config = (ROOT / "docs" / "config-reference.md").read_text(encoding="utf-8")

    assert "Required/common params" in matrix
    assert "`SSA`" in matrix
    assert "`MVMD`" in matrix
    assert "Top-level fields" in config
    assert "Method-specific parameters" in config
    assert "Univariate SSA" in config
    assert '"method": "MSSA"' in config


def test_notebook_gallery_is_committed_with_outputs() -> None:
    notebook_path = ROOT / "examples" / "notebooks" / "de_time_method_gallery.ipynb"
    page = (ROOT / "docs" / "notebook-gallery.md").read_text(encoding="utf-8")
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    asset_dir = ROOT / "docs" / "assets" / "generated" / "notebooks" / "method-gallery"

    assert "de_time_method_gallery.ipynb" in page
    assert "Out:" in page
    assert "gallery-note" in page
    assert "Download Python source code" in page
    assert "assets/generated/notebooks/method-gallery/ssa.png" in page
    assert (asset_dir / "ssa.png").is_file()
    assert (asset_dir / "de_time_method_gallery.ipynb").is_file()
    assert (asset_dir / "de_time_method_gallery.py").is_file()
    assert (asset_dir / "de_time_method_gallery.zip").is_file()
    assert len(notebook["cells"]) >= 30
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert any(cell.get("outputs") for cell in code_cells)
    assert any("run_gallery_case(\"SSA\")" in "".join(cell["source"]) for cell in code_cells)
    assert any("run_gallery_case(\"GABOR_CLUSTER\")" in "".join(cell["source"]) for cell in code_cells)


def test_column_notebooks_are_rendered_with_inline_outputs() -> None:
    pairs = [
        (
            ROOT / "examples" / "notebooks" / "quant_trading" / "01_real_market_data_and_detime_features.ipynb",
            ROOT / "docs" / "tutorials" / "quant-trading" / "notebooks" / "01_real_market_data_and_detime_features.md",
        ),
        (
            ROOT / "examples" / "notebooks" / "hot_trends" / "03_huggingface_open_model_pulse.ipynb",
            ROOT / "docs" / "tutorials" / "hot-trend-lab" / "notebooks" / "03_huggingface_open_model_pulse.md",
        ),
    ]

    for notebook_path, page_path in pairs:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        page = page_path.read_text(encoding="utf-8")
        code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]

        assert any(cell.get("outputs") for cell in code_cells)
        assert "Rendered notebook transcript" in page
        assert "notebook-cell" in page
        assert "notebook-output" in page
        assert "image/png" in page
        assert '<img src="../../../../assets/generated/notebooks/columns/' in page
        assert "Visualization:" in page
        assert "```python" in page

    asset_root = ROOT / "docs" / "assets" / "generated" / "notebooks" / "columns"
    assert asset_root.is_dir()
    assert len(list((asset_root / "quant-trading").glob("**/*.png"))) >= 20
    assert len(list((asset_root / "hot-trend-lab").glob("**/*.png"))) >= 18


def test_rendered_column_notebooks_do_not_expose_local_paths() -> None:
    page_roots = [
        ROOT / "docs" / "tutorials" / "quant-trading" / "notebooks",
        ROOT / "docs" / "tutorials" / "hot-trend-lab" / "notebooks",
    ]
    banned_fragments = ["WindowsPath(", "C:/Users/", "C:\\Users\\", "OneDrive/"]

    for page_root in page_roots:
        for page_path in page_root.glob("*.md"):
            page = page_path.read_text(encoding="utf-8")
            for fragment in banned_fragments:
                assert fragment not in page, f"{page_path} exposes local path fragment {fragment}"
