PYTHON ?= python
export PYTHONPATH := $(CURDIR)/src:$(CURDIR)/examples:$(PYTHONPATH)

.PHONY: setup probe test smoke smoke-03-04 smoke-05-06 strategy-lab strategy-lab-live strategy-expansion strategy-expansion-live quant-columns-01-02 quant-columns-01-02-live quant-columns-03-04 quant-columns-03-04-live quant-columns-05-06 quant-columns-05-06-live quant-columns-01-04 quant-columns-01-06 audit clean-pyc

setup:
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install -r examples/quant_trading/requirements.txt

probe:
	$(PYTHON) examples/quant_trading/scripts/system_probe.py --output examples/quant_trading/reports/hardware_probe.json

test:
	$(PYTHON) -m pytest -q tests/cli/test_cli.py tests/core/test_machine_interfaces.py tests/wrappers/test_wrappers.py

smoke: probe
	$(PYTHON) examples/quant_trading/scripts/smoke_quant_columns_01_02.py
	$(PYTHON) examples/quant_trading/scripts/smoke_quant_columns_03_04.py
	$(PYTHON) examples/quant_trading/scripts/smoke_quant_columns_05_06.py

smoke-03-04: probe
	$(PYTHON) examples/quant_trading/scripts/smoke_quant_columns_03_04.py

smoke-05-06: probe
	$(PYTHON) examples/quant_trading/scripts/smoke_quant_columns_05_06.py


strategy-lab: probe
	$(PYTHON) examples/quant_trading/scripts/run_strategy_lab.py --use-bundled-sample --methods STL --period 42 --train-window 180 --step 21 --allow-short-reversion --report-dir examples/quant_trading/reports/strategy_lab

strategy-lab-live: probe
	$(PYTHON) examples/quant_trading/scripts/run_strategy_lab.py --ticker SPY --start 2018-01-01 --methods STL SSA --period 63 --train-window 252 --step 21 --report-dir examples/quant_trading/reports/strategy_lab_live

strategy-expansion: probe
	$(PYTHON) examples/quant_trading/scripts/run_strategy_expansion.py --use-bundled-sample --variant-grid custom --methods STL SSA STD --periods 42 --train-window 126 --pair-method STL --pair-period 42 --pair-train-window 126 --step 126 --report-dir examples/quant_trading/reports/strategy_expansion

strategy-expansion-live: probe
	$(PYTHON) examples/quant_trading/scripts/run_strategy_expansion.py --ticker SPY --start 2018-01-01 --variant-grid default --include-wavelet --pairs KO:PEP XOM:CVX MA:V SPY:QQQ --pair-method STL --pair-period 63 --report-dir examples/quant_trading/reports/strategy_expansion_live

quant-columns-01-02:
	$(PYTHON) examples/quant_trading/scripts/run_columns_01_02.py --use-bundled-sample

quant-columns-01-02-live:
	$(PYTHON) examples/quant_trading/scripts/run_columns_01_02.py

quant-columns-03-04:
	$(PYTHON) examples/quant_trading/scripts/run_columns_03_04.py --use-bundled-sample --train-window 180 --step 126

quant-columns-03-04-live:
	$(PYTHON) examples/quant_trading/scripts/run_columns_03_04.py

quant-columns-05-06:
	rm -rf /tmp/detime_quant_columns_05_06_make && mkdir -p /tmp/detime_quant_columns_05_06_make
	$(PYTHON) examples/quant_trading/scripts/run_column_05_pairs_spread_decomposition.py --use-bundled-sample --report-dir /tmp/detime_quant_columns_05_06_make --method STL --period 42 --train-window 126 --step 252
	cp /tmp/detime_quant_columns_05_06_make/column_05_* examples/quant_trading/reports/
	$(PYTHON) examples/quant_trading/scripts/run_column_06_cross_sectional_rotation.py --use-bundled-sample --report-dir /tmp/detime_quant_columns_05_06_make --method STL --period 42 --train-window 126 --step 252
	cp /tmp/detime_quant_columns_05_06_make/column_06_* examples/quant_trading/reports/

quant-columns-05-06-live:
	$(PYTHON) examples/quant_trading/scripts/run_columns_05_06.py

quant-columns-01-04: quant-columns-01-02 quant-columns-03-04

quant-columns-01-06: quant-columns-01-02 quant-columns-03-04 quant-columns-05-06

audit:
	$(PYTHON) -c "from pathlib import Path; required=['examples/quant_trading/reports/repository_type.md','examples/quant_trading/reports/experiment_matrix.csv','examples/quant_trading/reports/dataset_passport.csv','examples/quant_trading/reports/baseline_passport.csv','examples/quant_trading/reports/metric_passport.csv','examples/quant_trading/reports/run_manifest_schema.json','examples/quant_trading/reports/benchmark_status_schema.json']; missing=[p for p in required if not Path(p).exists()]; assert not missing, 'Missing quant audit files: '+', '.join(missing); print('quant audit files present')"

clean-pyc:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
