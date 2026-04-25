import os
import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "backend" / "data" / "university.db"
SCHEMA_PATH = PROJECT_ROOT / "schema.sql"
DB_PATH = Path(os.getenv("UNIVERSITY_DB_PATH", DEFAULT_DB_PATH))


def initialize_database() -> None:
    """
    Creates the local SQLite database from schema.sql when it does not exist.
    """
    if DB_PATH.exists():
        return

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def get_db_connection() -> sqlite3.Connection:
    """
    Establishes a connection to the SQLite database.
    """
    initialize_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_read_query(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """
    Executes a read-only SQL query and returns rows as dictionaries.
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e


def get_table_names() -> list[str]:
    """
    Retrieves all user table names from the database.
    """
    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """
    results = execute_read_query(query)
    return [row["name"] for row in results]


def get_table_schema(table_name: str) -> str:
    """
    Retrieves the CREATE statement for a specific table.
    """
    query = """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?;
    """
    results = execute_read_query(query, (table_name,))
    if results:
        return results[0]["sql"]
    return ""
