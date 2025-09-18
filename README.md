# ICMP Ping Connectivity Checker

A Python tool for testing network connectivity to multiple IP addresses using ICMP ping with concurrent execution and comprehensive logging.

## Features

- **Concurrent ping testing** with configurable worker threads
- **Automatic logging** to timestamped files
- **Comment support** in IP files (inline and full-line comments)
- **Duplicate IP detection** and removal
- **Colored output** for easy result identification
- **Log analysis tool** to categorize IP response patterns
- **Flexible command-line interface** with various options

## Quick Start

```bash
# Test connectivity using sample IPs
make test

# Test with your own IP file
make run FILE=my_ips.txt
# or
make run-my_ips

# Analyze all test results
make analyze
```

## Usage

### Basic Usage

```bash
python ping_checker.py sample_ips.txt
```

### Advanced Options

```bash
# Custom timeout and worker count
python ping_checker.py my_ips.txt -t 5 -w 20

# Verbose output (shows all results)
python ping_checker.py my_ips.txt -v

# Custom ping count per IP
python ping_checker.py my_ips.txt -c 3
```

### IP File Format

Create a text file with one IP address per line:

```
# DNS servers
8.8.8.8         # Google DNS
8.8.4.4         # Google DNS secondary
1.1.1.1         # Cloudflare DNS

# Local network
192.168.1.1     # Router
10.0.0.1        # Gateway
```

Comments are supported both as full lines (starting with #) and inline comments.

## Log Analysis

The tool automatically logs all results and provides analysis capabilities:

```bash
# Analyze response patterns
python analyze_logs.py
# or
make analyze
```

This generates three analysis files:
- **`analysis_never_responded.txt`** - IPs that failed in all tests
- **`analysis_always_responded.txt`** - IPs that succeeded in all tests
- **`analysis_sometimes_responded.txt`** - IPs with mixed results (includes success rates)

## Make Targets

| Target | Description |
|--------|-------------|
| `make test` | Run ping checker with sample IPs |
| `make run FILE=filename` | Run with specific file |
| `make run-basename` | Run with basename.txt (e.g., `make run-production` uses `production.txt`) |
| `make analyze` | Analyze all log files and categorize IP patterns |

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-t, --timeout` | Ping timeout in seconds | 3 |
| `-c, --count` | Number of ping packets | 1 |
| `-w, --workers` | Concurrent worker threads | 10 |
| `-v, --verbose` | Show all results (not just failures) | False |

## Output

The tool provides:

1. **Console output** with colored status indicators:
   - 🟢 Green for reachable IPs
   - 🔴 Red for unreachable IPs

2. **Log files** in `logs/` directory:
   - `YYYYMMDD_HHMMSS_successful.txt`
   - `YYYYMMDD_HHMMSS_failed.txt`

3. **Analysis files** (updated on each analysis):
   - `analysis_never_responded.txt`
   - `analysis_always_responded.txt`
   - `analysis_sometimes_responded.txt`

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)
- System `ping` command available

## Installation

1. Clone or download the project
2. No additional installation required - uses Python standard library only

## Exit Codes

- **0**: All IPs reachable
- **1**: Some IPs unreachable (useful for monitoring scripts)

## Examples

### Test production servers
```bash
# Create production_servers.txt with your IPs
echo "prod1.example.com" > production_servers.txt
echo "prod2.example.com" >> production_servers.txt
make run-production_servers
```

### Monitor connectivity over time
```bash
# Run multiple tests
make test
sleep 300
make test
sleep 300
make test

# Analyze patterns
make analyze
```

### Batch testing
```bash
# Test multiple environments
make run FILE=staging_servers.txt
make run FILE=production_servers.txt
make run FILE=external_services.txt
make analyze
```

## Project Structure

```
.
├── ping_checker.py      # Main ping testing script
├── analyze_logs.py      # Log analysis tool
├── sample_ips.txt       # Example IP file
├── Makefile            # Build targets
├── requirements.txt    # Dependencies (none)
├── CLAUDE.md           # AI assistant guidance
└── logs/               # Auto-generated log files
```