#!/usr/bin/env bash
#SBATCH --job-name=detime_quant_05_06_smoke
#SBATCH --output=logs/slurm/quant_05_06_%j.out
#SBATCH --error=logs/slurm/quant_05_06_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -euo pipefail
ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
cd "$ROOT"
mkdir -p logs/slurm examples/quant_trading/reports
source .venv/bin/activate 2>/dev/null || true
export PYTHONPATH="$PWD/src:$PWD/examples:${PYTHONPATH:-}"
python examples/quant_trading/scripts/system_probe.py --output "examples/quant_trading/reports/hardware_probe_${SLURM_JOB_ID:-local}.json"
python examples/quant_trading/scripts/smoke_quant_columns_05_06.py
