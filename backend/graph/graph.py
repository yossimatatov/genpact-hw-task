from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from config import settings
from agents.executor import sql_executor_node
from agents.general import general_agent_node
from agents.rewriter import query_rewriter_node
from agents.router import query_router_node
from agents.sql_generator import sql_generator_node
from agents.synthesizer import response_synthesizer_node
from agents.table_selector import table_selector_node
from agents.validator import sql_validator_node
from agents.visualization import visualization_planner_node, visualization_generator_node
from state.state import AgentState
from tools.logger import logger

workflow = StateGraph(AgentState)

workflow.add_node("query_router", query_router_node)
workflow.add_node("query_rewriter", query_rewriter_node)
workflow.add_node("general_agent", general_agent_node)
workflow.add_node("table_selector", table_selector_node)
workflow.add_node("sql_generator", sql_generator_node)
workflow.add_node("sql_validator", sql_validator_node)
workflow.add_node("sql_executor", sql_executor_node)
workflow.add_node("response_synthesizer", response_synthesizer_node)
workflow.add_node("visualization_planner", visualization_planner_node)
workflow.add_node("visualization_generator", visualization_generator_node)

workflow.set_entry_point("query_router")


def router_edge(state: AgentState) -> str:
    if state.get("relevance") == "irrelevant":
        return "general_agent"
    return "query_rewriter"


def validator_edge(state: AgentState) -> str:
    if state.get("is_valid_sql"):
        return "sql_executor"

    if state.get("retry_count", 0) < settings.sql_max_retries:
        return "sql_generator"
    return "response_synthesizer"


def visualization_edge(state: AgentState) -> str:
    if state.get("needs_visualization"):
        return "visualization_generator"
    return "end"

workflow.add_conditional_edges(
    "query_router",
    router_edge,
    {
        "general_agent": "general_agent",
        "query_rewriter": "query_rewriter"
    }
)

workflow.add_edge("query_rewriter", "table_selector")
workflow.add_edge("table_selector", "sql_generator")
workflow.add_edge("sql_generator", "sql_validator")

workflow.add_conditional_edges(
    "sql_validator",
    validator_edge,
    {
        "sql_executor": "sql_executor",
        "sql_generator": "sql_generator",
        "response_synthesizer": "response_synthesizer",
    },
)


def executor_edge(state: AgentState) -> str:
    """
    Routes based on execution success or failure.
    """
    query_error = state.get("query_error")
    retry_count = state.get("retry_count", 0)

    logger.info(f"[Executor Edge] Query error: {query_error}")
    logger.info(f"[Executor Edge] Retry count: {retry_count}")

    if query_error:
        if retry_count < settings.sql_max_retries:
            logger.info("[Executor Edge] Routing to sql_generator for retry")
            return "sql_generator"
        logger.warning("[Executor Edge] Max retries reached, routing to response_synthesizer")
        return "response_synthesizer"

    logger.info("[Executor Edge] Routing to response_synthesizer")
    return "response_synthesizer"

workflow.add_conditional_edges(
    "sql_executor",
    executor_edge,
    {
        "sql_generator": "sql_generator",
        "response_synthesizer": "response_synthesizer"
    }
)
workflow.add_edge("response_synthesizer", "visualization_planner")

workflow.add_conditional_edges(
    "visualization_planner",
    visualization_edge,
    {
        "visualization_generator": "visualization_generator",
        "end": END
    }
)

workflow.add_edge("visualization_generator", END)
workflow.add_edge("general_agent", END)

checkpointer = MemorySaver()
app_graph = workflow.compile(checkpointer=checkpointer)
