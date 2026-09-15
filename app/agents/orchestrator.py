from __future__ import annotations

import re
import uuid
from typing import Any

from app.models.agent_models import InvestigationState, RoutingDecision


class OrchestratorAgent:
    def route(self, user_question: str) -> RoutingDecision:
        question = user_question.strip()
        if not question:
            raise ValueError("Question cannot be empty.")

        lowered = question.lower()
        if any(keyword in lowered for keyword in ["investigate", "and check whether", "documentation has a recommended solution", "recommended solution"]):
            return RoutingDecision(
                intent="COMPLEX_INVESTIGATION",
                agents_required=["etl_agent", "knowledge_agent"],
                reason="This needs both ETL evidence and operational documentation.",
            )
        if any(keyword in lowered for keyword in ["rollback", "deployment", "documentation", "procedure", "incident response", "known issue"]):
            return RoutingDecision(
                intent="KNOWLEDGE_SEARCH",
                agents_required=["knowledge_agent"],
                reason="User asks for documentation, procedure, or operational guidance.",
            )
        if any(keyword in lowered for keyword in ["customer_load", "failed", "why did", "job failed", "etl", "pipeline", "incident"]):
            return RoutingDecision(
                intent="ETL_INVESTIGATION",
                agents_required=["etl_agent"],
                reason="The request requires ETL log and incident investigation.",
            )
        if any(keyword in lowered for keyword in ["optimiz", "explain this sql", "query performance", "select *", "distinct", "join"]):
            return RoutingDecision(
                intent="SQL_OPTIMIZATION",
                agents_required=["sql_agent"],
                reason="This request focuses on SQL quality, safety, and performance analysis.",
            )
        if any(keyword in lowered for keyword in ["revenue", "customers", "orders", "sales", "anomal", "summarize"]):
            return RoutingDecision(
                intent="SQL_QUERY",
                agents_required=["sql_agent"],
                reason="This is a business SQL/data analysis request.",
            )
        if "ticket" in lowered:
            return RoutingDecision(
                intent="TICKET_REQUEST",
                agents_required=["etl_agent"],
                reason="User requests ticket creation after confirming an incident.",
            )
        return RoutingDecision(
            intent="KNOWLEDGE_SEARCH",
            agents_required=["knowledge_agent"],
            reason="Default to direct knowledge lookup for operational questions.",
        )

    def build_plan(self, decision: RoutingDecision) -> list[str]:
        return ["route", *[f"{name}" for name in decision.agents_required], "review"]

    def create_state(self, user_question: str) -> InvestigationState:
        decision = self.route(user_question)
        return InvestigationState(
            request_id=str(uuid.uuid4()),
            user_question=user_question,
            intent=decision.intent,
            plan=self.build_plan(decision),
            evidence=[],
            errors=[],
            review_status="PENDING",
            final_answer=None,
        )
