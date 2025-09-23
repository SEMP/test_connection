"""
Path constants for ping checker project

Centralizes all file and directory paths to avoid hardcoded paths throughout the codebase.
All paths are relative to the script directory for deployment flexibility.
"""

import os
from pathlib import Path

# Get the directory where this constants.py file is located (project root)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Data directory (for Docker volumes)
DATA_DIR = PROJECT_ROOT / "data"

# Configuration directory and files
CONFIG_DIR = DATA_DIR / "config"
SAMPLE_IPS_FILE = CONFIG_DIR / "sample_ips.txt"
DEFAULT_IPS_FILE = CONFIG_DIR / "ips_list.txt"
DAEMON_CONFIG_FILE = CONFIG_DIR / "ping_schedule.conf"

# Log directory and files
LOGS_DIR = DATA_DIR / "logs"
DAEMON_LOG_FILE = PROJECT_ROOT / "ping_daemon.log"

# Analysis directory and output files
ANALYSIS_DIR = DATA_DIR / "analysis"
ANALYSIS_NEVER_RESPONDED = ANALYSIS_DIR / "never_responded.txt"
ANALYSIS_ALWAYS_RESPONDED = ANALYSIS_DIR / "always_responded.txt"
ANALYSIS_SOMETIMES_RESPONDED = ANALYSIS_DIR / "sometimes_responded.txt"

# Virtual environment
VENV_DIR = PROJECT_ROOT / ".venv"

# Default values for ping operations
DEFAULT_PING_TIMEOUT = 3
DEFAULT_PING_COUNT = 1
DEFAULT_WORKER_COUNT = 10

# Database configuration (optional)
# Set these environment variables to enable database logging:
# DATABASE_URL=postgresql://user:password@host:port/database
# Or set individual variables:
# DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ping_checker')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_SCHEMA = os.getenv('DB_SCHEMA')  # Optional schema (defaults to 'public' in PostgreSQL)

# Build DATABASE_URL from individual vars if not explicitly set
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL and DB_USER and DB_PASSWORD and DB_NAME:
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Database enabled if DATABASE_URL is available (either set directly or built from vars)
DATABASE_ENABLED = bool(DATABASE_URL)

# IP Source Database Configuration (optional)
# Set these environment variables to get IP lists from a database instead of files:
IP_SOURCE_DATABASE_URL = os.getenv('IP_SOURCE_DATABASE_URL')
IP_SOURCE_DB_HOST = os.getenv('IP_SOURCE_DB_HOST', 'localhost')
IP_SOURCE_DB_PORT = os.getenv('IP_SOURCE_DB_PORT', '5432')
IP_SOURCE_DB_NAME = os.getenv('IP_SOURCE_DB_NAME')
IP_SOURCE_DB_USER = os.getenv('IP_SOURCE_DB_USER')
IP_SOURCE_DB_PASSWORD = os.getenv('IP_SOURCE_DB_PASSWORD')
IP_SOURCE_DB_SCHEMA = os.getenv('IP_SOURCE_DB_SCHEMA')

# SQL file to get IP addresses (relative to data/sql/ directory)
IP_SOURCE_SQL_FILE = os.getenv('IP_SOURCE_SQL_FILE', 'get_ips.sql')

# Build IP_SOURCE_DATABASE_URL from individual vars if not explicitly set
if not IP_SOURCE_DATABASE_URL and IP_SOURCE_DB_USER and IP_SOURCE_DB_PASSWORD and IP_SOURCE_DB_NAME:
    IP_SOURCE_DATABASE_URL = f'postgresql://{IP_SOURCE_DB_USER}:{IP_SOURCE_DB_PASSWORD}@{IP_SOURCE_DB_HOST}:{IP_SOURCE_DB_PORT}/{IP_SOURCE_DB_NAME}'

# IP source database enabled if URL is available
IP_SOURCE_DATABASE_ENABLED = bool(IP_SOURCE_DATABASE_URL)

# SQL directory for IP source queries
SQL_DIR = DATA_DIR / "sql"

def ensure_directories():
    """
    Create necessary directories if they don't exist.
    Should be called at startup of any script that needs these directories.
    """
    DATA_DIR.mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    ANALYSIS_DIR.mkdir(exist_ok=True)

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