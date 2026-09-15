from __future__ import annotations

from app.agents.orchestrator import OrchestratorAgent
from app.workflows.investigation_workflow import InvestigationWorkflow


SCENARIOS = [
    "Show the top 10 customers by revenue.",
    "What is the rollback procedure?",
    "Why did Customer_Load fail?",
    "Investigate why Customer_Load failed and check whether our documentation has a recommended solution.",
    "Optimize this query: SELECT * FROM customers ORDER BY revenue DESC;",
    "Create a ticket for this confirmed incident.",
]


def main() -> None:
    wf = InvestigationWorkflow()
    orchestrator = OrchestratorAgent()
    for question in SCENARIOS:
        decision = orchestrator.route(question)
        print(f"Question: {question}\nIntent: {decision.intent}\nAgents: {decision.agents_required}\n")
        response = wf.run(question)
        print(response["state"].final_answer)
        print("-" * 80)


if __name__ == "__main__":
    main()
