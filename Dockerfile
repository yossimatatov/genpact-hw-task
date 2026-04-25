FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

RUN python -m pip install --upgrade pip \
    && python -m pip install \
        langgraph \
        langchain \
        langchain-openai \
        langsmith \
        sqlalchemy \
        python-dotenv \
        pytest \
        openai \
        streamlit

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "python scripts/seed_database.py && streamlit run frontend/streamlit_app.py --server.address=0.0.0.0 --server.port=8501"]
