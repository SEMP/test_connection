#!/usr/bin/env python3
"""
ICMP Ping Connectivity Checker

Reads a list of IP addresses from a text file and tests connectivity
using ICMP ping. Reports success/failure for each IP.
"""

import subprocess
import sys
import argparse
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Tuple
from datetime import datetime
from constants import (
    LOGS_DIR, ensure_directories, resolve_ip_file_path,
    DEFAULT_PING_TIMEOUT, DEFAULT_PING_COUNT, DEFAULT_WORKER_COUNT
)
from database import save_ping_results, is_database_enabled
from ip_source import get_ips_from_database, is_ip_source_database_enabled


def ping_host(ip_address: str, timeout: int = DEFAULT_PING_TIMEOUT, count: int = DEFAULT_PING_COUNT) -> Tuple[str, bool, str]:
    """
    Ping a single host using system ping command.

    Args:
        ip_address (str): IP address to ping
        timeout (int): Timeout in seconds
        count (int): Number of ping packets

    Returns:
        tuple: (ip_address, success, response_time)
    """
    try:
        # Use system ping command with OS-specific parameters
        if platform.system().lower() == 'windows':
            # Windows: ping -n count -w timeout_ms ip
            cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), ip_address]
        else:
            # Unix/Linux/macOS: ping -c count -W timeout ip
            cmd = ['ping', '-c', str(count), '-W', str(timeout), ip_address]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)

        if result.returncode == 0:
            # Extract response time from ping output
            lines = result.stdout.split('\n')
            for line in lines:
                if platform.system().lower() == 'windows':
                    # Windows format: "Reply from x.x.x.x: bytes=32 time=1ms TTL=64"
                    if 'time=' in line and 'ms' in line:
                        time_part = line.split('time=')[1].split()[0]
                        return (ip_address, True, time_part)
                else:
                    # Unix format: "64 bytes from x.x.x.x: icmp_seq=1 ttl=64 time=1.234 ms"
                    if 'time=' in line:
                        time_str = line.split('time=')[1].split()[0]
                        return (ip_address, True, f"{time_str}ms")
            return (ip_address, True, "N/A")
        else:
            return (ip_address, False, "No response")

    except subprocess.TimeoutExpired:
        return (ip_address, False, "Timeout")
    except Exception as e:
        return (ip_address, False, f"Error: {str(e)}")


def read_ip_list(file_path: str) -> List[str]:
    """
    Read IP addresses from a text file.

    Args:
        file_path (str): Path to the text file containing IP addresses

    Returns:
        list: List of IP addresses
    """
    try:
        import re
        with open(file_path, 'r') as file:
            ips = set()
            for _, line in enumerate(file, 1):
                # Remove comments using regex
                line = re.sub(r'#.*$', '', line).strip()
                if line:
                    ips.add(line)
            return list(ips)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)


def setup_logging() -> Tuple[str, str]:
    """
    Create log directory and return paths for success and failure log files.

    Returns:
        tuple: (success_log_path, failure_log_path)
    """
    # Ensure logs directory exists
    ensure_directories()

    # Generate timestamp for this execution
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    success_log = LOGS_DIR / f"{timestamp}_successful.txt"
    failure_log = LOGS_DIR / f"{timestamp}_failed.txt"

    return str(success_log), str(failure_log)


def log_result(ip_address: str, success: bool, response_info: str, success_log: str, failure_log: str) -> None:
    """
    Log ping result to appropriate file.

    Args:
        ip_address: IP address that was pinged
        success: Whether the ping was successful
        response_info: Response time or error information
        success_log: Path to success log file
        failure_log: Path to failure log file
    """
    log_file = success_log if success else failure_log
    status = "SUCCESS" if success else "FAILED"

    with open(log_file, 'a') as f:
        f.write(f"{ip_address}\t{status}\t{response_info}\n")


