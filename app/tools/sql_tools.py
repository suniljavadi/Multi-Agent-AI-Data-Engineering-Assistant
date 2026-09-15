from __future__ import annotations

import re
import time
from typing import Any

import sqlglot

from app.config.settings import get_settings
from app.database.mock_db import MockDatabase


class SQLValidationTool:
    def __init__(self) -> None:
        self.settings = get_settings()

    def validate(self, query: str) -> dict[str, Any]:
        issues: list[str] = []
        if not query or not query.strip():
            return {"is_valid": False, "issues": ["Query is empty"]}
        if not re.search(r"\bSELECT\b|\bWITH\b", query, flags=re.I):
            issues.append("Only SELECT or WITH queries are allowed.")
        forbidden = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "MERGE",
            "EXEC",
            "CREATE",
            "GRANT",
            "REVOKE",
        ]
        for token in forbidden:
            if re.search(rf"\b{token}\b", query, flags=re.I):
                issues.append(f"Prohibited statement detected: {token}")
        if ";" in query:
            issues.append("Multiple statements are not allowed.")
        if "--" in query or "/*" in query:
            issues.append("Comment injection patterns are not allowed.")
        return {"is_valid": not issues, "issues": issues}

    def execute_read_only(self, query: str) -> list[dict[str, Any]]:
        validation = self.validate(query)
        if not validation["is_valid"]:
            raise ValueError("SQL rejected: " + "; ".join(validation["issues"]))
        db = MockDatabase()
        try:
            return db.execute_read_only(query)
        finally:
            db.close()


class SQLTool:
    def __init__(self) -> None:
        self.validation = SQLValidationTool()

    def describe_schema(self) -> dict[str, list[str]]:
        db = MockDatabase()
        try:
            return db.get_schema()
        finally:
            db.close()

    def search_schema(self, keywords: str) -> list[str]:
        schema = self.describe_schema()
        matches: list[str] = []
        for table, columns in schema.items():
            for col in columns:
                if keywords.lower() in table.lower() or keywords.lower() in col.lower():
                    matches.append(f"{table}.{col}")
        return matches

    def analyze_sql(self, query: str) -> dict[str, Any]:
        warnings: list[str] = []
        if "SELECT *" in query.upper():
            warnings.append("SELECT * can be less efficient; specify only necessary columns.")
        if "DISTINCT" in query.upper():
            warnings.append("Unnecessary DISTINCT may indicate missing aggregation or poor filtering.")
        if "ORDER BY" in query.upper() and "WHERE" not in query.upper():
            warnings.append("Sorting without filtering may be expensive.")
        try:
            expression = sqlglot.parse_one(query)
        except Exception:
            return {"warnings": warnings, "parsed": False, "details": "Could not parse query."}
        return {"warnings": warnings, "parsed": True, "details": expression.sql()}

    def execute_query(self, query: str, limit: int | None = None) -> list[dict[str, Any]]:
        rows = self.validation.execute_read_only(query)
        if limit is not None:
            return rows[:limit]
        return rows
