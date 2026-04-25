import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """
    Returns a configured AsyncOpenAI client.
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        _client = AsyncOpenAI(api_key=api_key)
    return _client
