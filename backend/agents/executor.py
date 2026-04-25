from state.state import AgentState
from tools.sql import execute_read_query


def sql_executor_node(state: AgentState) -> dict[str, object]:
    """
    Executes the validated SQL query against the database.
    """
    sql_query = state.get("generated_sql", "")

    try:
        results = execute_read_query(sql_query)
        return {
            "query_result": results,
            "query_error": None,
            "validation_error": None,
        }
    except Exception as e:
        return {
            "query_result": [],
            "query_error": str(e),
            "validation_error": None,
        }
