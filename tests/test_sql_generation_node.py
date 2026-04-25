import asyncio
from types import SimpleNamespace

import agents.sql_generator as sql_generator_agent


class FakeOpenAIClient:
    def __init__(self, content):
        self.calls = []
        self.content = content
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self.create),
        )

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.content, tool_calls=None)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


def test_sql_generator_cleans_markdown_and_uses_selected_schema(seeded_db, monkeypatch):
    fake_client = FakeOpenAIClient(
        """
        ```sql
        SELECT AVG(g.points) AS average_grade
        FROM grades g
        ```
        """
    )
    monkeypatch.setattr(sql_generator_agent, "get_openai_client", lambda: fake_client)

    state = {
        "user_query": "What is the average grade in Database Systems?",
        "selected_tables": ["courses", "course_offerings", "enrollments", "grades"],
        "retry_count": 0,
    }

    update = asyncio.run(sql_generator_agent.sql_generator_node(state))

    assert update["generated_sql"].startswith("SELECT AVG")
    assert "```" not in update["generated_sql"]
    assert update["retry_count"] == 0
    assert "CREATE TABLE grades" in fake_client.calls[0]["messages"][0]["content"]
    assert "average grade" in fake_client.calls[0]["messages"][1]["content"].lower()


def test_sql_generator_increments_retry_when_previous_error_exists(seeded_db, monkeypatch):
    fake_client = FakeOpenAIClient("SELECT COUNT(*) AS count FROM students")
    monkeypatch.setattr(sql_generator_agent, "get_openai_client", lambda: fake_client)

    state = {
        "user_query": "How many students are there?",
        "selected_tables": ["students"],
        "retry_count": 1,
        "validation_error": "no such column: student_name",
    }

    update = asyncio.run(sql_generator_agent.sql_generator_node(state))

    assert update["generated_sql"] == "SELECT COUNT(*) AS count FROM students"
    assert update["retry_count"] == 2
    assert update["validation_error"] is None
    assert "previous SQL failed" in fake_client.calls[0]["messages"][2]["content"]
