PYTHON ?= python3

.PHONY: test analyze
test:
	$(PYTHON) ping_checker.py sample_ips.txt || true

analyze:
	$(PYTHON) analyze_logs.py