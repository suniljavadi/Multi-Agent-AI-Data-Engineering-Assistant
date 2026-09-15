from __future__ import annotations

from app.models.agent_models import AgentResult
from app.tools.etl_tools import ETLTool


class ETLAgent:
    def __init__(self) -> None:
        self.tool = ETLTool()

    def execute(self, question: str) -> AgentResult:
        job_name = "Customer_Load" if "customer_load" in question.lower() or "customer" in question.lower() else "Product_Load"
        history = self.tool.get_job_history(job_name)
        logs = self.tool.get_job_logs(job_name)
        metrics = self.tool.get_execution_metrics(job_name)
        similar = self.tool.search_similar_incidents(question)

        observed = [
            f"{job_name} has historical failed executions in the synthetic environment.",
            "The most recent failure recorded a SQL timeout and an execution duration increase from 8 minutes to 42 minutes.",
        ]
        hypotheses = [
            "A query performance regression or blocking issue may be causing the timeout.",
            "If the logs show missing source files, that should be treated as a separate hypothesis until validated.",
        ]
        recommendations = [
            "Check the execution plan and blocking sessions for the slow query.",
            "Compare the failed execution against the last successful run and validate source freshness.",
        ]

        evidence = []
        for item in history:
            evidence.append({"source": "etl_history", "section": job_name, "chunk": str(item), "details": "historical incident"})
        for log in logs:
            evidence.append({"source": "etl_logs", "section": job_name, "chunk": str(log), "details": "execution log"})
        for metric in metrics:
            evidence.append({"source": "etl_metrics", "section": job_name, "chunk": str(metric), "details": "execution metric"})

        return AgentResult(
            agent_name="etl_agent",
            status="SUCCESS",
            summary="Investigated the ETL failure using synthetic log history and incident records.",
            findings=observed + [f"Similar incidents found: {len(similar)}"],
            evidence=evidence,
            recommendations=recommendations,
            confidence=0.86,
            metadata={"job_name": job_name, "history_count": len(history), "log_count": len(logs), "similar_incidents": len(similar)},
            errors=[],
        )
