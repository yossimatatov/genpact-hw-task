from collections import deque

from tools.sql import execute_read_query, get_table_names, get_table_schema


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def get_database_schema_string(table_names: list[str] | None = None) -> str:
    """
    Returns a formatted schema string for selected tables, or all tables.
    """
    if not table_names:
        table_names = get_table_names()

    schema_parts = []
    for table in table_names:
        schema = get_table_schema(table)
        if schema:
            schema_parts.append(schema)

    return "\n\n".join(schema_parts)


def get_all_table_names_formatted() -> str:
    """
    Returns a comma-separated string of all table names.
    """
    return ", ".join(get_table_names())


def get_table_relationships() -> list[dict[str, str]]:
    """
    Returns foreign-key relationships between user tables.
    """
    relationships: list[dict[str, str]] = []
    for table in get_table_names():
        rows = execute_read_query(f"PRAGMA foreign_key_list({_quote_identifier(table)})")
        for row in rows:
            relationships.append(
                {
                    "from_table": table,
                    "from_column": row["from"],
                    "to_table": row["table"],
                    "to_column": row["to"],
                }
            )
    return relationships


def _shortest_table_path(
    start: str,
    end: str,
    adjacency: dict[str, set[str]],
) -> list[str]:
    queue: deque[list[str]] = deque([[start]])
    visited = {start}

    while queue:
        path = queue.popleft()
        current = path[-1]
        if current == end:
            return path

        for neighbor in adjacency.get(current, set()):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append(path + [neighbor])

    return []


def expand_tables_with_relationships(table_names: list[str]) -> list[str]:
    """
    Adds foreign-key bridge tables required to join the selected tables.
    """
    all_tables = get_table_names()
    selected = [table for table in table_names if table in all_tables]
    if len(selected) <= 1:
        return selected

    adjacency = {table: set() for table in all_tables}
    for relationship in get_table_relationships():
        from_table = relationship["from_table"]
        to_table = relationship["to_table"]
        adjacency[from_table].add(to_table)
        adjacency[to_table].add(from_table)

    expanded = set(selected)
    for index, start in enumerate(selected):
        for end in selected[index + 1:]:
            path = _shortest_table_path(start, end, adjacency)
            expanded.update(path)

    return [table for table in all_tables if table in expanded]
