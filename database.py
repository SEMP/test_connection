"""
Database module for ping checker

Optional PostgreSQL integration for storing ping results.
Falls back gracefully if database is not configured or dependencies are missing.
"""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from constants import (
    DATABASE_ENABLED, DATABASE_URL, DB_HOST, DB_PORT,
    DB_NAME, DB_USER, DB_PASSWORD, DB_SCHEMA
)

# Global connection object
_connection = None

def get_table_name(table_name: str) -> str:
    """
    Get fully qualified table name with schema if configured.

    Args:
        table_name: Base table name

    Returns:
        str: Schema-qualified table name or just table name
    """
    if DB_SCHEMA:
        return f"{DB_SCHEMA}.{table_name}"
    return table_name

def get_database_connection():
    """
    Get database connection if configured and available.

    Returns:
        psycopg2.connection or None: Database connection or None if not available
    """
    global _connection

    if not DATABASE_ENABLED:
        return None

    if _connection is not None:
        try:
            # Test if connection is still alive
            _connection.execute('SELECT 1')
            return _connection
        except:
            _connection = None

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        if DATABASE_URL:
            _connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            _connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )

        # Auto-commit for simplicity
        _connection.autocommit = True

        # Ensure table exists
        create_table_if_not_exists(_connection)

        return _connection

    except ImportError:
        logging.warning("psycopg2 not installed. Database logging disabled. Install with: pip install psycopg2-binary")
        return None
    except Exception as e:
        logging.warning(f"Database connection failed: {e}. Continuing with file logging only.")
        return None

def create_table_if_not_exists(connection):
    """
    Create ping_results table if it doesn't exist.

    Args:
        connection: Database connection
    """
    try:
        table_name = get_table_name("ping_results")

        with connection.cursor() as cursor:
            # Create schema if specified and doesn't exist
            if DB_SCHEMA:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA};")

            # Create table with schema-qualified name
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    ip_address INET NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    success BOOLEAN NOT NULL,
                    response_time VARCHAR(20),
                    job_name VARCHAR(100),
                    timeout_seconds INTEGER,
                    ping_count INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );

                -- Create indexes for common queries
                CREATE INDEX IF NOT EXISTS idx_ping_results_timestamp ON {table_name}(timestamp);
                CREATE INDEX IF NOT EXISTS idx_ping_results_ip_address ON {table_name}(ip_address);
                CREATE INDEX IF NOT EXISTS idx_ping_results_success ON {table_name}(success);
                CREATE INDEX IF NOT EXISTS idx_ping_results_job_name ON {table_name}(job_name);
            """)
            logging.info("Database table ping_results ready")
    except Exception as e:
        logging.error(f"Failed to create database table: {e}")
        raise

def save_ping_results(results: List[Tuple[str, bool, str]], job_name: str = None,
                     timeout: int = None, count: int = None) -> bool:
    """
    Save ping results to database if configured.

    Args:
        results: List of (ip_address, success, response_time) tuples
        job_name: Optional job name for tracking
        timeout: Ping timeout used
        count: Ping count used

    Returns:
        bool: True if saved to database, False if skipped/failed
    """
    connection = get_database_connection()
    if not connection:
        return False

    try:
        timestamp = datetime.now()
        table_name = get_table_name("ping_results")

        with connection.cursor() as cursor:
            for ip_address, success, response_time in results:
                cursor.execute(f"""
                    INSERT INTO {table_name}
                    (ip_address, timestamp, success, response_time, job_name, timeout_seconds, ping_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (ip_address, timestamp, success, response_time, job_name, timeout, count))

        logging.info(f"Saved {len(results)} ping results to database")
        return True

    except Exception as e:
        logging.error(f"Failed to save ping results to database: {e}")
        return False

def get_ping_statistics(ip_address: str = None, hours: int = 24) -> Optional[dict]:
    """
    Get ping statistics from database.

    Args:
        ip_address: Specific IP to analyze (None for all IPs)
        hours: Number of hours to look back

    Returns:
        dict: Statistics or None if database not available
    """
    connection = get_database_connection()
    if not connection:
        return None

    try:
        table_name = get_table_name("ping_results")

        with connection.cursor() as cursor:
            where_clause = "WHERE timestamp >= NOW() - INTERVAL '%s hours'" % hours
            if ip_address:
                where_clause += " AND ip_address = %s"
                params = (ip_address,)
            else:
                params = ()

            cursor.execute(f"""
                SELECT
                    ip_address,
                    COUNT(*) as total_pings,
                    COUNT(*) FILTER (WHERE success = true) as successful_pings,
                    COUNT(*) FILTER (WHERE success = false) as failed_pings,
                    ROUND(
                        (COUNT(*) FILTER (WHERE success = true) * 100.0 / COUNT(*)), 2
                    ) as success_rate,
                    MIN(timestamp) as first_ping,
                    MAX(timestamp) as last_ping
                FROM {table_name}
                {where_clause}
                GROUP BY ip_address
                ORDER BY ip_address
            """, params)

            return cursor.fetchall()

    except Exception as e:
        logging.error(f"Failed to get ping statistics: {e}")
        return None

def is_database_enabled() -> bool:
    """
    Check if database functionality is enabled and working.

    Returns:
        bool: True if database is available
    """
    return get_database_connection() is not None