from __future__ import annotations

from typing import Any

from app.models.agent_models import ApprovalRequest


class MockJiraService:
    def __init__(self) -> None:
        self.tickets: dict[str, dict[str, Any]] = {}

    def create_ticket(self, approval: ApprovalRequest) -> dict[str, Any]:
        if not approval.ticket_title.strip():
            raise ValueError("Ticket title is required.")
        ticket_id = f"JIRA-{len(self.tickets) + 1:04d}"
        ticket = {
            "ticket_id": ticket_id,
            "title": approval.ticket_title,
            "description": approval.ticket_description,
            "severity": approval.priority,
            "status": "OPEN",
            "approved": True,
        }
        self.tickets[ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id: str) -> dict[str, Any]:
        return self.tickets.get(ticket_id, {})

    def search_tickets(self, term: str) -> list[dict[str, Any]]:
        if not term:
            return list(self.tickets.values())
        return [
            ticket for ticket in self.tickets.values()
            if term.lower() in ticket.get("title", "").lower() or term.lower() in ticket.get("description", "").lower()
        ]

    def add_comment(self, ticket_id: str, comment: str) -> dict[str, Any]:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        ticket.setdefault("comments", []).append(comment)
        return ticket
