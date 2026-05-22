# Hot Trend Lab Integration

This integration adds an English-language Hot Trend Lab tutorial column to the De-Time repository without changing the existing documentation design or rewriting existing pages.

Changed existing file:

- `mkdocs.yml`: added one Tutorials navigation group named `Hot Trend Lab`.

Added directories and files:

- `docs/tutorials/hot-trend-lab.md`
- `docs/tutorials/hot-trend-lab/`
- `examples/hot_trends/`
- `examples/notebooks/hot_trends/`

Paper-writing materials:

- The original `submission/` directory has been moved out of the main repo package and placed in a separate paper-writing archive, per request.

Data policy:

- The Hot Trend Lab uses real public data fetched at runtime.
- No synthetic fallback data is generated.
- If a live source is unavailable, the notebook stops with an explicit error.

Local checks performed in this packaging environment:

```bash
$env:PYTHONPATH='src;examples'
python -m compileall -q examples/hot_trends
@'
from pathlib import Path
import json
for p in Path('examples/notebooks/hot_trends').glob('*.ipynb'):
    json.loads(p.read_text())
print('hot trend notebooks valid JSON')
'@ | python -
```

Network notebooks were not executed in this packaging environment because external network access was unavailable to the container.

Additional compatibility change:

- `scripts/check_doc_consistency.py`: skips paper-only `submission/` checks when the submission bundle is intentionally distributed separately.
