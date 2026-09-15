from __future__ import annotations

from app.agents.etl_agent import ETLAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.sql_agent import SQLAgent
from app.models.agent_models import AgentResult, InvestigationState


class InvestigationWorkflow:
    def __init__(self) -> None:
        self.orchestrator = OrchestratorAgent()
        self.sql_agent = SQLAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.etl_agent = ETLAgent()
        self.reviewer = ReviewerAgent()

    def run(self, question: str) -> dict[str, object]:
        state = self.orchestrator.create_state(question)
        decision = self.orchestrator.route(question)
        state.intent = decision.intent
        state.plan = self.orchestrator.build_plan(decision)

        results: list[AgentResult] = []
        for agent_name in decision.agents_required:
            if agent_name == "sql_agent":
                result = self.sql_agent.execute(question)
                results.append(result)
            elif agent_name == "knowledge_agent":
                result = self.knowledge_agent.execute(question)
                results.append(result)
            elif agent_name == "etl_agent":
                result = self.etl_agent.execute(question)
                results.append(result)

        review = self.reviewer.review(results)
        results.append(review)
        state.agent_results = [item.model_dump() for item in results]
        state.review_status = review.status
        state.final_answer = self._compose_final_answer(question, results)
        return {"state": state, "results": results}

    def _compose_final_answer(self, question: str, results: list[AgentResult]) -> str:
        evidence_parts = []
        for result in results:
            if result.evidence:
                for item in result.evidence[:2]:
                    evidence_parts.append(f"{result.agent_name}: {item.get('details', 'evidence')}")
        if not evidence_parts:
            return "I could not find sufficient evidence in the knowledge base or operational logs."
        return "\n".join([
            f"Question: {question}",
            "Findings:",
            *[f"- {result.summary}" for result in results],
            "Evidence:",
            *[f"- {p}" for p in evidence_parts],
        ])
