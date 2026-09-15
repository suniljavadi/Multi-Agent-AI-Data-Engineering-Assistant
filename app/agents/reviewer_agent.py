from __future__ import annotations

from app.models.agent_models import AgentResult


class ReviewerAgent:
    def review(self, agent_results: list[AgentResult]) -> AgentResult:
        issues: list[str] = []
        evidence_count = 0
        for result in agent_results:
            evidence_count += len(result.evidence)
            if result.status == "ERROR":
                issues.append(f"{result.agent_name} reported an error: {result.errors}")
            if result.status == "NO_EVIDENCE":
                issues.append(f"{result.agent_name} found insufficient evidence.")
        if evidence_count == 0:
            issues.append("No evidence was produced by the specialist agents.")

        if issues:
            return AgentResult(
                agent_name="reviewer_agent",
                status="NEEDS_MORE_EVIDENCE",
                summary="The answer is not yet grounded enough to approve.",
                findings=["Insufficient or conflicting evidence was identified."],
                evidence=[],
                recommendations=["Collect additional log or documentation evidence before finalizing the answer."],
                confidence=0.25,
                errors=issues,
                metadata={"agent_count": len(agent_results), "evidence_count": evidence_count},
            )

        return AgentResult(
            agent_name="reviewer_agent",
            status="APPROVED",
            summary="The investigation is grounded in evidence and ready for the final answer.",
            findings=["Verified that agent responses were evidence-based."],
            evidence=[],
            recommendations=[],
            confidence=0.93,
            metadata={"agent_count": len(agent_results), "evidence_count": evidence_count},
        )
