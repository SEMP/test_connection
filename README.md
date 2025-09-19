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
- **Daemon service mode** with cron-like scheduling

## Quick Start

### One-time testing
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

### Service mode (daemon)
```bash
# Install dependencies for daemon mode
pip install -r requirements.txt

# Start daemon with default configuration
python ping_daemon.py

# Start daemon with custom configuration
python ping_daemon.py -c my_schedule.conf
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

Files should be placed in the `config/` directory, but the scripts will also search in the project root and other locations automatically.

## Log Analysis

The tool automatically logs all results and provides analysis capabilities:

```bash
# Analyze response patterns
python analyze_logs.py
# or
make analyze
```

This generates three analysis files:
- **`analysis/never_responded.txt`** - IPs that failed in all tests
- **`analysis/always_responded.txt`** - IPs that succeeded in all tests
- **`analysis/sometimes_responded.txt`** - IPs with mixed results (includes success rates)

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
   - `analysis/never_responded.txt`
   - `analysis/always_responded.txt`
   - `analysis/sometimes_responded.txt`

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

## Daemon Service Mode

The daemon mode allows continuous operation with cron-like scheduling defined in a configuration file.

### Configuration File (`config/ping_schedule.conf`)

Define jobs using cron syntax:

```ini
# Job format: [job:name]
[job:production_check]
ip_file = production_servers.txt
schedule = */5 * * * *        # Every 5 minutes
timeout = 5
count = 2
workers = 20

[job:daily_summary]
ip_file = all_servers.txt
schedule = 0 0 * * *          # Daily at midnight
timeout = 10
count = 1
workers = 15
```

### Schedule Format

Use standard cron syntax: `minute hour day month day_of_week`

| Field | Range | Special |
|-------|-------|---------|
| minute | 0-59 | */5 = every 5 minutes |
| hour | 0-23 | */2 = every 2 hours |
| day | 1-31 | * = every day |
| month | 1-12 | * = every month |
| day_of_week | 0-6 | 1-5 = weekdays |

### Starting the Daemon

```bash
# Install APScheduler dependency
pip install apscheduler

# Start daemon (runs in foreground)
python ping_daemon.py

# Start with custom config
python ping_daemon.py -c my_config.conf

# Run as system service (example with systemd)
sudo systemctl start ping-checker
```

### Daemon Features

- **Graceful shutdown** on SIGINT/SIGTERM
- **Comprehensive logging** to `ping_daemon.log`
- **Error handling** and job failure recovery
- **Multiple concurrent jobs** with different schedules
- **Relative path support** for IP files

## Project Structure

```
.
├── ping_checker.py      # Main ping testing script
├── ping_daemon.py       # Daemon service with scheduling
├── analyze_logs.py      # Log analysis tool
├── constants.py         # Centralized path constants
├── config/             # Configuration files directory
│   ├── ping_schedule.conf  # Daemon job configuration
│   ├── ips_list.txt        # Default IP list for daemon
│   └── sample_ips.txt      # Example IP file for testing
├── analysis/           # Analysis output files
│   ├── never_responded.txt    # IPs that never responded
│   ├── always_responded.txt   # IPs that always responded
│   └── sometimes_responded.txt # IPs with mixed results
├── Makefile            # Build targets
├── requirements.txt    # Dependencies
├── CLAUDE.md           # AI assistant guidance
├── ping_daemon.log     # Daemon operation log
└── logs/               # Auto-generated ping logs
```