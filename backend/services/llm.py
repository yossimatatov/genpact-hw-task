from config import settings
from langsmith.wrappers import wrap_openai
from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """
    Returns a configured AsyncOpenAI client.
    """
    global _client
    if _client is None:
        api_key = settings.openai_api_key
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        client = AsyncOpenAI(
            api_key=api_key,
            max_retries=settings.llm_max_retries,
        )
        _client = wrap_openai(client) if settings.langsmith_tracing else client
    return _client
