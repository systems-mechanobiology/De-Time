from __future__ import annotations

import base64
import html
import os
import re
import shutil
from pathlib import Path
from typing import Any

import nbformat


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
GITHUB_BLOB_ROOT = "https://github.com/systems-mechanobiology/De-Time/blob/main"

COLUMNS = [
    {
        "key": "quant-trading",
        "label": "Quant Trading",
        "notebook_dir": ROOT / "examples" / "notebooks" / "quant_trading",
        "docs_dir": DOCS_DIR / "tutorials" / "quant-trading" / "notebooks",
        "asset_dir": DOCS_DIR / "assets" / "generated" / "notebooks" / "columns" / "quant-trading",
    },
    {
        "key": "hot-trend-lab",
        "label": "Hot Trend Lab",
        "notebook_dir": ROOT / "examples" / "notebooks" / "hot_trends",
        "docs_dir": DOCS_DIR / "tutorials" / "hot-trend-lab" / "notebooks",
        "asset_dir": DOCS_DIR / "assets" / "generated" / "notebooks" / "columns" / "hot-trend-lab",
    },
]


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

NOTEBOOK_INDEX_INTROS = {
    "quant-trading": (
        "These pages render the Quant Trading notebooks as documentation pages, "
        "including markdown notes, code cells, stdout, tables, and captured figures."
    ),
    "hot-trend-lab": (
        "These pages render the Hot Trend Lab notebooks as documentation pages, "
        "including markdown notes, code cells, stdout, tables, and captured figures."
    ),
}


def _cell_source(cell: nbformat.NotebookNode) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(source)
    return str(source)


def _mime_value(data: dict[str, Any], mime_type: str) -> str | None:
    value = data.get(mime_type)
    if value is None:
        return None
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return str(value)


def _markdown_title(notebook: nbformat.NotebookNode, fallback: str) -> str:
    for cell in notebook.cells:
        if cell.get("cell_type") != "markdown":
            continue
        for line in _cell_source(cell).splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
    return fallback.replace("_", " ").replace("-", " ").title()


def _strip_duplicate_h1(markdown: str, title: str) -> str:
    lines = markdown.splitlines()
    if not lines:
        return markdown
    first = lines[0].strip()
    if first == f"# {title}":
        return "\n".join(lines[1:]).lstrip()
    return markdown


def _code_fence(source: str, language: str = "") -> str:
    fence = "````" if "```" in source else "```"
    suffix = language if language else ""
    return f"{fence}{suffix}\n{source.rstrip()}\n{fence}"


def _relative_link(target: Path, source_dir: Path) -> str:
    return os.path.relpath(target, source_dir).replace(os.sep, "/")


def _write_image_output(
    *,
    png_data: str,
    output_index: int,
    cell_index: int,
    page_path: Path,
    notebook_asset_dir: Path,
    alt: str,
) -> str:
    notebook_asset_dir.mkdir(parents=True, exist_ok=True)
    image_path = notebook_asset_dir / f"cell-{cell_index:03d}-output-{output_index:02d}.png"
    image_path.write_bytes(base64.b64decode(png_data))
    # MkDocs serves each markdown page as page-name/index.html when directory URLs
    # are enabled, so raw HTML asset URLs need one more parent hop than markdown
    # source-relative links.
    src = html.escape("../" + _relative_link(image_path, page_path.parent), quote=True)
    alt_text = html.escape(alt, quote=True)
    return f'<img src="{src}" alt="{alt_text}" class="notebook-output-image">'


def _render_output(
    *,
    output: nbformat.NotebookNode,
    output_index: int,
    cell_index: int,
    page_path: Path,
    notebook_asset_dir: Path,
) -> list[str]:
    output_type = output.get("output_type", "")
    pieces: list[str] = []

    if output_type == "stream":
        text = output.get("text", "")
        if isinstance(text, list):
            text = "".join(text)
        cleaned = ANSI_RE.sub("", str(text)).rstrip()
        if cleaned:
            pieces.extend(
                [
                    '<div class="notebook-output-label">stdout</div>',
                    _code_fence(cleaned, "text"),
                ]
            )
        return pieces

    if output_type in {"execute_result", "display_data"}:
        data = output.get("data", {})
        html_value = _mime_value(data, "text/html")
        png_value = _mime_value(data, "image/png")
        svg_value = _mime_value(data, "image/svg+xml")
        text_value = _mime_value(data, "text/plain")

        if png_value:
            pieces.extend(
                [
                    '<div class="notebook-output-label">image/png</div>',
                    _write_image_output(
                        png_data=png_value,
                        output_index=output_index,
                        cell_index=cell_index,
                        page_path=page_path,
                        notebook_asset_dir=notebook_asset_dir,
                        alt=f"Notebook output cell {cell_index}",
                    ),
                ]
            )
        elif html_value:
            pieces.extend(
                [
                    '<div class="notebook-output-label">text/html</div>',
                    '<div class="notebook-html-output">',
                    html_value,
                    "</div>",
                ]
            )
        elif svg_value:
            pieces.extend(
                [
                    '<div class="notebook-output-label">image/svg+xml</div>',
                    '<div class="notebook-svg-output">',
                    svg_value,
                    "</div>",
                ]
            )
        elif text_value:
            cleaned = ANSI_RE.sub("", text_value).rstrip()
            if cleaned:
                pieces.extend(
                    [
                        '<div class="notebook-output-label">text/plain</div>',
                        _code_fence(cleaned, "text"),
                    ]
                )
        return pieces

    if output_type == "error":
        ename = output.get("ename", "Error")
        evalue = output.get("evalue", "")
        traceback = output.get("traceback", [])
        if isinstance(traceback, list):
            text = "\n".join(str(line) for line in traceback)
        else:
            text = str(traceback)
        cleaned = ANSI_RE.sub("", text).rstrip()
        pieces.extend(
            [
                f'<div class="notebook-output-label notebook-error-label">{html.escape(str(ename))}: {html.escape(str(evalue))}</div>',
                _code_fence(cleaned, "text"),
            ]
        )
    return pieces


