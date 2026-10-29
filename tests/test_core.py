import pytest
from fastapi.testclient import TestClient

from app.agents.orchestrator import OrchestratorAgent
from app.api.main import app
from app.tools.sql_tools import SQLValidationTool, SQLTool
from app.tools.knowledge_tools import KnowledgeTool
from app.tools.etl_tools import ETLTool
from app.models.agent_models import RoutingDecision, ApprovalRequest
from app.database.mock_db import MockDatabase


@pytest.fixture
def orchestrator():
    return OrchestratorAgent()


@pytest.fixture
def api_client():
    return TestClient(app)


def test_orchestrator_routes_sql_query(orchestrator):
    decision = orchestrator.route("Show me customers with revenue above 100000.")
    assert isinstance(decision, RoutingDecision)
    assert decision.intent == "SQL_QUERY"
    assert "sql_agent" in decision.agents_required


def test_sql_validation_allows_safe_select():
    tool = SQLValidationTool()
    result = tool.validate("SELECT * FROM customers WHERE customer_id = 1")
    assert result["is_valid"] is True


def test_sql_validation_blocks_injection():
    tool = SQLValidationTool()
    result = tool.validate("SELECT * FROM customers WHERE customer_id = 1; DROP TABLE customers;")
    assert result["is_valid"] is False
    assert "DROP" in str(result["issues"]).upper()


def test_read_only_database_caps_returned_rows():
    db = MockDatabase(db_path=":memory:", max_rows=2, timeout_seconds=1)
    try:
        rows = db.execute_read_only(
            "SELECT 1 AS value UNION ALL SELECT 2 UNION ALL SELECT 3"
        )
        assert len(rows) == 2
        assert [row["value"] for row in rows] == [1, 2]
    finally:
        db.close()


def test_read_only_database_interrupts_timed_out_query():
    db = MockDatabase(db_path=":memory:", max_rows=2, timeout_seconds=1)
    try:
        query = """
            WITH RECURSIVE numbers(value) AS (
                SELECT 0
                UNION ALL
                SELECT value + 1 FROM numbers WHERE value < 1000000000
            )
            SELECT COUNT(*) FROM numbers
        """
        with pytest.raises(TimeoutError, match="execution timeout"):
            db.execute_read_only(query)
    finally:
        db.close()


def test_api_rejects_blank_question(api_client):
    response = api_client.post("/api/v1/chat", json={"question": "   "})
    assert response.status_code == 422


def test_api_rejects_oversized_sql(api_client):
    response = api_client.post("/api/v1/sql/validate", json={"query": " " + "x" * 10000})
    assert response.status_code == 422


def test_knowledge_tool_returns_relevant_docs():
    tool = KnowledgeTool()
    results = tool.search("rollback procedure")
    assert len(results) >= 1
    assert results[0]["source"]


def test_etl_tool_returns_history():
    tool = ETLTool()
    history = tool.get_job_history("Customer_Load")
    assert len(history) >= 1


def test_approval_model_rejects_missing_title():
    with pytest.raises(ValueError):
        ApprovalRequest(ticket_title="", ticket_description="desc")