def get_ip_list(ip_file: str = None, sql_file: str = None) -> List[str]:
    """
    Get IP addresses from file or database source.

    Args:
        ip_file: Text file containing IP addresses (optional)
        sql_file: SQL file for database query (optional)

    Returns:
        List[str]: List of IP addresses
    """
    # Try database source first if enabled
    if is_ip_source_database_enabled():
        try:
            db_ips = get_ips_from_database(sql_file)
            if db_ips:
                print(f"Using {len(db_ips)} IP addresses from database")
                return db_ips
        except Exception as e:
            print(f"Warning: Database IP source failed: {e}")

    # Fall back to file source
    if not ip_file:
        print("Error: No IP source available (file or database)")
        sys.exit(1)

    ip_file_path = resolve_ip_file_path(ip_file)
    if not ip_file_path.exists():
        print(f"Error: File '{ip_file_path}' does not exist.")
        print(f"Tried looking in: config/, project root, and as provided path")
        sys.exit(1)

    ip_list = read_ip_list(str(ip_file_path))
    if not ip_list:
        print("No IP addresses found in the file.")
        sys.exit(1)

    print(f"Using {len(ip_list)} IP addresses from file: {ip_file_path}")
    return ip_list


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments and validate input file.

    Returns:
        argparse.Namespace: Parsed arguments with validated ip_file
    """
    parser = argparse.ArgumentParser(description='Check connectivity to a list of IP addresses using ICMP ping')
    parser.add_argument('ip_file', nargs='?', help='Text file containing IP addresses (one per line, optional if database configured)')
    parser.add_argument('-s', '--sql-file', help='SQL file to use for database IP source (optional)')
    parser.add_argument('-t', '--timeout', type=int, default=DEFAULT_PING_TIMEOUT, help=f'Ping timeout in seconds (default: {DEFAULT_PING_TIMEOUT})')
    parser.add_argument('-c', '--count', type=int, default=DEFAULT_PING_COUNT, help=f'Number of ping packets (default: {DEFAULT_PING_COUNT})')
    parser.add_argument('-w', '--workers', type=int, default=DEFAULT_WORKER_COUNT, help=f'Number of concurrent workers (default: {DEFAULT_WORKER_COUNT})')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Check if we have at least one IP source
    if not args.ip_file and not is_ip_source_database_enabled():
        print("Error: No IP source available. Provide an IP file or configure database IP source.")
        print("Set IP_SOURCE_DATABASE_URL or IP_SOURCE_DB_* environment variables.")
        sys.exit(1)

    return args


def main() -> None:
    args = parse_args()
    ip_list = get_ip_list(args.ip_file, args.sql_file)

    # Setup logging
    success_log, failure_log = setup_logging()

    print(f"Testing connectivity to {len(ip_list)} IP addresses...")
    print(f"Timeout: {args.timeout}s, Count: {args.count}, Workers: {args.workers}")
    print(f"Logs will be saved to: {success_log} and {failure_log}")
    print("-" * 60)

    start_time = time.time()
    successful = 0
    failed = 0
    all_results = []  # Collect all results for database

    # Use ThreadPoolExecutor for concurrent pings
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Submit all ping tasks
        future_to_ip = {
            executor.submit(ping_host, ip, args.timeout, args.count): ip
            for ip in ip_list
        }

        # Process results as they complete
        for future in as_completed(future_to_ip):
            ip_address, success, response_info = future.result()

            # Collect result for database
            all_results.append((ip_address, success, response_info))

            # Log the result
            log_result(ip_address, success, response_info, success_log, failure_log)

            if success:
                successful += 1
                status = "✓ REACHABLE"
                color = "\033[92m"  # Green
            else:
                failed += 1
                status = "✗ UNREACHABLE"
                color = "\033[91m"  # Red

            reset_color = "\033[0m"

            if args.verbose or not success:
                print(f"{color}{ip_address:<15} {status:<12} {response_info}{reset_color}")
            elif success:
                print(f"{color}{ip_address:<15} {status:<12} {response_info}{reset_color}")

    end_time = time.time()

    # Save to database if configured
    if is_database_enabled():
        try:
            if save_ping_results(all_results, timeout=args.timeout, count=args.count):
                print("✓ Results saved to database")
            else:
                print("⚠ Failed to save results to database")
        except Exception as e:
            print(f"⚠ Database error: {e}")
    elif args.verbose:
        print("Database logging disabled (not configured)")

    print("-" * 60)
    print(f"Results: {successful} reachable, {failed} unreachable")
    print(f"Total time: {end_time - start_time:.2f} seconds")

    # Exit with non-zero code if any hosts are unreachable
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()