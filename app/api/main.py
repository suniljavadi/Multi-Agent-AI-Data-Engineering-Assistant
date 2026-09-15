from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agents.orchestrator import OrchestratorAgent
from app.models.agent_models import AgentResult, ApprovalRequest, ApiResponse, InvestigationState
from app.tools.jira_tools import MockJiraService
from app.tools.sql_tools import SQLValidationTool
from app.workflows.investigation_workflow import InvestigationWorkflow

app = FastAPI(title="Multi-Agent Data Engineering Copilot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = InvestigationWorkflow()
validator = SQLValidationTool()
mock_jira = MockJiraService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/chat")
def chat(payload: dict[str, Any]) -> ApiResponse:
    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    req_id = str(uuid.uuid4())
    result = workflow.run(question)
    return ApiResponse(request_id=req_id, status="ok", result={"state": result["state"].model_dump(), "results": [item.model_dump() for item in result["results"]]})


@app.post("/api/v1/investigate")
def investigate(payload: dict[str, Any]) -> ApiResponse:
    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    req_id = str(uuid.uuid4())
    result = workflow.run(question)
    return ApiResponse(request_id=req_id, status="ok", result={"state": result["state"].model_dump(), "results": [item.model_dump() for item in result["results"]]})


@app.post("/api/v1/approve")
def approve(payload: dict[str, Any]) -> dict[str, Any]:
    approval = ApprovalRequest(
        ticket_title=payload.get("ticket_title", ""),
        ticket_description=payload.get("ticket_description", ""),
        priority=payload.get("priority", "MEDIUM"),
    )
    ticket = mock_jira.create_ticket(approval)
    return {"status": "approved", "ticket": ticket}


@app.post("/api/v1/sql/validate")
def validate_sql(payload: dict[str, Any]) -> dict[str, Any]:
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    return validator.validate(query)


@app.post("/api/v1/sql/execute")
def execute_sql(payload: dict[str, Any]) -> dict[str, Any]:
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    rows = validator.execute_read_only(query)
    return {"status": "ok", "rows": rows}


@app.get("/api/v1/jobs")
def jobs() -> list[dict[str, Any]]:
    return [{"job_name": "Customer_Load", "owner": "data-engineering", "schedule": "daily"}]


@app.get("/api/v1/incidents")
def incidents() -> list[dict[str, Any]]:
    return [{"incident_id": 1, "job_name": "Customer_Load", "error_type": "SQL_TIMEOUT"}]


@app.get("/api/v1/documents")
def documents() -> list[dict[str, Any]]:
    return [{"id": 1, "title": "ETL Runbook", "category": "etl"}]


@app.get("/api/v1/tickets")
def tickets() -> list[dict[str, Any]]:
    return list(mock_jira.tickets.values())
