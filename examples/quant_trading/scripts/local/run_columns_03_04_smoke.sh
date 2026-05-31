#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT/examples:${PYTHONPATH:-}"

python examples/quant_trading/scripts/system_probe.py --output examples/quant_trading/reports/hardware_probe.json
python examples/quant_trading/scripts/smoke_quant_columns_03_04.py
python examples/quant_trading/scripts/run_columns_03_04.py --use-bundled-sample --step 63
