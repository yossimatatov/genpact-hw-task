import json
from typing import Literal

from config import settings
from pydantic import BaseModel, Field

from services.llm import get_openai_client
from state.state import AgentState
from tools.prompts import SYSTEM_PROMPT_ROUTER_AGENT


class RouterOutput(BaseModel):
    relevance: Literal["relevant", "irrelevant"] = Field(
        description="Whether the question should be answered from the university database."
    )


async def query_router_node(state: AgentState) -> dict[str, str]:
    """
    Determines if the user query is relevant to the database.
    """
    client = get_openai_client()

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_ROUTER_AGENT},
            {"role": "user", "content": state["user_query"]},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "route_query",
                    "description": "Route the user query based on database relevance.",
                    "parameters": RouterOutput.model_json_schema(),
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": "route_query"}},
        temperature=0,
    )

    tool_calls = response.choices[0].message.tool_calls or []
    if tool_calls:
        arguments = json.loads(tool_calls[0].function.arguments)
        relevance = arguments.get("relevance", "irrelevant")
        if relevance in {"relevant", "irrelevant"}:
            return {"relevance": relevance}

    return {"relevance": "irrelevant"}
