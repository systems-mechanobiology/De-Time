# Citation / Release Notes

## Citation

Use [`CITATION.cff`](https://github.com/systems-mechanobiology/De-Time/blob/main/CITATION.cff) for machine-readable citation metadata.

The current branch targets `0.1.1`. Tagged standalone releases use the
`de-time-v*` convention and publish the `de-time` distribution.

## Release notes

- [`CHANGELOG.md`](https://github.com/systems-mechanobiology/De-Time/blob/main/CHANGELOG.md) tracks package-level changes.
- `tsdecomp` remains available only as a deprecated compatibility alias.
- Benchmark code and review artifacts are no longer part of the release payload
  for the main package.
- Companion benchmark work now lives in
  [`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).
- The release workflow also performs post-publish smoke verification from PyPI.
