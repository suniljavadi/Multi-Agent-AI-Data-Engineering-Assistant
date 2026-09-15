from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


class AnalysisTool:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[2]

    def run_python_analysis(self, csv_path: str, columns: list[str] | None = None) -> dict[str, Any]:
        data = pd.read_csv(csv_path)
        if columns:
            data = data[columns]
        summary = data.describe(include="all").to_dict()
        anomalies = []
        for col in data.select_dtypes(include=["number"]).columns:
            q1 = data[col].quantile(0.25)
            q3 = data[col].quantile(0.75)
            iqr = q3 - q1
            low = q1 - 1.5 * iqr
            high = q3 + 1.5 * iqr
            outliers = data[(data[col] < low) | (data[col] > high)]
            if not outliers.empty:
                anomalies.append({"column": col, "count": int(len(outliers)), "low": float(low), "high": float(high)})
        return {"rows": int(len(data)), "columns": list(data.columns), "summary": summary, "anomalies": anomalies}
