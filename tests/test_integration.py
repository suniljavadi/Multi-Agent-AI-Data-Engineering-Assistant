from app.agents.orchestrator import OrchestratorAgent
from app.agents.sql_agent import SQLAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.etl_agent import ETLAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.workflows.investigation_workflow import InvestigationWorkflow


def test_orchestrator_routes_complex_investigation():
    decision = OrchestratorAgent().route("Investigate why Customer_Load failed and check whether our documentation has a recommended solution.")
    assert decision.intent == "COMPLEX_INVESTIGATION"
    assert "etl_agent" in decision.agents_required


def test_sql_agent_returns_results():
    result = SQLAgent().execute("Show top 10 customers by revenue.")
    assert result.status == "SUCCESS"
    assert result.confidence > 0


def test_knowledge_agent_has_evidence():
    result = KnowledgeAgent().execute("rollback procedure")
    assert result.status == "SUCCESS"
    assert result.evidence


def test_etl_agent_reports_observed_facts():
    result = ETLAgent().execute("Why did Customer_Load fail?")
    assert result.status == "SUCCESS"
    assert any("execution duration" in item.lower() for item in result.findings)


def test_reviewer_approves_grounded_workflow():
    workflow = InvestigationWorkflow()
    result = workflow.run("Why did Customer_Load fail?")
    review = next(item for item in result["results"] if item.agent_name == "reviewer_agent")
    assert review.status == "APPROVED"


def test_workflow_builds_state():
    state = InvestigationWorkflow().orchestrator.create_state("What is the rollback procedure?")
    assert state.request_id
    assert state.intent == "KNOWLEDGE_SEARCH"
