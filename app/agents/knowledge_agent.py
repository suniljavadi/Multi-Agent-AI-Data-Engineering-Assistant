from __future__ import annotations

from app.models.agent_models import AgentResult
from app.tools.knowledge_tools import KnowledgeTool


class KnowledgeAgent:
    def __init__(self) -> None:
        self.tool = KnowledgeTool()

    def execute(self, question: str) -> AgentResult:
        results = self.tool.search(question)
        if not results:
            return AgentResult(
                agent_name="knowledge_agent",
                status="NO_EVIDENCE",
                summary="I could not find sufficient evidence in the knowledge base.",
                findings=["Knowledge retrieval returned no matches."],
                evidence=[],
                recommendations=["Search with more specific terms or request a different source."],
                confidence=0.3,
                metadata={"query": question},
            )

        top = results[0]
        return AgentResult(
            agent_name="knowledge_agent",
            status="SUCCESS",
            summary="Retrieved relevant operational guidance from the knowledge base.",
            findings=[f"Matched {top['source']} with a relevance score of {top['score']}."],
            evidence=[{"source": top["source"], "section": top["section"], "chunk": top["chunk"], "score": top["score"]}],
            recommendations=["Use the cited policy as the starting point for operational decisions."],
            confidence=0.88,
            metadata={"query": question, "matches": len(results)},
        )
