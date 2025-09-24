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
- **Database IP sources** with configurable SQL queries
- **Label support** for module-based IP categorization
- **Real-time progress tracking** with batched database saves
- **IP validation** with invalid IP logging

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
- **SQL query files** in `data/sql/`
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

# Use database IP source with custom SQL file
python ping_checker.py -s my_custom_query.sql

# Mix of options with database source
python ping_checker.py -s network_devices.sql -t 5 -w 15 -v
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

## IP Sources: Files vs Database

The ping checker supports multiple IP source methods depending on your use case:

### **Text Files (Traditional Method)**

**When to use:**
- Simple, static IP lists
- Manual management of IP addresses
- Testing specific sets of IPs
- No existing inventory database

**Example:**
```bash
# Use a specific IP file
python ping_checker.py data/config/my_servers.txt

# Or let it auto-find ips_list.txt
make run
```

### **Database IP Sources (Advanced Method)**

**When to use:**
- Dynamic IP lists from existing databases
- Integration with network inventory systems
- Module-based IP categorization (TCP devices, etc.)
- Automatic IP discovery from CMDB

**Setup:**
1. **Configure database connection:**
   ```bash
   export IP_SOURCE_DATABASE_URL="postgresql://user:pass@host:5432/inventory_db"
   ```

2. **Create SQL query file in `data/sql/`:**
   ```sql
   -- data/sql/tcp_modules.sql
   SELECT ip_address,
          CONCAT(module_name, '_TCP') as label
   FROM network_devices n
   JOIN modules m ON n.module_id = m.id
   WHERE n.device_type = 'tcp_meter' AND n.active = true;
   ```

3. **Use database source:**
   ```bash
   # Use specific SQL file
   python ping_checker.py -s tcp_modules.sql

   # Use default get_ips.sql
   python ping_checker.py  # (if no txt file specified)
   ```

### **Daemon Jobs Configuration**

Configure different IP sources per job:

```ini
# data/config/ping_schedule.conf

# Traditional file source
[job:external_services]
ip_file = external_ips.txt
schedule = 0 * * * *

# Database source with custom SQL
[job:tcp_modules]
sql_file = tcp_modules.sql
schedule = */5 * * * *

# Database source with default SQL
[job:all_devices]
# No ip_file or sql_file = uses default database query
schedule = 0 */6 * * *
```

### **Label Support for Module Categorization**

Database sources can return labels for per-IP module identification:

**Single Column (IP only):**
```sql
SELECT ip_address FROM devices WHERE active = true;
-- Results stored with label = NULL
```

**Two Columns (IP + Label):**
```sql
SELECT ip_address, module_name
FROM devices d
JOIN modules m ON d.module_id = m.id
WHERE active = true;
-- Results stored with module labels
```

**Database benefits:**
- Direct module filtering: `WHERE label = 'Module_A_TCP'`
- No complex joins needed in ping results
- Real-time IP discovery from inventory systems

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
| `-s, --sql-file` | SQL file for database IP source | None |
| `-v, --verbose` | Show all results (not just failures) | False |

## Output

The tool provides:

1. **Console output** with colored status indicators:
   - 🟢 Green for reachable IPs
   - 🔴 Red for unreachable IPs

2. **Log files** in `data/logs/` directory:
   - `YYYYMMDD_HHMMSS_successful.txt` - Successful ping results
   - `YYYYMMDD_HHMMSS_failed.txt` - Failed ping results
   - `YYYYMMDD_HHMMSS_invalid_ips.txt` - Invalid/malformed IP addresses (if any)

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

The ping checker supports PostgreSQL integration for both **result logging** and **IP source management**. Database support is completely optional and works alongside file-based operations.

### **Two Database Uses:**

#### **1. Database Result Logging**
Store ping results in PostgreSQL for advanced analytics:

**Setup:**
1. **Install dependencies:**
   ```bash
   make install  # Includes psycopg2-binary
   ```

