import pytest

from app.agents.orchestrator import OrchestratorAgent
from app.tools.sql_tools import SQLValidationTool, SQLTool
from app.tools.knowledge_tools import KnowledgeTool
from app.tools.etl_tools import ETLTool
from app.models.agent_models import RoutingDecision, ApprovalRequest


@pytest.fixture
def orchestrator():
    return OrchestratorAgent()


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
