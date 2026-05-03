# Entry points

Use this file when you want the shortest path into the product.

- `START_HERE.md`
  - one landing page for the fastest useful entry into the package
- `docs/index.md`
  - docs homepage for humans who want the software overview first
- `docs/quickstart.md`
  - shortest path to a first Python or CLI run
- `docs/machine-api.md`
  - schemas, catalog, compact result modes, and MCP guidance
- `docs/method-cards.md`
  - assumptions, failure modes, maturity, and not-recommended cases
- `docs/method-matrix.md`
  - compact method comparison table for input mode, dependencies, params, and outputs
- `docs/config-reference.md`
  - `DecompositionConfig` fields and per-method parameter semantics
- `examples/notebooks/de_time_method_gallery.ipynb`
  - plotted beginner notebook for the retained method surface
- `detime run`
  - one file in, one decomposition artifact set out
- `detime batch`
  - same method across many files
- `detime profile`
  - runtime-oriented profiling by method and backend
- `detime schema`
  - packaged JSON schema lookup
- `detime recommend`
  - method shortlisting from workflow constraints
- `python -m detime.mcp.server`
  - minimal MCP server for tool-based access
- `docs/token-benchmarks.md`
  - token-budget evidence for `full`, `summary`, and `meta`
- `python -c "from detime import decompose, DecompositionConfig"`
  - fastest programmatic smoke-test path
