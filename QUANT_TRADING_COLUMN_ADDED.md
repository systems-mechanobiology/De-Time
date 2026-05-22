# Quant Trading Column Integration

This integration adds an English-language quant trading tutorial column to the De-Time repository without changing existing documentation design or existing page content.

Changed existing file:

- `mkdocs.yml`: added one Tutorials navigation group for the quant trading column.

Added directories:

- `docs/tutorials/quant-trading.md`
- `docs/tutorials/quant-trading/`
- `examples/notebooks/quant_trading/`
- `examples/quant_trading/`

Data policy:

- The notebooks use real market data downloaded at runtime through `yfinance`.
- No artificial price-series fallback is provided.
- If the data vendor is unavailable, `MarketDataError` is raised.

Local checks performed:

```bash
$env:PYTHONPATH='src;examples'
python examples/quant_trading/scripts/smoke_quant_trading.py
python -m compileall -q examples/quant_trading
@'
from pathlib import Path
import nbformat
for p in Path('examples/notebooks/quant_trading').glob('*.ipynb'):
    nbformat.read(p, as_version=4)
print('notebooks valid')
'@ | python -
$env:PYTHONPATH='src'
python scripts/check_doc_consistency.py
```

`mkdocs build --strict` was not executed in this container because MkDocs was not installed in the runtime environment.
