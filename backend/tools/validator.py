import re

from tools.sql import get_db_connection

FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "TRUNCATE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "GRANT",
    "REVOKE",
    "CREATE",
    "REPLACE",
]


def validate_sql_safety(query: str) -> tuple[bool, str]:
    """
    Validates that the SQL query is read-only and safe to execute.
    """
    stripped = query.strip()
    if not stripped:
        return False, "SQL query is empty."

    normalized = stripped.upper()
    if not re.match(r"^(SELECT|WITH)\b", normalized):
        return False, "Only SELECT or WITH queries are allowed."

    without_final_semicolon = stripped[:-1] if stripped.endswith(";") else stripped
    if ";" in without_final_semicolon:
        return False, "Multiple SQL statements are not allowed."

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(r"\b" + keyword + r"\b", normalized):
            return False, f"SQL query contains forbidden keyword: {keyword}"

    return True, ""


def validate_sql_against_database(query: str) -> tuple[bool, str]:
    """
    Validates that SQLite can compile the query against the current database schema.
    """
    stripped = query.strip()
    if stripped.endswith(";"):
        stripped = stripped[:-1].strip()

    try:
        with get_db_connection() as conn:
            conn.execute(f"EXPLAIN QUERY PLAN {stripped}")
    except Exception as e:
        return False, f"SQL does not match the database schema: {e}"

    return True, ""


# Backward-compatible alias for older imports.
valudate_sql_safety = validate_sql_safety
