import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import settings 
from graph.graph import app_graph  


EXAMPLE_QUESTIONS = [
    "What is the average grade in Database Systems?",
    "How many students are enrolled in each course in Spring 2026?",
    "Which courses does Rachel Cohen teach?",
    "List students who failed any course.",
]


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def merge_state(current: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    merged = current.copy()
    for key, value in update.items():
        merged[key] = value
    return merged


async def run_agent(question: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    initial_state = {
        "user_query": question,
        "retry_count": 0,
        "logs": [],
        "steps": [],
    }
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {"thread_id": thread_id},
        "run_name": settings.langsmith_run_name,
        "tags": settings.langsmith_tags,
        "metadata": {
            "thread_id": thread_id,
            "entrypoint": "streamlit_app",
            "database_url": settings.database_url,
            "llm_model": settings.llm_model,
            "langsmith_tracing": settings.langsmith_tracing,
        },
    }

    final_state: dict[str, Any] = initial_state.copy()
    trace: list[dict[str, Any]] = []

    async for event in app_graph.astream(initial_state, config=config, stream_mode="updates"):
        for node_name, update in event.items():
            if not isinstance(update, dict):
                continue

            final_state = merge_state(final_state, update)
            trace.append(
                {
                    "node": node_name,
                    "update": update,
                }
            )

    return final_state, trace


def run_agent_sync(question: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    return asyncio.run(run_agent(question))


def render_trace(trace: list[dict[str, Any]]) -> None:
    if not trace:
        st.info("No trace captured.")
        return

    for index, item in enumerate(trace, start=1):
        node_name = item["node"]
        update = item["update"]
        with st.expander(f"{index}. {node_name}", expanded=False):
            st.json(update)


def render_result(final_state: dict[str, Any], trace: list[dict[str, Any]]) -> None:
    answer = final_state.get("natural_lang_response")
    if answer:
        st.subheader("Answer")
        st.write(answer)

    sql_query = final_state.get("generated_sql")
    if sql_query:
        st.subheader("SQL")
        st.code(sql_query, language="sql")

    query_error = final_state.get("query_error") or final_state.get("validation_error")
    if query_error:
        st.subheader("Error")
        st.error(str(query_error))

    rows = final_state.get("query_result")
    if rows:
        st.subheader("Rows")
        st.dataframe(rows, use_container_width=True)

    visualization_spec = final_state.get("visualization_spec")
    if visualization_spec:
        st.subheader("Visualization")
        st.vega_lite_chart(spec=visualization_spec, use_container_width=True)

    st.subheader("Trace")
    render_trace(trace)

    with st.expander("Final State", expanded=False):
        st.code(compact_json(final_state), language="json")


def main() -> None:
    st.set_page_config(
        page_title="University QA Agent",
        layout="wide",
    )

    st.title("University QA Agent")
    st.caption("Natural language questions over the university SQLite database.")

    with st.sidebar:
        st.header("Examples")
        selected_example = st.radio(
            "Pick a question",
            EXAMPLE_QUESTIONS,
            index=0,
            label_visibility="collapsed",
        )
        use_example = st.button("Use Example", use_container_width=True)

        st.divider()
        st.header("Run Notes")
        st.write("Set `OPENAI_API_KEY` and LangSmith variables in `.env` before asking a question.")

    if "question" not in st.session_state:
        st.session_state.question = EXAMPLE_QUESTIONS[0]

    if use_example:
        st.session_state.question = selected_example

    with st.form("question_form"):
        question = st.text_area(
            "Question",
            key="question",
            height=100,
            placeholder="Ask about students, teachers, courses, semesters, enrollments, or grades.",
        )
        submitted = st.form_submit_button("Ask", type="primary", use_container_width=True)

    if not submitted:
        return

    if not question.strip():
        st.warning("Enter a question first.")
        return

    with st.spinner("Running LangGraph..."):
        try:
            final_state, trace = run_agent_sync(question.strip())
        except Exception as exc:
            st.error(f"Agent failed: {exc}")
            return

    render_result(final_state, trace)


if __name__ == "__main__":
    main()
