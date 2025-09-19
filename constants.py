"""
Path constants for ping checker project

Centralizes all file and directory paths to avoid hardcoded paths throughout the codebase.
All paths are relative to the script directory for deployment flexibility.
"""

import os
from pathlib import Path

# Get the directory where this constants.py file is located (project root)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Configuration directory and files
CONFIG_DIR = PROJECT_ROOT / "config"
SAMPLE_IPS_FILE = CONFIG_DIR / "sample_ips.txt"
DEFAULT_IPS_FILE = CONFIG_DIR / "ips_list.txt"
DAEMON_CONFIG_FILE = CONFIG_DIR / "ping_schedule.conf"

# Log directory and files
LOGS_DIR = PROJECT_ROOT / "logs"
DAEMON_LOG_FILE = PROJECT_ROOT / "ping_daemon.log"

# Analysis output files
ANALYSIS_NEVER_RESPONDED = PROJECT_ROOT / "analysis_never_responded.txt"
ANALYSIS_ALWAYS_RESPONDED = PROJECT_ROOT / "analysis_always_responded.txt"
ANALYSIS_SOMETIMES_RESPONDED = PROJECT_ROOT / "analysis_sometimes_responded.txt"

# Virtual environment
VENV_DIR = PROJECT_ROOT / ".venv"

def ensure_directories():
    """
    Create necessary directories if they don't exist.
    Should be called at startup of any script that needs these directories.
    """
    CONFIG_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

def get_absolute_path(relative_path: str) -> Path:
    """
    Convert a relative path to absolute path relative to project root.

    Args:
        relative_path: Path relative to project root (e.g., "config/my_ips.txt")

    Returns:
        Path: Absolute path object
    """
    if os.path.isabs(relative_path):
        return Path(relative_path)
    return PROJECT_ROOT / relative_path

def resolve_ip_file_path(ip_file: str) -> Path:
    """
    Resolve IP file path with intelligent fallback logic.

    Priority:
    1. If absolute path, use as-is
    2. If exists relative to current directory, use that
    3. Try in config/ directory
    4. Return original path (will fail later with clear error)

    Args:
        ip_file: IP file path (absolute or relative)

    Returns:
        Path: Resolved path object
    """
    path = Path(ip_file)

    # If absolute path, return as-is
    if path.is_absolute():
        return path

    # Try relative to current directory first
    if path.exists():
        return path.absolute()

    # Try in config directory
    config_path = CONFIG_DIR / ip_file
    if config_path.exists():
        return config_path

    # Try in project root
    root_path = PROJECT_ROOT / ip_file
    if root_path.exists():
        return root_path

    # Return config path as default (will show clear error if doesn't exist)
    return config_path