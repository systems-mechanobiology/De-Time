# Publishing De-Time

This file describes the standalone release flow for the `de-time`
distribution, the `detime` import path, and the legacy `tsdecomp`
compatibility aliases.

## Current release record

Release `0.1.0` was cut on April 8, 2026 as tag `de-time-v0.1.0`.

Release contract:

- product brand: `De-Time`
- PyPI distribution: `de-time`
- preferred import path: `detime`
- legacy import path: `tsdecomp`
- preferred CLI: `detime`
- legacy CLI alias: `tsdecomp`

The packaged compatibility scope is intentionally narrow: only top-level
`import tsdecomp` and the `tsdecomp` CLI alias remain. Transition-era
submodules such as `tsdecomp.methods.*`, `tsdecomp.leaderboard`, and
`tsdecomp.bench_config` are not part of the release payload.

## Maintainer checklist for the next release

1. Update the version in `pyproject.toml`, `CHANGELOG.md`, and `CITATION.cff`.
2. Regenerate schema assets.
3. Regenerate the performance snapshot.
4. Run the documentation consistency check.
5. Run local tests.
6. Build a source distribution and wheel.
7. Run the release smoke matrix.
8. Commit the release changes.
9. Tag the release.
10. Push the branch and tag.
11. Publish the GitHub release.
12. Let the release workflow publish to PyPI.
13. Verify the docs deployment and installation path.

## Local release commands

```bash
python -m pip install -U pip build twine
python -m pip install -e .[dev,multivar,docs]
python -m pytest tests -q
python scripts/generate_schema_assets.py
python scripts/generate_performance_snapshot.py
python scripts/check_doc_consistency.py
python -m build
python scripts/check_dist_contents.py dist/*.tar.gz dist/*.whl
python scripts/release_smoke_matrix.py
python -m twine check dist/*
```

## Tagging convention

Use release tags that match the standalone product:

```bash
git tag de-time-v0.1.1
git push origin de-time-v0.1.1
```

The wheel workflow is configured around `de-time-v*` tags.

## GitHub Actions expectations

The standalone repository contains:

- `.github/workflows/ci.yml`
- `.github/workflows/wheels.yml`
- `.github/workflows/docs.yml`

Those workflows assume this package directory is the repository root.

## PyPI and trusted publishing

If you use GitHub Actions for publishing:

- configure PyPI trusted publishing for the standalone repository,
- ensure the release workflow has `id-token: write`,
- publish only from release tags or GitHub releases.

## Docs deployment

The docs workflow builds MkDocs and deploys to GitHub Pages. Before using it:

- enable GitHub Pages for the repository,
- allow Pages deployment from GitHub Actions,
- confirm `site_url` in `mkdocs.yml`.

## Notes on compatibility

The canonical implementation lives under `src/detime/`. The `src/tsdecomp/`
tree retains only the top-level compatibility entrypoints needed for
`import tsdecomp` and the legacy CLI alias. Transition-era submodules are
intentionally omitted from the packaged artifacts.
