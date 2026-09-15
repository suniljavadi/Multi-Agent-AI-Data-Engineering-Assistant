from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

IntentType = Literal[
    "SQL_QUERY",
    "ETL_INVESTIGATION",
    "KNOWLEDGE_SEARCH",
    "DATA_ANALYSIS",
    "SQL_OPTIMIZATION",
    "COMPLEX_INVESTIGATION",
    "TICKET_REQUEST",
]


class RoutingDecision(BaseModel):
    intent: IntentType
    agents_required: list[str] = Field(default_factory=list)
    reason: str


class InvestigationState(BaseModel):
    request_id: str
    user_question: str
    intent: str | None = None
    plan: list[str] = Field(default_factory=list)
    agent_results: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    review_status: str = "PENDING"
    final_answer: str | None = None


class AgentResult(BaseModel):
    agent_name: str
    status: str
    summary: str
    findings: list[str] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if value < 0.0 or value > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return value


class EvidenceItem(BaseModel):
    source: str
    section: str | None = None
    chunk: str | None = None
    score: float | None = None
    details: str | None = None


class ToolCallRecord(BaseModel):
    request_id: str
    agent: str
    tool: str
    status: str
    duration_ms: int
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    ticket_title: str
    ticket_description: str
    priority: str = "MEDIUM"
    approval_required: bool = True

    @field_validator("ticket_title", "ticket_description")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if value is None or not value.strip():
            raise ValueError("This field is required.")
        return value.strip()


class ApiResponse(BaseModel):
    request_id: str
    status: str
    result: dict[str, Any]
