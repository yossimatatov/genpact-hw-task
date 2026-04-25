from config import settings
from services.llm import get_openai_client
from state.state import AgentState
from tools.prompts import SYSTEM_PROMPT_REWRITER_AGENT


async def query_rewriter_node(state: AgentState) -> dict[str, str]:
    """
    Rewrites the user query to be more specific and SQL-friendly.
    """
    client = get_openai_client()
    user_query = state["user_query"]

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_REWRITER_AGENT},
            {"role": "user", "content": user_query},
        ],
        temperature=0,
    )

    refined_query = response.choices[0].message.content or user_query
    return {"refined_query": refined_query.strip()}
