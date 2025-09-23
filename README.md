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
- **Docker support** for containerized deployment
- **Cross-platform compatibility** (Windows, Linux, macOS)
- **Optional database logging** (PostgreSQL support)

## Quick Start

The most common workflow is:

```bash
# 1. Setup environment and dependencies
make install

# 2. Run connectivity tests (uses data/config/ips_list.txt)
make run
```

### Additional options
```bash
# Test with sample IPs
make test

# Run scheduled daemon service
make daemon

# Analyze test results
make analyze

# Check environment status
make status
```

## Docker Usage

### Quick Start with Docker

```bash
# 1. Configure your IPs
echo "8.8.8.8" > data/config/ips_list.txt
echo "1.1.1.1" >> data/config/ips_list.txt

# 2. Build and run daemon
docker-compose up -d

# 3. Check logs
docker-compose logs -f
```

### Docker Commands

```bash
# Build and run daemon service (scheduled jobs)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop daemon
docker-compose down

# For one-time operations, use Make commands:
make run      # One-time ping check
make analyze  # Log analysis
```

### Docker Volumes

The `data/` directory is mounted as a volume to persist:
- **Configuration files** in `data/config/`
- **Log files** in `data/logs/`
- **Analysis results** in `data/analysis/`

## Usage

### Direct Script Usage

```bash
# Basic usage with default settings
python ping_checker.py data/config/ips_list.txt

# Custom timeout and worker count
python ping_checker.py data/config/my_ips.txt -t 5 -w 20

# Verbose output (shows all results)
python ping_checker.py data/config/my_ips.txt -v

# Custom ping count per IP
python ping_checker.py data/config/my_ips.txt -c 3
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

Files should be placed in the `data/config/` directory, but the scripts will also search in the project root and other locations automatically.

## Log Analysis

The tool automatically logs all results and provides analysis capabilities:

```bash
# Analyze response patterns
python analyze_logs.py
# or
make analyze
```

This generates three analysis files:
- **`data/analysis/never_responded.txt`** - IPs that failed in all tests
- **`data/analysis/always_responded.txt`** - IPs that succeeded in all tests
- **`data/analysis/sometimes_responded.txt`** - IPs with mixed results (includes success rates)

## Make Targets

| Target | Description |
|--------|-------------|
| `make install` | Create virtual environment and install dependencies |
| `make run` | Run ping checker with data/config/ips_list.txt |
| `make test` | Run ping checker with sample IPs (data/config/sample_ips.txt) |
| `make daemon` | Start scheduled daemon service with data/config/ping_schedule.conf |
| `make analyze` | Analyze all log files and categorize IP patterns |
| `make status` | Show virtual environment and project status |
| `make clean` | Remove virtual environment |

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

2. **Log files** in `data/logs/` directory:
   - `YYYYMMDD_HHMMSS_successful.txt`
   - `YYYYMMDD_HHMMSS_failed.txt`

3. **Analysis files** (updated on each analysis):
   - `data/analysis/never_responded.txt`
   - `data/analysis/always_responded.txt`
   - `data/analysis/sometimes_responded.txt`

## Requirements

- Python 3.6+
- APScheduler (for daemon mode scheduling)
- System `ping` command available
- **Cross-platform support**: Works on Windows, Linux, and macOS

## Cross-Platform Compatibility

This project fully supports Windows, Linux, and macOS:

### **Windows Support:**
- Automatic detection of Windows ping command syntax (`-n`, `-w`)
- Virtual environment path handling (`Scripts/` vs `bin/`)
- Path compatibility with spaces and backslashes

### **Linux/macOS Support:**
- Native ping command syntax (`-c`, `-W`)
- Standard Unix virtual environment structure
- POSIX path handling

### **Make Commands:**
The Makefile automatically detects your operating system and uses the appropriate:
- Python command (`python` on Windows, `python3` on Unix)
- Virtual environment paths
- File path extraction from centralized constants

## Database Support (Optional)

The ping checker can optionally store results in a PostgreSQL database alongside the existing file logging system.

### **Setup Database Logging:**

1. **Install dependencies (includes PostgreSQL support):**
   ```bash
   make install  # Installs psycopg2-binary automatically
   ```

2. **Configure database connection (choose one method):**

   **Method 1: Database URL**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/ping_checker"
   ```

   **Method 2: Individual variables**
   ```bash
   export DB_HOST="localhost"
   export DB_PORT="5432"
   export DB_NAME="ping_checker"
   export DB_USER="your_user"
   export DB_PASSWORD="your_password"
   ```

3. **Run ping checker as usual:**
   ```bash
   make run
   # Output will show: "✓ Results saved to database"
   ```

### **Database Schema:**

The tool automatically creates a `ping_results` table with:
- `ip_address` (INET) - IP address tested
- `timestamp` (TIMESTAMPTZ) - When the test was performed
- `success` (BOOLEAN) - Whether ping succeeded
- `response_time` (VARCHAR) - Response time (e.g., "15ms")
- `job_name` (VARCHAR) - Optional job identifier
- `timeout_seconds` (INTEGER) - Ping timeout used
- `ping_count` (INTEGER) - Number of ping packets sent

### **Benefits:**
- **Dual logging**: Files + database (not either/or)
- **Graceful fallback**: Works without database configured
- **No breaking changes**: Existing file logging unchanged
- **Analytics ready**: SQL queries for advanced analysis

## Installation

```bash
# 1. Clone or download the project
# 2. Setup environment and install dependencies
make install

# 3. Configure your IP addresses in data/config/ips_list.txt
# 4. Run connectivity tests
make run
```

## Exit Codes

- **0**: All IPs reachable
- **1**: Some IPs unreachable (useful for monitoring scripts)

## Examples

### Docker Examples

```bash
# Production monitoring with Docker daemon
echo "prod1.example.com" >> data/config/ips_list.txt
echo "prod2.example.com" >> data/config/ips_list.txt
docker-compose up -d

# One-time connectivity check
make run

# Analyze historical data
make analyze
```

### Test production servers
```bash
# Add your IPs to data/config/ips_list.txt
echo "prod1.example.com" >> data/config/ips_list.txt
echo "prod2.example.com" >> data/config/ips_list.txt
make run
```

### Monitor connectivity over time
```bash
# Run multiple tests
make run
sleep 300
make run
sleep 300
make run

# Analyze patterns
make analyze
```

### Using daemon for continuous monitoring
```bash
# Configure scheduled jobs in data/config/ping_schedule.conf
# Start daemon service
make daemon
```

## Daemon Service Mode

The daemon mode allows continuous operation with cron-like scheduling defined in a configuration file.

### Configuration File (`data/config/ping_schedule.conf`)

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
python ping_daemon.py -c data/config/my_config.conf

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
├── data/               # Data directory (Docker volume)
│   ├── config/         # Configuration files
│   │   ├── ping_schedule.conf  # Daemon job configuration
│   │   ├── ips_list.txt        # Default IP list for daemon
│   │   └── sample_ips.txt      # Example IP file for testing
│   ├── logs/           # Auto-generated ping logs
│   └── analysis/       # Analysis output files
│       ├── never_responded.txt    # IPs that never responded
│       ├── always_responded.txt   # IPs that always responded
│       └── sometimes_responded.txt # IPs with mixed results
├── Makefile            # Build targets
├── requirements.txt    # Dependencies
├── CLAUDE.md           # AI assistant guidance
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # Docker orchestration
├── .dockerignore       # Docker build exclusions
└── ping_daemon.log     # Daemon operation log
```