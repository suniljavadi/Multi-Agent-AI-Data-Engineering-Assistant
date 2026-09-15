from __future__ import annotations

from collections import defaultdict
from typing import Any


class AuditTrail:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def record(self, **payload: Any) -> None:
        self.events.append(payload)

    def summary(self) -> dict[str, int]:
        summary = defaultdict(int)
        for event in self.events:
            summary[event.get("status", "unknown")] += 1
        return dict(summary)
