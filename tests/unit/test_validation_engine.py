"""
Unit Test Loop: Deterministic Validation Engine (WAF Operational Excellence)
Hermetic unit tests verifying mathematical, temporal, and lifecycle constraints.
"""
import pytest
from hr_agentic.validation.engine import (
    calculate_working_days,
    validate_leave_request,
    validate_phone_e164,
    validate_ticket_transition,
    validate_ticket_priority
)

class TestWorkingDaysCalculation:
    def test_standard_work_week(self):
        # Mon (2026-09-07) to Fri (2026-09-11) = 5 days
        assert calculate_working_days("2026-09-07", "2026-09-11") == 5

    def test_weekend_crossing(self):
        # Fri (2026-09-11) to Mon (2026-09-14) = 2 days (Fri, Mon)
        assert calculate_working_days("2026-09-11", "2026-09-14") == 2

    def test_single_business_day(self):
        # Wed (2026-09-09) to Wed (2026-09-09) = 1 day
        assert calculate_working_days("2026-09-09", "2026-09-09") == 1

    def test_weekend_only_range(self):
        # Sat (2026-09-12) to Sun (2026-09-13) = 0 days
        assert calculate_working_days("2026-09-12", "2026-09-13") == 0

    def test_invalid_date_chronology(self):
        with pytest.raises(ValueError, match="Temporal validity violation"):
            calculate_working_days("2026-09-15", "2026-09-10")

class TestLeaveRequestValidation:
    def test_valid_leave_request(self):
        valid, err, days = validate_leave_request("2026-09-07", "2026-09-09", available_days=15.0)
        assert valid is True
        assert err is None
        assert days == 3

    def test_insufficient_leave_balance(self):
        valid, err, days = validate_leave_request("2026-09-07", "2026-09-11", available_days=2.0)
        assert valid is False
        assert "Insufficient leave balance" in err
        assert days == 5

    def test_invalid_date_chronology_leave(self):
        valid, err, days = validate_leave_request("2026-09-20", "2026-09-15", available_days=10.0)
        assert valid is False
        assert "Invalid date range" in err
        assert days == 0

    def test_malformed_date_string(self):
        valid, err, days = validate_leave_request("not-a-date", "2026-09-15", available_days=10.0)
        assert valid is False
        assert "Invalid date format" in err
        assert days == 0

class TestPhoneValidation:
    def test_valid_singapore_phone(self):
        assert validate_phone_e164("+65 9123 4567") is True
        assert validate_phone_e164("+6591234567") is True

    def test_valid_us_phone(self):
        assert validate_phone_e164("+1 (415) 555-2671") is True

    def test_invalid_phone_formats(self):
        assert validate_phone_e164("INVALID_PHONE_123") is False
        assert validate_phone_e164("phone-number") is False
        assert validate_phone_e164("") is False

class TestTicketLifecycleTransition:
    def test_valid_transitions(self):
        assert validate_ticket_transition("New", "In-Progress")[0] is True
        assert validate_ticket_transition("In-Progress", "Resolved")[0] is True
        assert validate_ticket_transition("Resolved", "Closed")[0] is True

    def test_illegal_direct_jumps(self):
        valid, err = validate_ticket_transition("New", "Closed")
        assert valid is False
        assert "Illegal lifecycle transition" in err

    def test_terminal_state_transitions(self):
        valid, err = validate_ticket_transition("Closed", "In-Progress")
        assert valid is False
        assert "Illegal lifecycle transition" in err

class TestPriorityAntiInflation:
    def test_downgrade_trivial_incident(self):
        assert validate_ticket_priority("The coffee machine is leaking", "1 - Critical") == "4 - Low"
        assert validate_ticket_priority("Replace my mouse pad", "2 - High") == "4 - Low"

    def test_preserve_legitimate_critical_incident(self):
        assert validate_ticket_priority("Production VPN gateway authentication failure", "1 - Critical") == "1 - Critical"
        assert validate_ticket_priority("Payroll database connection timed out", "2 - High") == "2 - High"
