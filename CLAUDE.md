# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for testing network connectivity to multiple IP addresses using ICMP ping. The main script `ping_checker.py` reads IP addresses from a text file and performs concurrent ping tests.

## Project Structure

- `ping_checker.py` - Main script for ICMP connectivity testing
- `sample_ips.txt` - Example file with IP addresses for testing
- `requirements.txt` - Project dependencies (uses only standard library)

## Common Commands

### Running the ping checker
```bash
# Basic usage with sample file
python ping_checker.py sample_ips.txt

# With custom timeout and worker count
python ping_checker.py sample_ips.txt -t 5 -w 20

# Verbose output
python ping_checker.py sample_ips.txt -v

# Show help
python ping_checker.py -h
```

### Development Setup

No external dependencies required - uses only Python standard library.

```bash
# Make script executable (optional)
chmod +x ping_checker.py

# Run directly if executable
./ping_checker.py sample_ips.txt
```

## Architecture Notes

- Uses `subprocess` to call system ping command for reliability
- Implements concurrent pinging with `ThreadPoolExecutor` for performance
- Supports configurable timeout, ping count, and worker threads
- Exits with non-zero code if any hosts are unreachable (useful for scripts/monitoring)
- Automatically logs results to timestamped files in `logs/` directory:
  - `YYYYMMDD_HHMMSS_successful.txt` - successful ping results
  - `YYYYMMDD_HHMMSS_failed.txt` - failed ping results

## Log Files

Results are automatically saved to the `logs/` directory with timestamp-based filenames. Each execution creates two files with the same timestamp:
- Successful connections: IP, status, and response time
- Failed connections: IP, status, and error reason

Log format: `IP_ADDRESS\tSTATUS\tRESPONSE_INFO`