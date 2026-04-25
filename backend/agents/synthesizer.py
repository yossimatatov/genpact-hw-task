from services.llm import get_openai_client
from state.state import AgentState
from tools.prompts import SYSTEM_PROMPT_SYNTHESIZER_AGENT


async def response_synthesizer_node(state: AgentState) -> dict[str, str]:
    """
    Synthesizes a natural language response from the SQL result.
    """
    client = get_openai_client()

    user_query = state["user_query"]
    sql_query = state.get("generated_sql", "No SQL generated")
    results = state.get("query_result", [])
    query_error = state.get("query_error")
    validation_error = state.get("validation_error")

    if query_error or validation_error:
        error = query_error or validation_error
        return {"natural_lang_response": f"I could not answer the question because the SQL failed: {error}"}

    str_results = str(results)
    if len(str_results) > 10000:
        str_results = str_results[:10000] + "... (truncated)"

    system_prompt = f"""{SYSTEM_PROMPT_SYNTHESIZER_AGENT}

User question: {user_query}
SQL query used: {sql_query}
SQL result: {str_results}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        temperature=0,
    )

    answer = response.choices[0].message.content or ""
    return {"natural_lang_response": answer.strip()}
