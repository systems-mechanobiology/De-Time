#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT/examples:${PYTHONPATH:-}"
python examples/quant_trading/scripts/system_probe.py
python examples/quant_trading/scripts/smoke_quant_columns_01_02.py
