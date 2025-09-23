"""
IP Source module for ping checker

Provides functionality to get IP addresses from database sources using
configurable SQL queries stored in files.
"""

import logging
from typing import List, Optional
from pathlib import Path
from constants import (
    IP_SOURCE_DATABASE_ENABLED, IP_SOURCE_DATABASE_URL,
    IP_SOURCE_DB_HOST, IP_SOURCE_DB_PORT, IP_SOURCE_DB_NAME,
    IP_SOURCE_DB_USER, IP_SOURCE_DB_PASSWORD, IP_SOURCE_DB_SCHEMA,
    IP_SOURCE_SQL_FILE, SQL_DIR
)

# Global connection object for IP source database
_ip_source_connection = None

def get_ip_source_connection():
    """
    Get IP source database connection if configured and available.

    Returns:
        psycopg2.connection or None: Database connection or None if not available
    """
    global _ip_source_connection

    if not IP_SOURCE_DATABASE_ENABLED:
        return None

    if _ip_source_connection is not None:
        try:
            # Test if connection is still alive
            with _ip_source_connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            return _ip_source_connection
        except:
            _ip_source_connection = None

    try:
        import psycopg2

        if IP_SOURCE_DATABASE_URL:
            _ip_source_connection = psycopg2.connect(IP_SOURCE_DATABASE_URL)
        else:
            _ip_source_connection = psycopg2.connect(
                host=IP_SOURCE_DB_HOST,
                port=IP_SOURCE_DB_PORT,
                database=IP_SOURCE_DB_NAME,
                user=IP_SOURCE_DB_USER,
                password=IP_SOURCE_DB_PASSWORD
            )

        # Auto-commit for simplicity
        _ip_source_connection.autocommit = True

        return _ip_source_connection

    except ImportError:
        logging.warning("psycopg2 not installed. IP source database disabled.")
        return None
    except Exception as e:
        logging.warning(f"IP source database connection failed: {e}")
        return None

def load_sql_query(sql_file: str) -> Optional[str]:
    """
    Load SQL query from file in data/sql/ directory.

    Args:
        sql_file: SQL filename (e.g., 'get_ips.sql')

    Returns:
        str: SQL query content or None if file not found
    """
    try:
        sql_path = SQL_DIR / sql_file
        if not sql_path.exists():
            logging.error(f"SQL file not found: {sql_path}")
            return None

        with open(sql_path, 'r', encoding='utf-8') as f:
            query = f.read().strip()

        if not query:
            logging.error(f"SQL file is empty: {sql_path}")
            return None

        logging.debug(f"Loaded SQL query from {sql_path}")
        return query

    except Exception as e:
        logging.error(f"Failed to load SQL file {sql_file}: {e}")
        return None

def get_ips_from_database(sql_file: str = None) -> Optional[List[str]]:
    """
    Get IP addresses from database using SQL query from file.
    Query must return a single column with IP addresses.

    Args:
        sql_file: SQL filename (defaults to IP_SOURCE_SQL_FILE from config)

    Returns:
        List[str]: List of IP addresses or None if failed
    """
    if not IP_SOURCE_DATABASE_ENABLED:
        logging.debug("IP source database not configured")
        return None

    connection = get_ip_source_connection()
    if not connection:
        logging.warning("IP source database connection not available")
        return None

    sql_file = sql_file or IP_SOURCE_SQL_FILE
    query = load_sql_query(sql_file)
    if not query:
        return None

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

            # Extract IP addresses from first column (regardless of column name)
            ip_list = []
            for row in results:
                if row and len(row) > 0:
                    ip = str(row[0]).strip()
                    if ip and ip not in ip_list:  # Avoid duplicates
                        ip_list.append(ip)

            logging.info(f"Retrieved {len(ip_list)} IP addresses from database using {sql_file}")
            return ip_list if ip_list else None

    except Exception as e:
        logging.error(f"Failed to get IPs from database: {e}")
        return None

def is_ip_source_database_enabled() -> bool:
    """
    Check if IP source database functionality is enabled and working.

    Returns:
        bool: True if IP source database is available
    """
    if not IP_SOURCE_DATABASE_ENABLED:
        logging.debug("IP source database disabled: No environment variables configured")
        return False

    connection = get_ip_source_connection()
    if connection is None:
        logging.warning("IP source database enabled in config but connection failed")
        return False

    # Check if SQL file exists
    sql_path = SQL_DIR / IP_SOURCE_SQL_FILE
    if not sql_path.exists():
        logging.warning(f"IP source database enabled but SQL file not found: {sql_path}")
        return False

    logging.debug("IP source database connection and SQL file ready")
    return True

