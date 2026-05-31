#!/usr/bin/env bash
#SBATCH --job-name=detime_quant_01_02
#SBATCH --output=logs/slurm/detime_quant_01_02_%j.out
#SBATCH --error=logs/slurm/detime_quant_01_02_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G

set -euo pipefail
mkdir -p logs/slurm examples/quant_trading/reports
export PYTHONPATH="$PWD/src:$PWD/examples:${PYTHONPATH:-}"
python examples/quant_trading/scripts/system_probe.py
python examples/quant_trading/scripts/smoke_quant_columns_01_02.py
