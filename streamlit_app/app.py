from __future__ import annotations

import json
from typing import Any

import requests
import streamlit as st


API_BASE = "http://localhost:8000"


st.set_page_config(page_title="Multi-Agent Data Engineering Copilot", layout="wide")


def call_api(path: str, payload: dict[str, Any] | None = None) -> Any:
    url = f"{API_BASE}{path}"
    response = requests.post(url, json=payload or {}, timeout=20)
    response.raise_for_status()
    return response.json()


st.title("Multi-Agent Data Engineering Copilot")

page = st.sidebar.selectbox(
    "Pages",
    [
        "AI Assistant",
        "SQL Assistant",
        "ETL Investigation",
        "Knowledge Search",
        "Incident Explorer",
        "Agent Activity",
    ],
)

if page == "AI Assistant":
    question = st.text_area("Ask a question", value="Show me customers with revenue above 100000.")
    if st.button("Run"):
        result = call_api("/api/v1/chat", {"question": question})
        st.json(result)

if page == "SQL Assistant":
    query = st.text_area("SQL query", value="SELECT customer_name, revenue FROM customers WHERE revenue > 100000 ORDER BY revenue DESC")
    if st.button("Validate"):
        result = call_api("/api/v1/sql/validate", {"query": query})
        st.json(result)
    if st.button("Execute"):
        result = call_api("/api/v1/sql/execute", {"query": query})
        st.json(result)

if page == "ETL Investigation":
    question = st.text_area("ETL investigation", value="Why did Customer_Load fail?")
    if st.button("Investigate"):
        result = call_api("/api/v1/investigate", {"question": question})
        st.json(result)

if page == "Knowledge Search":
    query = st.text_area("Search docs", value="What is the rollback procedure?")
    if st.button("Search"):
        result = call_api("/api/v1/investigate", {"question": query})
        st.json(result)

if page == "Incident Explorer":
    incidents = requests.get(f"{API_BASE}/api/v1/incidents", timeout=20).json()
    st.table(incidents)

if page == "Agent Activity":
    st.markdown("""
    Orchestrator -> SQL Agent -> Tool -> Reviewer

    This panel intentionally displays only safe execution metadata and not hidden reasoning.
    """)
    st.json({"status": "safe metadata", "agents": ["orchestrator", "sql_agent", "reviewer_agent"]})
