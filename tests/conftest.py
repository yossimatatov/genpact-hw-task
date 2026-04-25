import sys
import os
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = ""

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture()
def seeded_db(tmp_path, monkeypatch):
    from tools import sql as sql_tools

    db_path = tmp_path / "university_test.db"
    monkeypatch.setattr(sql_tools, "DB_PATH", db_path)
    monkeypatch.setattr(sql_tools, "SCHEMA_PATH", PROJECT_ROOT / "db" / "schema.sql")
    monkeypatch.setattr(sql_tools, "SEED_PATH", PROJECT_ROOT / "db" / "seed.sql")

    sql_tools.seed_database(reset=True)

    return db_path
