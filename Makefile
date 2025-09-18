PYTHON ?= python3

.PHONY: test analyze run
test:
	$(PYTHON) ping_checker.py sample_ips.txt || true

analyze:
	$(PYTHON) analyze_logs.py

run:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make run FILE=<filename>"; \
		echo "Example: make run FILE=my_ips.txt"; \
		exit 1; \
	fi
	$(PYTHON) ping_checker.py $(FILE) || true

# Allow positional argument: make run-production_servers (for production_servers.txt)
run-%:
	$(PYTHON) ping_checker.py $*.txt || true