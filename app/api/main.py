from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.models.agent_models import (
    ApiResponse,
    ApprovalRequest,
    QuestionRequest,
    SQLQueryRequest,
)
from app.tools.jira_tools import MockJiraService
from app.tools.sql_tools import SQLValidationTool
from app.workflows.investigation_workflow import InvestigationWorkflow

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
def chat(payload: QuestionRequest) -> ApiResponse:
    req_id = str(uuid.uuid4())
    result = workflow.run(payload.question)
    return ApiResponse(request_id=req_id, status="ok", result={"state": result["state"].model_dump(), "results": [item.model_dump() for item in result["results"]]})


@app.post("/api/v1/investigate")
def investigate(payload: QuestionRequest) -> ApiResponse:
    req_id = str(uuid.uuid4())
    result = workflow.run(payload.question)
    return ApiResponse(request_id=req_id, status="ok", result={"state": result["state"].model_dump(), "results": [item.model_dump() for item in result["results"]]})


@app.post("/api/v1/approve")
def approve(payload: ApprovalRequest) -> dict[str, Any]:
    ticket = mock_jira.create_ticket(payload)
    return {"status": "approved", "ticket": ticket}


@app.post("/api/v1/sql/validate")
def validate_sql(payload: SQLQueryRequest) -> dict[str, Any]:
    return validator.validate(payload.query)


@app.post("/api/v1/sql/execute")
def execute_sql(payload: SQLQueryRequest) -> dict[str, Any]:
    try:
        rows = validator.execute_read_only(payload.query)
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
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
