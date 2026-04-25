from state.state import AgentState
from tools.validator import (
    validate_sql_against_database,
    validate_sql_safety,
)


def sql_validator_node(state: AgentState) -> dict[str, object]:
    """
    Validates the generated SQL for safety.
    """
    sql_query = state.get("generated_sql", "")
    is_safe, error_message = validate_sql_safety(sql_query)
    if not is_safe:
        return {
            "is_valid_sql": False,
            "validation_error": error_message,
            "query_error": None,
        }

    is_valid_schema, error_message = validate_sql_against_database(sql_query)
    if not is_valid_schema:
        return {
            "is_valid_sql": False,
            "validation_error": error_message,
            "query_error": None,
        }

    return {
        "is_valid_sql": True,
        "validation_error": None,
        "query_error": None,
    }
