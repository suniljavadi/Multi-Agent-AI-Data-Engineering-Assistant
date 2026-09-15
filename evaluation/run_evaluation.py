from __future__ import annotations

import json
from pathlib import Path

from app.agents.orchestrator import OrchestratorAgent
from app.agents.sql_agent import SQLAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.etl_agent import ETLAgent


ROOT = Path(__file__).resolve().parent


def run() -> dict[str, object]:
    orchestrator = OrchestratorAgent()
    sql_agent = SQLAgent()
    knowledge_agent = KnowledgeAgent()
    etl_agent = ETLAgent()

    with open(ROOT / "questions.json", "r", encoding="utf-8") as fh:
        questions = json.load(fh)

    report = []
    for item in questions:
        decision = orchestrator.route(item["question"])
        expected = item["expected_intent"]
        route_ok = decision.intent == expected
        report.append({
            "scenario": item["scenario"],
            "question": item["question"],
            "expected": expected,
            "actual": decision.intent,
            "route_ok": route_ok,
            "agents_required": decision.agents_required,
        })

    success = sum(1 for x in report if x["route_ok"]) / len(report)
    return {"scenarios": report, "routing_accuracy": round(success, 2), "total_scenarios": len(report)}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