2. **Configure results database:**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/ping_results"
   # Optional: Use schema for multi-tenant deployments
   export DB_SCHEMA="monitoring"
   ```

3. **Run as usual:**
   ```bash
   make run
   # Shows: "✓ Results saved to database"
   ```

#### **2. Database IP Sources**
Get IP addresses from existing inventory databases:

**Setup:**
1. **Configure IP source database:**
   ```bash
   export IP_SOURCE_DATABASE_URL="postgresql://user:password@inventory.company.com:5432/network_db"
   ```

2. **Create SQL query files:**
   ```sql
   -- data/sql/tcp_devices.sql
   SELECT device_ip,
          CONCAT(module_name, '_TCP') as label
   FROM network_inventory
   WHERE device_type = 'tcp_communication';
   ```

3. **Use database IPs:**
   ```bash
   python ping_checker.py -s tcp_devices.sql
   ```

### **Database Schema (Results)**

Auto-created `ping_results` table:
- `id` (SERIAL) - Primary key
- `ip_address` (INET) - IP address tested
- `ping_time` (TIMESTAMPTZ) - Test timestamp
- `success` (BOOLEAN) - Ping success/failure
- `response_time_ms` (FLOAT) - Response time in milliseconds
- `job_name` (VARCHAR) - Job identifier (e.g., "tcp_modules")
- `label` (VARCHAR) - Module/device label (e.g., "Module_A_TCP")
- `timeout_seconds` (INTEGER) - Ping timeout used
- `ping_count` (INTEGER) - Number of pings sent

### **Advanced Database Features:**

**IP Validation & Error Handling:**
- Invalid IPs (like `10.204.15..`) are logged to `invalid_ips.txt`
- Database operations continue with valid IPs only
- Prevents batch INSERT failures

**Real-time Progress & Batching:**
- Results saved in configurable batches (default: 50 records)
- Real-time progress: `"(156/1000)"` for large IP lists
- Efficient for monitoring 1000+ devices

**Schema Support:**
```bash
export DB_SCHEMA="production"
# Tables created as: production.ping_results
```

**Query Examples:**
```sql
-- Module success rates
SELECT label,
       AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
       COUNT(*) as total_tests
FROM ping_results
WHERE ping_time >= NOW() - INTERVAL '24 hours'
GROUP BY label;

-- Recent failures by module
SELECT ip_address, label, ping_time
FROM ping_results
WHERE success = false
  AND ping_time >= NOW() - INTERVAL '1 hour'
ORDER BY ping_time DESC;
```

### **Benefits:**
- **Dual logging**: Files + database (both active)
- **Graceful fallback**: Works without database
- **No breaking changes**: File logging unchanged
- **Module analytics**: Direct label-based filtering
- **Enterprise ready**: Schema support for multi-tenant

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

Define jobs with multiple IP source options:

```ini
# Traditional file source
[job:external_services]
ip_file = external_ips.txt
schedule = 0 * * * *          # Every hour
timeout = 10
count = 1
workers = 15

# Database source with custom SQL
[job:tcp_modules]
sql_file = tcp_devices.sql
schedule = */5 * * * *        # Every 5 minutes
timeout = 3
count = 1
workers = 20

# Database source with default SQL (uses get_ips.sql)
[job:all_devices]
# No ip_file or sql_file specified
schedule = 0 */6 * * *        # Every 6 hours
timeout = 5
count = 2
workers = 25
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
├── database.py          # PostgreSQL integration (optional)
├── ip_source.py         # Database IP source management
├── data/               # Data directory (Docker volume)
│   ├── config/         # Configuration files
│   │   ├── ping_schedule.conf  # Daemon job configuration
│   │   ├── ips_list.txt        # Default IP list for daemon
│   │   └── sample_ips.txt      # Example IP file for testing
│   ├── sql/            # SQL query files for database IP sources
│   │   ├── get_ips.sql         # Default SQL query (user customizable)
│   │   ├── get_servers.sql     # Server IP addresses with labels
│   │   ├── get_network_devices.sql  # Network devices with modules
│   │   └── get_critical_hosts.sql   # Critical infrastructure hosts
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