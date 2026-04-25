import json
from typing import Literal

from pydantic import BaseModel, Field

from services.llm import get_openai_client
from state.state import AgentState
from tools.prompts import SYSTEM_PROMPT_VISUALIZATION_AGENT


def _format_visualization_prompt(query_to_use: str, results: object) -> str:
    return (
        SYSTEM_PROMPT_VISUALIZATION_AGENT
        .replace("{query_to_use}", query_to_use)
        .replace("{json.dumps(results)}", json.dumps(results))
    )


class VizPlannerOutput(BaseModel):
    needs_visualization: bool = Field(
        description="Whether the user asked for or would benefit from a visualization."
    )
    visualization_type: Literal["bar", "line", "pie", "scatter"] | None = Field(
        description="Type of chart to generate if needed."
    )
    reasoning: str = Field(description="Why visualization is needed or not.")


async def visualization_planner_node(state: AgentState) -> dict[str, bool]:
    """
    Decides if a visualization is needed.
    """
    client = get_openai_client()

    query_to_use = state.get("refined_query") or state["user_query"]
    results = state.get("query_result", [])

    if not results or state.get("query_error"):
        return {"needs_visualization": False}

    visualization_prompt = _format_visualization_prompt(query_to_use, results[:5])
    system_prompt = f"""{visualization_prompt}

Rules:
- If the user explicitly asks for a plot, chart, graph, or visualization, return true.
- If the result is a single number or a short text answer, return false.
- If the result compares categories or changes across semesters/years, return true.
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "plan_visualization",
                    "description": "Plan whether a visualization is needed.",
                    "parameters": VizPlannerOutput.model_json_schema(),
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": "plan_visualization"}},
        temperature=0,
    )

    tool_calls = response.choices[0].message.tool_calls or []
    if tool_calls:
        arguments = json.loads(tool_calls[0].function.arguments)
        return {"needs_visualization": bool(arguments.get("needs_visualization", False))}

    return {"needs_visualization": False}


async def visualization_generator_node(state: AgentState) -> dict[str, object]:
    """
    Generates a Vega-Lite specification for the data.
    """
    client = get_openai_client()

    query_to_use = state.get("refined_query") or state["user_query"]
    results = state.get("query_result", [])

    system_prompt = _format_visualization_prompt(query_to_use, results)

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    try:
        spec = json.loads(response.choices[0].message.content or "{}")
        return {"visualization_spec": spec}
    except json.JSONDecodeError:
        return {"visualization_spec": None}
