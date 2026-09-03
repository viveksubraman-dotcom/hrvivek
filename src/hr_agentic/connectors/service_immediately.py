"""
ServiceImmediately (ITSM/HRSD) Connector & Mock Store (FR-4.1 ~ FR-4.3)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..validation.engine import validate_ticket_transition, validate_ticket_priority

class ServiceImmediatelyConnector:
    def __init__(self):
        self._incidents: Dict[str, Dict[str, Any]] = {
            "INC0094821": {
                "ticket_id": "INC0094821",
                "requestor_id": "EMP-90210",
                "category": "IT-Network",
                "short_description": "VPN connection drops every 10 minutes",
                "priority": "3 - Moderate",
                "status": "In-Progress",
                "assignee": "Alex Chen (Network Ops)",
                "created_at": "2026-09-01T09:00:00Z",
                "comments": [
                    {"author": "System", "text": "Ticket routed to Network Tier 2", "time": "2026-09-01T09:05:00Z"},
                    {"author": "Alex Chen", "text": "Investigating Singapore Gateway logs", "time": "2026-09-01T10:15:00Z"}
                ]
            }
        }

    def get_incident(self, ticket_id: str) -> Dict[str, Any]:
        """GET /api/v1/incidents/{id}"""
        ticket = self._incidents.get(ticket_id)
        if not ticket:
            raise ValueError(f"Incident ticket '{ticket_id}' not found in ServiceImmediately.")
        return ticket

    def check_duplicate(self, requestor_id: str, category: str, window_minutes: int = 5) -> Optional[Dict[str, Any]]:
        """FR-4.3 / TC-INTG-04: Anti-duplicate ticket detection within 5-minute sliding window."""
        now = datetime.utcnow()
        for t in self._incidents.values():
            if t["requestor_id"] == requestor_id and t["category"] == category and t["status"] in ["New", "In-Progress", "Assigned"]:
                created_dt = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                if (now - created_dt) <= timedelta(minutes=window_minutes):
                    return t
        return None

    def create_incident(self, requestor_id: str, category: str, short_desc: str, priority: str = "3 - Moderate", shipping_address: Optional[str] = None) -> Dict[str, Any]:
        """POST /api/v1/incidents"""
        # 1. Anti-duplicate scan
        dup = self.check_duplicate(requestor_id, category, window_minutes=5)
        if dup:
            return {
                "status": "DUPLICATE_SUPPRESSED",
                "ticket_id": dup["ticket_id"],
                "message": f"Existing active ticket '{dup['ticket_id']}' in category '{category}' was submitted within the last 5 minutes. Appending comment instead of creating duplicate."
            }

        # 2. Priority anti-inflation guardrail
        validated_priority = validate_ticket_priority(short_desc, priority)

        ticket_num = len(self._incidents) + 55421
        ticket_id = f"INC-{ticket_num}"
        record = {
            "ticket_id": ticket_id,
            "requestor_id": requestor_id,
            "category": category,
            "short_description": short_desc,
            "priority": validated_priority,
            "status": "New",
            "assignee": "Unassigned (Auto-Triage)",
            "shipping_address": shipping_address,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "automation_source": "AI_HR_AGENT_MVP1",
            "comments": []
        }
        self._incidents[ticket_id] = record
        return record

    def add_comment(self, ticket_id: str, author_id: str, comment_text: str) -> Dict[str, Any]:
        """POST /api/v1/incidents/{id}/comments"""
        ticket = self.get_incident(ticket_id)
        comment_entry = {
            "author": author_id,
            "text": comment_text,
            "time": datetime.utcnow().isoformat() + "Z",
            "source": "AI_HR_AGENT_MVP1"
        }
        ticket["comments"].append(comment_entry)
        return {"status": "SUCCESS", "ticket_id": ticket_id, "comments_count": len(ticket["comments"])}

    def update_status(self, ticket_id: str, target_status: str, resolution_notes: Optional[str] = None) -> Dict[str, Any]:
        """PATCH /api/v1/incidents/{id}/status"""
        ticket = self.get_incident(ticket_id)
        is_valid, err_msg = validate_ticket_transition(ticket["status"], target_status)
        if not is_valid:
            raise ValueError(err_msg)

        ticket["status"] = target_status
        if resolution_notes:
            self.add_comment(ticket_id, "System", f"Status changed to {target_status}: {resolution_notes}")
        return {"status": "SUCCESS", "ticket_id": ticket_id, "new_status": target_status}

_si_client = ServiceImmediatelyConnector()
def get_service_immediately_client() -> ServiceImmediatelyConnector:
    return _si_client
