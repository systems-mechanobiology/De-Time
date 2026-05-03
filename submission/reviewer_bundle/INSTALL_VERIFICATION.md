# Install Verification

- Release target: `0.1.1`
- Current source install path: `python -m pip install "git+https://github.com/systems-mechanobiology/De-Time.git"`
- Planned PyPI install path after release: `pip install de-time`
- Release state: publish from `main` via the release workflow, then run post-publish smoke verification.
- Release smoke script: `scripts/release_smoke_matrix.py`
- Wheel/sdist validation: `scripts/check_dist_contents.py` and `python -m twine check dist/*`
