PYTHON ?= python3
VENV_DIR = .venv
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_DIR)/bin/pip

# Check if virtual environment exists and is activated
VENV_ACTIVE = $(shell python -c "import sys; print('1' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '0')" 2>/dev/null)

.PHONY: install test analyze run daemon status clean help run
help:
	@echo "Available targets:"
	@echo "  install    - Create virtual environment and install dependencies"
	@echo "  test       - Run ping checker with sample IPs"
	@echo "  analyze    - Analyze all log files"
	@echo "  run        - Start ping daemon with default ips_list.txt"
	@echo "  daemon     - Start ping daemon with ping_schedule.conf"
	@echo "  status     - Show virtual environment status"
	@echo "  clean      - Remove virtual environment"
	@echo ""
	@echo "Testing with custom files:"
	@echo "  make test-FILE=filename   - Test specific file"
	@echo "  make test-basename        - Test basename.txt"

# Create virtual environment and install dependencies
install:
	@echo "Setting up virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment in $(VENV_DIR)..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	else \
		echo "Virtual environment already exists."; \
	fi
	@echo "Installing dependencies..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@echo "Installation complete!"
	@echo "Virtual environment created at: $(VENV_DIR)"

# Test connectivity with sample IPs
test:
	@$(MAKE) _ensure_venv
	$(VENV_PYTHON) ping_checker.py data/config/sample_ips.txt || true

# Analyze log files
analyze:
	@$(MAKE) _ensure_venv
	$(VENV_PYTHON) analyze_logs.py

# Start daemon with default ips_list.txt (single file mode)
run:
	@$(MAKE) _ensure_venv
	@if [ ! -f "data/config/ips_list.txt" ]; then \
		echo "Error: data/config/ips_list.txt not found. Create this file with your IP addresses."; \
		echo "Example: echo '8.8.8.8' > data/config/ips_list.txt"; \
		exit 1; \
	fi
	$(VENV_PYTHON) ping_checker.py data/config/ips_list.txt || true

# Start daemon with scheduled jobs from ping_schedule.conf
daemon:
	@$(MAKE) _ensure_venv
	@if [ ! -f "data/config/ping_schedule.conf" ]; then \
		echo "Error: data/config/ping_schedule.conf not found."; \
		echo "Use the provided sample configuration or create your own."; \
		exit 1; \
	fi
	$(VENV_PYTHON) ping_daemon.py

# Test with custom file (make test-FILE=filename)
test-%:
	@$(MAKE) _ensure_venv
	@if [ -z "$(FILE)" ]; then \
		# Pattern matching: make test-production_servers -> production_servers.txt
		$(VENV_PYTHON) ping_checker.py $*.txt || true; \
	else \
		# Explicit file: make test-custom FILE=my_file.txt
		$(VENV_PYTHON) ping_checker.py $(FILE) || true; \
	fi

# Show virtual environment status
status:
	@echo "Virtual environment status:"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "  ✓ Virtual environment exists at: $(VENV_DIR)"; \
		echo "  Python version: $$($(VENV_PYTHON) --version 2>/dev/null || echo 'Not available')"; \
		echo "  Installed packages:"; \
		$(VENV_PIP) list --format=columns 2>/dev/null | head -10 || echo "    Cannot list packages"; \
	else \
		echo "  ✗ Virtual environment not found"; \
		echo "  Run 'make install' to create it"; \
	fi
	@echo ""
	@if [ "$(VENV_ACTIVE)" = "1" ]; then \
		echo "  ✓ Virtual environment is currently activated"; \
	else \
		echo "  ○ Virtual environment not activated (Makefile will handle this)"; \
	fi

# Clean up virtual environment
clean:
	@echo "Removing virtual environment..."
	@if [ -d "$(VENV_DIR)" ]; then \
		rm -rf $(VENV_DIR); \
		echo "Virtual environment removed."; \
	else \
		echo "No virtual environment to remove."; \
	fi

# Internal target to ensure virtual environment exists
_ensure_venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Running 'make install'..."; \
		$(MAKE) install; \
	fi