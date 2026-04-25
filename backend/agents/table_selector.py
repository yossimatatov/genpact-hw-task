import json

from config import settings
from pydantic import BaseModel, Field

from services.llm import get_openai_client
from state.state import AgentState
from tools.prompts import SYSTEM_PROMPT_TABLE_SELECTOR_AGENT
from tools.sql import get_table_names


class TableSelectorOutput(BaseModel):
    selected_tables: list[str] = Field(
        description="Table names that are relevant to the user query."
    )


async def table_selector_node(state: AgentState) -> dict[str, list[str]]:
    """
    Selects relevant tables for the user query from the database schema.
    """
    client = get_openai_client()

    all_tables = get_table_names()
    formatted_tables = ", ".join(all_tables)
    query_to_use = state.get("refined_query") or state["user_query"]

    system_prompt = SYSTEM_PROMPT_TABLE_SELECTOR_AGENT.format(
        formatted_tables=formatted_tables,
    )

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_to_use},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "select_tables",
                    "description": "Select relevant database tables.",
                    "parameters": TableSelectorOutput.model_json_schema(),
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": "select_tables"}},
        temperature=0,
    )

    selected: list[str] = []
    tool_calls = response.choices[0].message.tool_calls or []
    if tool_calls:
        try:
            arguments = json.loads(tool_calls[0].function.arguments)
            selected = arguments.get("selected_tables", [])
        except json.JSONDecodeError:
            selected = []

    valid_tables = [table for table in selected if table in all_tables]
    return {"selected_tables": valid_tables or all_tables}
