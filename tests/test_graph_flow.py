import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

import agents.rewriter as rewriter_agent
import agents.router as router_agent
import agents.sql_generator as sql_generator_agent
import agents.synthesizer as synthesizer_agent
import agents.table_selector as table_selector_agent
import agents.visualization as visualization_agent
from graph.graph import app_graph


AVERAGE_GRADE_SQL = """
SELECT AVG(g.points) AS average_grade
FROM grades g
JOIN enrollments e ON e.enrollment_id = g.enrollment_id
JOIN course_offerings co ON co.offering_id = e.offering_id
JOIN courses c ON c.course_id = co.course_id
WHERE c.course_name = 'Database Systems'
""".strip()


class FakeOpenAIClient:
    def __init__(self):
        self.calls = []
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self.create),
        )

    async def create(self, **kwargs):
        self.calls.append(kwargs)

        tool_name = self._tool_name(kwargs)
        if tool_name == "route_query":
            return self._tool_response({"relevance": "relevant"})
        if tool_name == "select_tables":
            return self._tool_response(
                {
                    "selected_tables": [
                        "courses",
                        "course_offerings",
                        "enrollments",
                        "grades",
                    ]
                }
            )
        if tool_name == "plan_visualization":
            return self._tool_response(
                {
                    "needs_visualization": False,
                    "visualization_type": None,
                    "reasoning": "Single aggregate result.",
                }
            )

        system_prompt = kwargs["messages"][0]["content"]
        if "SQL query rewriting assistant" in system_prompt:
            return self._text_response("What is the average grade in Database Systems?")
        if "expert SQL developer" in system_prompt:
            return self._text_response(AVERAGE_GRADE_SQL)
        if "helpful data assistant" in system_prompt:
            return self._text_response("The average grade in Database Systems is 80.0.")

        raise AssertionError(f"Unexpected mocked OpenAI call: {kwargs}")

    @staticmethod
    def _tool_name(kwargs):
        tools = kwargs.get("tools") or []
        if not tools:
            return None
        return tools[0]["function"]["name"]

    @staticmethod
    def _text_response(content):
        message = SimpleNamespace(content=content, tool_calls=None)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])

    @staticmethod
    def _tool_response(arguments):
        tool_call = SimpleNamespace(
            function=SimpleNamespace(arguments=json.dumps(arguments)),
        )
        message = SimpleNamespace(content=None, tool_calls=[tool_call])
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


def test_langgraph_end_to_end_flow_with_mocked_llm(seeded_db, monkeypatch):
    fake_client = FakeOpenAIClient()

    for module in (
        router_agent,
        rewriter_agent,
        table_selector_agent,
        sql_generator_agent,
        synthesizer_agent,
        visualization_agent,
    ):
        monkeypatch.setattr(module, "get_openai_client", lambda: fake_client)

    final_state, trace = asyncio.run(_run_graph("What is the average grade in Database Systems?"))

    assert final_state["relevance"] == "relevant"
    assert final_state["generated_sql"] == AVERAGE_GRADE_SQL
    assert final_state["query_result"] == [{"average_grade": 80.0}]
    assert final_state["natural_lang_response"] == "The average grade in Database Systems is 80.0."
    assert final_state["needs_visualization"] is False

    assert trace == [
        "query_router",
        "query_rewriter",
        "table_selector",
        "sql_generator",
        "sql_validator",
        "sql_executor",
        "response_synthesizer",
        "visualization_planner",
    ]


async def _run_graph(question):
    state = {
        "user_query": question,
        "retry_count": 0,
        "logs": [],
        "steps": [],
    }
    config = {"configurable": {"thread_id": str(uuid4())}}
    final_state = state.copy()
    trace = []

    async for event in app_graph.astream(state, config=config, stream_mode="updates"):
        for node_name, update in event.items():
            trace.append(node_name)
            if isinstance(update, dict):
                final_state.update(update)

    return final_state, trace