def _render_code_cell(
    *,
    cell: nbformat.NotebookNode,
    cell_index: int,
    page_path: Path,
    notebook_asset_dir: Path,
) -> str:
    execution_count = cell.get("execution_count")
    count_label = "" if execution_count is None else str(execution_count)
    source = _cell_source(cell).rstrip()
    lines = [
        '<div class="notebook-cell">',
        f'<div class="notebook-input-label">In [{count_label}]</div>',
        "",
        _code_fence(source, "python"),
    ]

    output_blocks: list[str] = []
    for output_index, output in enumerate(cell.get("outputs", []), start=1):
        rendered = _render_output(
            output=output,
            output_index=output_index,
            cell_index=cell_index,
            page_path=page_path,
            notebook_asset_dir=notebook_asset_dir,
        )
        if rendered:
            output_blocks.extend(rendered)

    if output_blocks:
        lines.extend(
            [
                "",
                '<div class="gallery-out notebook-output">',
                *output_blocks,
                "</div>",
            ]
        )

    lines.append("</div>")
    return "\n".join(lines)


def render_notebook_page(column: dict[str, Path | str], notebook_path: Path) -> tuple[Path, str]:
    notebook = nbformat.read(notebook_path, as_version=4)
    page_path = Path(column["docs_dir"]) / f"{notebook_path.stem}.md"
    notebook_asset_dir = Path(column["asset_dir"]) / notebook_path.stem
    page_path.parent.mkdir(parents=True, exist_ok=True)
    if notebook_asset_dir.exists():
        shutil.rmtree(notebook_asset_dir)

    title = _markdown_title(notebook, notebook_path.stem)
    source_rel = notebook_path.relative_to(ROOT).as_posix()
    source_url = f"{GITHUB_BLOB_ROOT}/{source_rel}"

    lines = [
        "<!-- Generated by scripts/generate_column_notebook_pages.py; do not edit manually. -->",
        f"# {title}",
        "",
        '<div class="gallery-note notebook-transcript-note">',
        f'  <strong>Rendered notebook transcript.</strong> This page is generated from <a href="{source_url}"><code>{source_rel}</code></a> and includes code cells plus captured outputs from the committed notebook.',
        "</div>",
        "",
    ]

    for cell_index, cell in enumerate(notebook.cells, start=1):
        cell_type = cell.get("cell_type")
        if cell_type == "markdown":
            markdown = _strip_duplicate_h1(_cell_source(cell).rstrip(), title)
            if markdown:
                lines.extend([markdown, ""])
        elif cell_type == "code":
            lines.extend(
                [
                    _render_code_cell(
                        cell=cell,
                        cell_index=cell_index,
                        page_path=page_path,
                        notebook_asset_dir=notebook_asset_dir,
                    ),
                    "",
                ]
            )

    page_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return page_path, title


def write_notebook_index(column: dict[str, Path | str], pages: list[tuple[Path, str]]) -> Path:
    index_path = Path(column["docs_dir"]) / "index.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    label = str(column["label"])
    key = str(column["key"])
    lines = [
        "<!-- Generated by scripts/generate_column_notebook_pages.py; do not edit manually. -->",
        f"# {label} Notebook Outputs",
        "",
        NOTEBOOK_INDEX_INTROS.get(key, "These pages render notebook code and captured outputs directly in the documentation."),
        "",
        "| Page | Source notebook |",
        "|---|---|",
    ]
    for page_path, title in pages:
        source_name = f"{page_path.stem}.ipynb"
        lines.append(f"| [{title}]({page_path.name}) | `{source_name}` |")
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index_path


def main() -> int:
    rendered: list[Path] = []
    for column in COLUMNS:
        notebook_dir = Path(column["notebook_dir"])
        column_pages: list[tuple[Path, str]] = []
        for notebook_path in sorted(notebook_dir.glob("*.ipynb")):
            page_path, title = render_notebook_page(column, notebook_path)
            rendered.append(page_path)
            column_pages.append((page_path, title))
        rendered.append(write_notebook_index(column, column_pages))

    for path in rendered:
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
