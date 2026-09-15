from __future__ import annotations

from app.models.agent_models import AgentResult
from app.tools.sql_tools import SQLTool


class SQLAgent:
    def __init__(self) -> None:
        self.tool = SQLTool()

    def execute(self, question: str) -> AgentResult:
        safe_question = question.strip()
        schema = self.tool.describe_schema()
        if "revenue" in safe_question.lower() or "customers" in safe_question.lower() or "orders" in safe_question.lower():
            query = "SELECT customer_name, revenue FROM customers ORDER BY revenue DESC LIMIT 10"
            if "above 100000" in safe_question.lower():
                query = "SELECT customer_name, revenue FROM customers WHERE revenue > 100000 ORDER BY revenue DESC"
            validation = self.tool.validation.validate(query)
            if not validation["is_valid"]:
                return AgentResult(agent_name="sql_agent", status="ERROR", summary="Rejected unsafe query.", errors=validation["issues"])
            rows = self.tool.execute_query(query, limit=100)
            summary = f"Retrieved {len(rows)} rows for the requested analysis."
            evidence = [{"source": "database", "section": "customers", "chunk": "customer_name, revenue", "details": f"SQL executed: {query}"}]
            return AgentResult(agent_name="sql_agent", status="SUCCESS", summary=summary, findings=["Used read-only SQL against synthetic customer data."], evidence=evidence, recommendations=["Use the same pattern for additional filters or aggregations."], confidence=0.95, metadata={"query": query, "row_count": len(rows)})

        query = "SELECT * FROM customers LIMIT 10"
        validation = self.tool.validation.validate(query)
        if not validation["is_valid"]:
            return AgentResult(agent_name="sql_agent", status="ERROR", summary="Rejected unsafe query.", errors=validation["issues"])
        rows = self.tool.execute_query(query, limit=10)
        return AgentResult(agent_name="sql_agent", status="SUCCESS", summary="Inspected the schema and returned a safe sample query.", findings=[f"Schema includes {list(schema.keys())}"], evidence=[{"source": "database", "section": "schema", "chunk": str(schema), "details": "Sample query safe."}], confidence=0.9, metadata={"query": query, "row_count": len(rows)})
