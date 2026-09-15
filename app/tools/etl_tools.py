from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config.settings import ROOT_DIR


class ETLTool:
    def __init__(self) -> None:
        incidents_dir = ROOT_DIR / "synthetic_data" / "incidents"
        logs_dir = ROOT_DIR / "synthetic_data" / "logs"
        self.incidents_dir = incidents_dir
        self.logs_dir = logs_dir

    def _read_json(self, file_name: str) -> list[dict[str, Any]]:
        path = self.incidents_dir / file_name
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_job_history(self, job_name: str) -> list[dict[str, Any]]:
        incidents = self._read_json("incidents.json")
        return [item for item in incidents if item.get("job_name") == job_name]

    def get_job_logs(self, job_name: str) -> list[dict[str, Any]]:
        logs_path = self.logs_dir / "etl_logs.json"
        if not logs_path.exists():
            return []
        with open(logs_path, "r", encoding="utf-8") as file:
            logs = json.load(file)
        return [item for item in logs if item.get("job_name") == job_name]

    def get_execution_metrics(self, job_name: str) -> list[dict[str, Any]]:
        metrics_path = self.logs_dir / "execution_metrics.json"
        if not metrics_path.exists():
            return []
        with open(metrics_path, "r", encoding="utf-8") as file:
            metrics = json.load(file)
        return [item for item in metrics if item.get("job_name") == job_name]

    def search_similar_incidents(self, description: str) -> list[dict[str, Any]]:
        incidents = self._read_json("incidents.json")
        results: list[dict[str, Any]] = []
        q = description.lower()
        for incident in incidents:
            text = " ".join([
                incident.get("job_name", ""),
                incident.get("error_type", ""),
                incident.get("root_cause", ""),
                incident.get("resolution", "")
            ]).lower()
            if q in text:
                results.append(incident)
        return results

    def get_job_metadata(self, job_name: str) -> dict[str, Any]:
        return {"job_name": job_name, "status": "synthetic-demo", "owner": "data-engineering"}
