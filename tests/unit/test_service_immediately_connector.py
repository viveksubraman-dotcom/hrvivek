"""
Unit Test Loop: ServiceImmediately ITSM Connector
Hermetic unit tests verifying incident creation, comments, lifecycle transitions, deduplication, and priority anti-inflation.
"""

import pytest

from hr_agentic.connectors.service_immediately import get_service_immediately_client


class TestIncidentManagement:
    def test_create_incident_success(self):
        si = get_service_immediately_client()
        inc = si.create_incident(
            requestor_id="EMP-90210",
            category="IT Support",
            short_desc="External display power flickers intermittently",
            priority="3 - Moderate",
        )
        assert inc["ticket_id"].startswith("INC-")
        assert inc["status"] == "New"
        assert inc["priority"] == "3 - Moderate"
        assert inc["requestor_id"] == "EMP-90210"

    def test_get_incident_found(self):
        si = get_service_immediately_client()
        inc = si.get_incident("INC0094821")
        assert inc["ticket_id"] == "INC0094821"
        assert inc["category"] == "IT-Network"

    def test_get_incident_not_found(self):
        si = get_service_immediately_client()
        with pytest.raises(ValueError, match="not found"):
            si.get_incident("INC-DOES-NOT-EXIST")

    def test_add_comment_to_incident(self):
        si = get_service_immediately_client()
        res = si.add_comment("INC0094821", "EMP-90210", "Technician dispatched to desk 4A.")
        assert res["status"] == "SUCCESS"
        inc = si.get_incident("INC0094821")
        comments = [c["text"] for c in inc["comments"]]
        assert "Technician dispatched to desk 4A." in comments

    def test_lifecycle_transition_valid(self):
        si = get_service_immediately_client()
        res = si.update_status("INC0094821", "Resolved", resolution_notes="Firmware patched.")
        assert res["status"] == "SUCCESS"
        assert res["new_status"] == "Resolved"

    def test_lifecycle_transition_invalid_jump(self):
        si = get_service_immediately_client()
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            # New incident cannot jump to Closed
            new_inc = si.create_incident(
                "EMP-90210", "IT-Audio", "Testing invalid jump", "3 - Moderate"
            )
            si.update_status(new_inc["ticket_id"], "Closed")


class TestServiceImmediatelyGuardrails:
    def test_anti_duplicate_suppression_5min(self):
        si = get_service_immediately_client()
        unique_desc = "Testing anti-duplicate 5-minute detection window"
        # First creation succeeds
        inc1 = si.create_incident("EMP-90210", "IT-Facilities", unique_desc, "3 - Moderate")
        assert inc1["ticket_id"] is not None

        # Immediate second creation with same caller & desc is suppressed
        inc2 = si.create_incident("EMP-90210", "IT-Facilities", unique_desc, "3 - Moderate")
        assert inc2["status"] == "DUPLICATE_SUPPRESSED"
        assert inc2["ticket_id"] == inc1["ticket_id"]

    def test_priority_anti_inflation_auto_downgrade(self):
        si = get_service_immediately_client()
        inc = si.create_incident(
            "EMP-90210", "Facilities", "The coffee machine needs fresh beans", "1 - Critical"
        )
        assert inc["priority"] == "4 - Low"
