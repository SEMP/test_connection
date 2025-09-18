#!/usr/bin/env python3
"""
ICMP Ping Connectivity Checker

Reads a list of IP addresses from a text file and tests connectivity
using ICMP ping. Reports success/failure for each IP.
"""

import subprocess
import sys
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Tuple


def ping_host(ip_address: str, timeout: int = 3, count: int = 1) -> Tuple[str, bool, str]:
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
        # Use system ping command
        cmd = ['ping', '-c', str(count), '-W', str(timeout), ip_address]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)

        if result.returncode == 0:
            # Extract response time from ping output
            lines = result.stdout.split('\n')
            for line in lines:
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


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments and validate input file.

    Returns:
        argparse.Namespace: Parsed arguments with validated ip_file
    """
    parser = argparse.ArgumentParser(description='Check connectivity to a list of IP addresses using ICMP ping')
    parser.add_argument('ip_file', help='Text file containing IP addresses (one per line)')
    parser.add_argument('-t', '--timeout', type=int, default=3, help='Ping timeout in seconds (default: 3)')
    parser.add_argument('-c', '--count', type=int, default=1, help='Number of ping packets (default: 1)')
    parser.add_argument('-w', '--workers', type=int, default=10, help='Number of concurrent workers (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Check if file exists
    if not Path(args.ip_file).exists():
        print(f"Error: File '{args.ip_file}' does not exist.")
        sys.exit(1)

    # Read IP addresses
    ip_list = read_ip_list(args.ip_file)
    if not ip_list:
        print("No IP addresses found in the file.")
        sys.exit(1)

    return args


def main() -> None:
    args = parse_args()
    ip_list = read_ip_list(args.ip_file)

    print(f"Testing connectivity to {len(ip_list)} IP addresses...")
    print(f"Timeout: {args.timeout}s, Count: {args.count}, Workers: {args.workers}")
    print("-" * 60)

    start_time = time.time()
    successful = 0
    failed = 0

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

    print("-" * 60)
    print(f"Results: {successful} reachable, {failed} unreachable")
    print(f"Total time: {end_time - start_time:.2f} seconds")

    # Exit with non-zero code if any hosts are unreachable
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()