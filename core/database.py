"""
core/database.py
----------------
PostgreSQL connection and query execution.
No Streamlit dependency — pure Python, fully testable.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import psycopg2

from core.config import settings


@dataclass
class QueryResult:
    data: pd.DataFrame | None
    success: bool
    row_count: int
    elapsed_ms: float
    error: str | None = None


def run_query(sql: str) -> QueryResult:
    """
    Execute a SELECT query against the configured PostgreSQL database.

    Args:
        sql: A valid PostgreSQL SELECT statement.

    Returns:
        QueryResult with a DataFrame on success, or an error message on failure.
    """
    import time

    db = settings.database
    start = time.perf_counter()

    try:
        conn = psycopg2.connect(
            host=db.host,
            port=db.port,
            dbname=db.name,
            user=db.user,
            password=db.password,
            connect_timeout=10,
        )
        df = pd.read_sql_query(sql, conn)
        conn.close()

        elapsed_ms = (time.perf_counter() - start) * 1000

        return QueryResult(
            data=df,
            success=True,
            row_count=len(df),
            elapsed_ms=round(elapsed_ms, 1),
        )

    except psycopg2.OperationalError as exc:
        return QueryResult(
            data=None,
            success=False,
            row_count=0,
            elapsed_ms=0,
            error=f"Connection failed: {exc}",
        )
    except Exception as exc:  # noqa: BLE001
        return QueryResult(
            data=None,
            success=False,
            row_count=0,
            elapsed_ms=0,
            error=str(exc),
        )
