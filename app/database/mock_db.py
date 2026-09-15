from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config.settings import DATA_DIR, get_settings


class MockDatabase:
    def __init__(self, db_path: str | None = None) -> None:
        settings = get_settings()
        self.db_path = Path(db_path or settings.database_url.replace("sqlite:///./", "./"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        schema_path = Path(__file__).resolve().parents[2] / "database" / "schema.sql"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as fh:
                self.conn.executescript(fh.read())
        self._populate_seed_data()

    def _populate_seed_data(self) -> None:
        data_path = Path(__file__).resolve().parents[2] / "database" / "seed_data.json"
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            for table_name, rows in payload.items():
                if not rows:
                    continue
                columns = list(rows[0].keys())
                placeholders = ", ".join("?" for _ in columns)
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                for row in rows:
                    values = [row.get(col) for col in columns]
                    try:
                        self.conn.execute(insert_sql, values)
                    except sqlite3.IntegrityError:
                        pass
        self.conn.commit()

    def execute_read_only(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        blocked = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "MERGE",
            "EXEC",
            "CREATE",
        ]
        upper = query.upper()
        if any(token in upper for token in blocked):
            raise ValueError("Read-only query rejected: prohibited SQL statement detected.")
        cursor = self.conn.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_schema(self) -> dict[str, list[str]]:
        schema: dict[str, list[str]] = {}
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        for table in tables:
            columns = self.conn.execute(f"PRAGMA table_info('{table[0]}')").fetchall()
            schema[table[0]] = [col[1] for col in columns]
        return schema

    def close(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    db = MockDatabase()
    print(db.get_schema())
    db.close()
