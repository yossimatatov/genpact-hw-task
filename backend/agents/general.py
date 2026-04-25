from state.state import AgentState
from services.llm import get_openai_client
from tools.prompts import SYSTEM_PROMPT_GENERAL_AGENT

async def general_agent_node(state: AgentState):
    """
    Handles queries that aren't relevant to the specific DB domain
    Provides a helpful response and guieds the user back to the suppored topoc 
    """
    client = get_openai_client()
    user_query = state["user_query"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_GENERAL_AGENT},
        {"role": "user", "content": user_query}
    ]

    from langgraph.types import StreamWriter
    from langgraph.config import get_stream_writer

    writer: StreamWriter = get_stream_writer()

    stream = await client.chat.completions.create(
        model="gpt-4o", # TODO take from .env
        messages=messages,
        temperature=0.7,
        stream=True,
    )

    full_response = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            writer(content)
    
    return {"natural_response": full_response}
