import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc


def _get_list(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _resolve_database_path(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        database_url = database_url.removeprefix("sqlite:///")
    elif database_url.startswith("sqlite://"):
        raise ValueError("Only sqlite:/// database URLs are supported.")

    return _resolve_project_path(database_url)


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None

    database_url: str
    database_path: Path
    schema_path: Path
    seed_path: Path

    llm_model: str
    llm_max_retries: int
    sql_max_retries: int

    langsmith_tracing: bool
    langsmith_api_key: str | None
    langsmith_project: str
    langsmith_run_name: str
    langsmith_tags: list[str]


database_url = os.getenv("DATABASE_URL") or os.getenv("UNIVERSITY_DB_PATH") or "db/university.db"

settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    database_url=database_url,
    database_path=_resolve_database_path(database_url),
    schema_path=_resolve_project_path(os.getenv("SCHEMA_PATH", "db/schema.sql")),
    seed_path=_resolve_project_path(os.getenv("SEED_PATH", "db/seed.sql")),
    llm_model=os.getenv("LLM_MODEL", "gpt-4o"),
    llm_max_retries=_get_int("LLM_MAX_RETRIES", 2),
    sql_max_retries=_get_int("SQL_MAX_RETRIES", 3),
    langsmith_tracing=_get_bool("LANGSMITH_TRACING", False),
    langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
    langsmith_project=os.getenv("LANGSMITH_PROJECT", "genpact-hw-task"),
    langsmith_run_name=os.getenv("LANGSMITH_RUN_NAME", "University QA LangGraph"),
    langsmith_tags=_get_list("LANGSMITH_TAGS", ["streamlit", "langgraph", "university-qa"]),
)
