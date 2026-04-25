import operator
from typing import Annotated, Any, TypedDict


class AgentState(TypedDict, total=False):
    """
    Global state for the agent workflow.
    """
    user_query: str
    refined_query: str

    relevance: str
    selected_tables: list[str]

    generated_sql: str
    query_result: list[dict[str, Any]]
    query_error: str | None
    is_valid_sql: bool
    retry_count: int
    validation_error: str | None

    natural_lang_response: str
    visualization_spec: dict[str, Any] | None
    needs_visualization: bool

    logs: Annotated[list[str], operator.add]
    steps: Annotated[list[str], operator.add]
