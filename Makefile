PYTHON ?= python3

.PHONY: test
test:
	$(PYTHON) ping_checker.py sample_ips.txt