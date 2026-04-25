from config import settings
from services.llm import get_openai_client
from state.state import AgentState
from tools.logger import logger
from tools.prompts import SYSTEM_PROMPT_SQL_GENERATOR_AGENT
from tools.schema import get_database_schema_string


async def sql_generator_node(state: AgentState) -> dict[str, object]:
    """
    Generates a SQL query based on the user query and selected table schemas.
    """
    client = get_openai_client()
    selected_tables = state.get("selected_tables")
    schema_context = get_database_schema_string(selected_tables)

    system_prompt = SYSTEM_PROMPT_SQL_GENERATOR_AGENT.format(
        schema_context=schema_context,
    )

    query_to_use = state.get("refined_query") or state["user_query"]
    validation_error = state.get("validation_error")
    query_error = state.get("query_error")
    retry_count = state.get("retry_count", 0)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query_to_use},
    ]

    if validation_error or query_error:
        messages.append(
            {
                "role": "user",
                "content": (
                    "The previous SQL failed. "
                    f"Validation error: {validation_error or 'none'}. "
                    f"Execution error: {query_error or 'none'}. "
                    "Generate a corrected SQLite SELECT query."
                ),
            }
        )

    temperature = 0.2 if validation_error or query_error else 0
    logger.info(f"[SQL Generator] Retry count: {retry_count}")

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=temperature,
    )

    generated_sql = response.choices[0].message.content or ""
    clean_sql = generated_sql.replace("```sql", "").replace("```", "").strip()

    logger.info(f"[SQL Generator] Generated SQL: {clean_sql[:200]}")

    should_increment = bool(validation_error or query_error)
    return {
        "generated_sql": clean_sql,
        "retry_count": retry_count + 1 if should_increment else retry_count,
        "query_error": None,
        "validation_error": None,
    }
