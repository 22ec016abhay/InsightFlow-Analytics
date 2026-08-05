"""
database.py
===========
The bridge between Python and PostgreSQL.

Everything else in the project that needs to read from or write to
the database goes through THIS file — nobody else should be opening
raw psycopg2 connections directly.

Key ideas used here:
- Context manager (the "with" statement): guarantees the database
  connection is always closed properly, even if an error happens
  halfway through a query.
- Custom exception: a clearer error type specific to our project,
  instead of a generic Python error.
"""

import psycopg2
import psycopg2.extras
from contextlib import contextmanager

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from utils import get_logger, log_errors

logger = get_logger(__name__)


class DatabaseConnectionError(Exception):
    """Raised when InsightFlow Analytics cannot connect to PostgreSQL."""
    pass


@contextmanager
def get_connection():
    """
    Context manager that opens a PostgreSQL connection and guarantees
    it gets closed afterwards, no matter what happens in between.

    Usage:
        with get_connection() as conn:
            ... do something with conn ...
        # connection is automatically closed here, even on error
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
        logger.info(f"Connected to database '{config.DB_NAME}' at {config.DB_HOST}:{config.DB_PORT}")
        yield conn
    except psycopg2.OperationalError as exc:
        logger.error(f"Could not connect to the database: {exc}")
        raise DatabaseConnectionError(
            f"Failed to connect to '{config.DB_NAME}'. "
            f"Check that PostgreSQL is running and your .env credentials are correct."
        ) from exc
    finally:
        if conn is not None:
            conn.close()
            logger.info("Database connection closed.")


@log_errors
def run_query(sql: str, params: tuple | None = None) -> list[dict]:
    """
    Run a SELECT query and return the results as a list of dictionaries
    (one dictionary per row, column names as keys).

    Example:
        rows = run_query("SELECT * FROM stores WHERE region = %s;", ("West",))
        for row in rows:
            print(row["store_name"])
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(sql, params)
            results = cursor.fetchall()
            logger.info(f"Query returned {len(results)} row(s)")
            return [dict(row) for row in results]


@log_errors
def execute_statement(sql: str, params: tuple | None = None) -> int:
    """
    Run an INSERT / UPDATE / DELETE statement and commit the change.
    Returns the number of rows affected.

    Example:
        rows_changed = execute_statement(
            "UPDATE products SET unit_price = %s WHERE product_id = %s;",
            (29.99, 101)
        )
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
            logger.info(f"Statement affected {cursor.rowcount} row(s)")
            return cursor.rowcount


if __name__ == "__main__":
    # Quick manual test: run "python src/database.py"
    # Proves Python can actually reach PostgreSQL and read real data.
    try:
        result = run_query("SELECT COUNT(*) AS total_orders FROM orders;")
        print("Connection successful!")
        print("Total orders in database:", result[0]["total_orders"])
    except DatabaseConnectionError as exc:
        print("Connection FAILED:", exc)