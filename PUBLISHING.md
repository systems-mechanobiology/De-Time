# Publishing De-Time

This file describes the standalone release flow for the `de-time`
distribution, the `detime` import path, and the legacy `tsdecomp`
compatibility aliases.

## Release contract

- product brand: `De-Time`
- PyPI distribution: `de-time`
- preferred import path: `detime`
- legacy import path: `tsdecomp`
- preferred CLI: `detime`
- legacy CLI alias: `tsdecomp`

Until `de-time` is actually published on PyPI, reviewer-facing docs should use
the GitHub installation path rather than claiming `pip install de-time`.

## Before the first public release

Confirm these repository-level settings match the actual standalone repository:

- `pyproject.toml` project URLs
- `mkdocs.yml` `repo_url`, `repo_name`, and `site_url`
- GitHub Pages target, if docs will be published
- PyPI project name availability for `de-time`

If the final standalone repository or docs site uses a different slug, update
those URLs before tagging the release.

## Maintainer checklist

1. Update the version in `pyproject.toml`.
2. Run local tests.
3. Build a source distribution and wheel.
4. Smoke-test the new package name and legacy compatibility surface.
5. Commit the release changes.
6. Tag the release.
7. Push the branch and tag.
8. Publish the GitHub release.
9. Let the release workflow publish to PyPI.
10. Verify the docs deployment and installation path.

## Local release commands

```bash
python3 -m pip install -U pip build twine
python3 -m pip install -e .[dev,multivar,docs]
python3 -m pytest tests -q
python3 -m build
python3 -m twine check dist/*
```

Compatibility smoke tests:

```bash
python3 -m pip install dist/*.whl
python3 -c "import detime, tsdecomp; print(detime.DecompositionConfig.__name__, tsdecomp.DecompositionConfig.__name__)"
python3 -m detime --help
python3 -m tsdecomp --help
```

## Tagging convention

Use a release tag that matches the new standalone product:

```bash
git tag de-time-v0.1.0
git push origin de-time-v0.1.0
```

The included wheel workflow is configured around `de-time-v*` tags.

## GitHub Actions expectations

The standalone repository should contain:

- `.github/workflows/ci.yml`
- `.github/workflows/wheels.yml`
- `.github/workflows/docs.yml`

Those workflows assume this package directory is the repository root.

## PyPI and trusted publishing

If you use GitHub Actions for publishing:

- configure PyPI trusted publishing for the standalone repository
- ensure the release workflow has `id-token: write`
- publish only from release tags or GitHub releases

## Docs deployment

The docs workflow builds MkDocs and deploys to GitHub Pages. Before using it:

- enable GitHub Pages for the repository
- allow Pages deployment from GitHub Actions
- confirm `site_url` in `mkdocs.yml`

## Notes on compatibility

The canonical implementation now lives under `src/detime/`. The
`src/tsdecomp/` tree remains only as a deprecated compatibility alias that
re-exports the De-Time public surface and warns on import or CLI use.
