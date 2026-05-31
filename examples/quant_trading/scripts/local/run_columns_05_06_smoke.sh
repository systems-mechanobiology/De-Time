#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$PWD/src:$PWD/examples:${PYTHONPATH:-}"
python examples/quant_trading/scripts/system_probe.py --output examples/quant_trading/reports/hardware_probe.json
python examples/quant_trading/scripts/smoke_quant_columns_05_06.py
