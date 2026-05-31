#!/usr/bin/env bash
#SBATCH --job-name=detime_quant_03_04
#SBATCH --output=logs/slurm/quant_03_04_%j.out
#SBATCH --error=logs/slurm/quant_03_04_%j.err
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -euo pipefail

mkdir -p logs/slurm examples/quant_trading/reports
export PYTHONPATH="$PWD/src:$PWD/examples:${PYTHONPATH:-}"
python examples/quant_trading/scripts/system_probe.py --output examples/quant_trading/reports/hardware_probe_${SLURM_JOB_ID:-local}.json
python examples/quant_trading/scripts/run_columns_03_04.py --use-bundled-sample --step 63
