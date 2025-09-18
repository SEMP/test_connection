#!/usr/bin/env python3
"""
Log Analysis Tool for Ping Results

Analyzes all ping log files and categorizes IPs based on their response patterns:
- Never responded: IPs that failed in all tests
- Always responded: IPs that succeeded in all tests
- Sometimes responded: IPs that had mixed results
"""

import os
import glob
from typing import Dict, Set, Tuple
from collections import defaultdict
from datetime import datetime


def parse_log_files(log_dir: str = "logs") -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Parse all log files in the directory and count successes/failures per IP.

    Args:
        log_dir: Directory containing log files

    Returns:
        tuple: (success_counts, failure_counts) - dictionaries with IP as key, count as value
    """
    if not os.path.exists(log_dir):
        print(f"Error: Log directory '{log_dir}' does not exist.")
        return {}, {}

    success_counts = defaultdict(int)
    failure_counts = defaultdict(int)

    # Find all log files
    success_files = glob.glob(os.path.join(log_dir, "*_successful.txt"))
    failure_files = glob.glob(os.path.join(log_dir, "*_failed.txt"))

    print(f"Found {len(success_files)} success log files and {len(failure_files)} failure log files")

    # Parse success files
    for file_path in success_files:
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            ip = parts[0]
                            success_counts[ip] += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    # Parse failure files
    for file_path in failure_files:
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            ip = parts[0]
                            failure_counts[ip] += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return dict(success_counts), dict(failure_counts)


def categorize_ips(success_counts: Dict[str, int], failure_counts: Dict[str, int]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Categorize IPs based on their response patterns.

    Args:
        success_counts: Dictionary of IP -> success count
        failure_counts: Dictionary of IP -> failure count

    Returns:
        tuple: (never_responded, always_responded, sometimes_responded) sets
    """
    all_ips = set(success_counts.keys()) | set(failure_counts.keys())

    never_responded = set()
    always_responded = set()
    sometimes_responded = set()

    for ip in all_ips:
        successes = success_counts.get(ip, 0)
        failures = failure_counts.get(ip, 0)

        if successes == 0 and failures > 0:
            never_responded.add(ip)
        elif failures == 0 and successes > 0:
            always_responded.add(ip)
        elif successes > 0 and failures > 0:
            sometimes_responded.add(ip)

    return never_responded, always_responded, sometimes_responded


def write_analysis_files(never_responded: Set[str], always_responded: Set[str],
                        sometimes_responded: Set[str], success_counts: Dict[str, int],
                        failure_counts: Dict[str, int]) -> None:
    """
    Write analysis results to files.

    Args:
        never_responded: Set of IPs that never responded
        always_responded: Set of IPs that always responded
        sometimes_responded: Set of IPs that sometimes responded
        success_counts: Success count per IP
        failure_counts: Failure count per IP
    """
    analysis_time = datetime.now()

    # Never responded IPs
    with open("analysis_never_responded.txt", 'w') as f:
        f.write(f"# IPs that never responded (analysis generated on {analysis_time})\n")
        f.write(f"# Total IPs: {len(never_responded)}\n")
        f.write("# Format: IP_ADDRESS\tFAILED_COUNT\n\n")
        for ip in sorted(never_responded):
            failures = failure_counts.get(ip, 0)
            f.write(f"{ip}\t{failures}\n")

    # Always responded IPs
    with open("analysis_always_responded.txt", 'w') as f:
        f.write(f"# IPs that always responded (analysis generated on {analysis_time})\n")
        f.write(f"# Total IPs: {len(always_responded)}\n")
        f.write("# Format: IP_ADDRESS\tSUCCESS_COUNT\n\n")
        for ip in sorted(always_responded):
            successes = success_counts.get(ip, 0)
            f.write(f"{ip}\t{successes}\n")

    # Sometimes responded IPs
    with open("analysis_sometimes_responded.txt", 'w') as f:
        f.write(f"# IPs that sometimes responded (analysis generated on {analysis_time})\n")
        f.write(f"# Total IPs: {len(sometimes_responded)}\n")
        f.write("# Format: IP_ADDRESS\tSUCCESS_COUNT\tFAILED_COUNT\tSUCCESS_RATE\n\n")
        for ip in sorted(sometimes_responded):
            successes = success_counts.get(ip, 0)
            failures = failure_counts.get(ip, 0)
            total = successes + failures
            success_rate = (successes / total * 100) if total > 0 else 0
            f.write(f"{ip}\t{successes}\t{failures}\t{success_rate:.1f}%\n")

    print(f"Analysis files updated:")
    print(f"  - analysis_never_responded.txt ({len(never_responded)} IPs)")
    print(f"  - analysis_always_responded.txt ({len(always_responded)} IPs)")
    print(f"  - analysis_sometimes_responded.txt ({len(sometimes_responded)} IPs)")


def main() -> None:
    """Main function to run log analysis."""
    print("Analyzing ping log files...")
    print("-" * 50)

    # Parse log files
    success_counts, failure_counts = parse_log_files()

    if not success_counts and not failure_counts:
        print("No log data found. Run some ping tests first.")
        return

    # Categorize IPs
    never_responded, always_responded, sometimes_responded = categorize_ips(success_counts, failure_counts)

    # Print summary
    total_ips = len(never_responded) + len(always_responded) + len(sometimes_responded)
    print(f"\nAnalysis Summary:")
    print(f"  Total unique IPs tested: {total_ips}")
    print(f"  Never responded: {len(never_responded)} IPs")
    print(f"  Always responded: {len(always_responded)} IPs")
    print(f"  Sometimes responded: {len(sometimes_responded)} IPs")

    if total_ips == 0:
        print("No valid IP data found in log files.")
        return

    # Write analysis files
    write_analysis_files(never_responded, always_responded, sometimes_responded,
                        success_counts, failure_counts)

    print(f"\nAnalysis complete!")


if __name__ == "__main__":
    main()