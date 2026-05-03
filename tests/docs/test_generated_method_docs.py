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
