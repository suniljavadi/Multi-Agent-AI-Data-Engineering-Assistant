from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config.settings import ROOT_DIR


class KnowledgeTool:
    def __init__(self) -> None:
        self.docs_dir = ROOT_DIR / "synthetic_data" / "documents"

    def search(self, query: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        if not query:
            return results
        for path in sorted(self.docs_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            lowered = content.lower()
            q = query.lower()
            if q in lowered:
                results.append({
                    "source": path.name,
                    "section": "main",
                    "chunk": content[:500],
                    "score": 0.9,
                    "content": content,
                })
        if not results:
            for path in sorted(self.docs_dir.glob("*.md")):
                content = path.read_text(encoding="utf-8")
                tokens = set(query.lower().split())
                words = set(content.lower().split())
                score = len(tokens & words) / max(1, len(tokens))
                if score > 0:
                    results.append({
                        "source": path.name,
                        "section": "main",
                        "chunk": content[:500],
                        "score": round(score, 2),
                        "content": content,
                    })
        return sorted(results, key=lambda item: item.get("score", 0), reverse=True)[:5]

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        return self.search(query)
