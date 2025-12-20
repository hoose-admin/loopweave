"""
Database connection and query utilities for Cloud SQL PostgreSQL.
"""
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import execute_batch, RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from psycopg2 import sql
import pandas as pd


# Connection pool (initialized on first use)
_connection_pool: Optional[ThreadedConnectionPool] = None


def get_connection_string() -> str:
    """
    Build PostgreSQL connection string from environment variables.
    
    Supports Cloud SQL Proxy via Unix socket (recommended) or direct connection.
    """
    user = os.getenv("CLOUDSQL_USER", "loopweave_app")
    password = os.getenv("CLOUDSQL_PASSWORD", "")
    database = os.getenv("CLOUDSQL_DATABASE_NAME", "loopweave")
    
    # Check if using Cloud SQL Proxy via Unix socket
    connection_name = os.getenv("CLOUDSQL_INSTANCE_CONNECTION_NAME")
    if connection_name:
        # Unix socket connection (no SSL needed, no port)
        host = f"/cloudsql/{connection_name}"
        return f"postgresql://{user}:{password}@{host}/{database}"
    else:
        # Fallback to direct connection (for local development)
        host = os.getenv("CLOUDSQL_HOST", os.getenv("CLOUDSQL_PUBLIC_IP", "localhost"))
        port = os.getenv("CLOUDSQL_PORT", "5432")
        # Direct connection with SSL (Cloud SQL requires SSL for public IP)
        return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"


def get_connection_pool() -> ThreadedConnectionPool:
    """Get or create connection pool."""
    global _connection_pool
    
    if _connection_pool is None:
        conn_string = get_connection_string()
        # Pool size: 5-10 connections for small instance
        _connection_pool = ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dsn=conn_string
        )
    
    return _connection_pool


@contextmanager
def get_db_connection():
    """
    Get a database connection from the pool.
    
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ...")
    """
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return results as list of dictionaries.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters for parameterized query
        
    Returns:
        List of dictionaries (one per row)
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]


def execute_query_dataframe(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """
    Execute a SELECT query and return results as pandas DataFrame.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters for parameterized query
        
    Returns:
        pandas DataFrame
    """
    with get_db_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute_insert(table: str, rows: List[Dict[str, Any]], on_conflict: Optional[str] = None) -> int:
    """
    Insert rows into a table using batch INSERT.
    
    Args:
        table: Table name
        rows: List of dictionaries (one per row)
        on_conflict: Optional ON CONFLICT clause (e.g., "ON CONFLICT (symbol, date) DO UPDATE SET ...")
        
    Returns:
        Number of rows inserted
    """
    if not rows:
        return 0
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get column names from first row
            columns = list(rows[0].keys())
            placeholders = ["%s"] * len(columns)
            
            # Build INSERT statement
            insert_query = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            if on_conflict:
                insert_query += f" {on_conflict}"
            
            # Prepare data
            values = [tuple(row[col] for col in columns) for row in rows]
            
            # Execute batch insert
            execute_batch(cur, insert_query, values, page_size=1000)
            
            return len(rows)


def execute_copy(table: str, rows: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> int:
    """
    Insert rows using PostgreSQL COPY (fastest for bulk inserts).
    
    Args:
        table: Table name
        rows: List of dictionaries (one per row)
        columns: Optional list of column names (uses all keys from first row if not provided)
        
    Returns:
        Number of rows inserted
    """
    if not rows:
        return 0
    
    if columns is None:
        columns = list(rows[0].keys())
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Create StringIO-like object for COPY
            from io import StringIO
            import csv
            
            output = StringIO()
            writer = csv.writer(output)
            
            for row in rows:
                writer.writerow([row.get(col) for col in columns])
            
            output.seek(0)
            
            # Use COPY FROM
            cur.copy_expert(
                sql.SQL("COPY {} ({}) FROM STDIN WITH CSV").format(
                    sql.Identifier(table),
                    sql.SQL(', ').join(sql.Identifier(col) for col in columns)
                ),
                output
            )
            
            return len(rows)


def get_latest_timestamp(symbol: str, table: str) -> Optional[str]:
    """
    Get the latest timestamp for a symbol from a table.
    
    Args:
        symbol: Stock symbol
        table: Table name (timeseries or timeseries_4h)
        
    Returns:
        Latest timestamp as ISO string, or None if no data
    """
    query = f"""
        SELECT MAX(date) AS latest_date
        FROM {table}
        WHERE symbol = %s
    """
    
    result = execute_query(query, (symbol,))
    if result and result[0].get("latest_date"):
        return result[0]["latest_date"].isoformat()
    return None


def update_timeseries_metrics(
    symbol: str,
    table: str,
    metrics: List[Dict[str, Any]]
) -> int:
    """
    Update metrics for timeseries rows.
    
    Args:
        symbol: Stock symbol
        table: Table name (timeseries or timeseries_4h)
        metrics: List of dicts with 'date' and metric fields to update
        
    Returns:
        Number of rows updated
    """
    if not metrics:
        return 0
    
    # Get all metric column names (excluding symbol and date)
    metric_columns = [k for k in metrics[0].keys() if k not in ('symbol', 'date')]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            updated = 0
            for metric_row in metrics:
                # Build SET clause
                set_clause = ', '.join([f"{col} = %s" for col in metric_columns])
                values = [metric_row.get(col) for col in metric_columns]
                values.extend([symbol, metric_row['date']])
                
                update_query = f"""
                    UPDATE {table}
                    SET {set_clause}
                    WHERE symbol = %s AND date = %s
                """
                
                cur.execute(update_query, values)
                updated += cur.rowcount
            
            return updated
