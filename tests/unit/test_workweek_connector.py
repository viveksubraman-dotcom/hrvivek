"""
Unit Test Loop: WorkWeek HCM Connector & Staged Transactions
Hermetic unit tests verifying profile operations, leave deductions, and 3-phase staging.
"""
import pytest
from hr_agentic.connectors.workweek import get_workweek_client

class TestWorkWeekProfile:
    def test_get_employee_profile_success(self):
        ww = get_workweek_client()
        prof = ww.get_employee_profile("EMP-90210")
        assert prof["employee_id"] == "EMP-90210"
        assert prof["name"] == "Jane Doe"
        assert prof["department"] == "Engineering"
        assert "Remote" in prof["work_location"]
        assert prof["home_address"] == "123 Tech Lane, Austin TX 78701"
        assert prof["phone_number"] == "+1 512 555 0199"

    def test_get_employee_profile_not_found(self):
        ww = get_workweek_client()
        with pytest.raises(ValueError, match="not found"):
            ww.get_employee_profile("EMP-NONEXISTENT")

    def test_update_contact_in_place(self):
        ww = get_workweek_client()
        res = ww.update_contact("EMP-90210", phone_number="+65 9111 2222")
        assert res["status"] == "SUCCESS"
        assert res["phone_number"] == "+65 9111 2222"
        # Verify master profile was updated
        assert ww.get_employee_profile("EMP-90210")["phone_number"] == "+65 9111 2222"

class TestWorkWeekLeaveManagement:
    def test_get_leave_balances(self):
        ww = get_workweek_client()
        balances = ww.get_leave_balances("EMP-90210")
        assert "vacation_remaining_days" in balances
        assert "sick_remaining_days" in balances
        assert balances["vacation_remaining_days"] >= 0

    def test_submit_leave_request_deduction(self):
        ww = get_workweek_client()
        init_vac = ww.get_leave_balances("EMP-90210")["vacation_remaining_days"]
        # Submit 1 business day (2026-11-04 is Wednesday)
        res = ww.submit_leave_request("EMP-90210", "Vacation", "2026-11-04", "2026-11-04")
        assert res["status"] == "SUBMITTED"
        assert res["work_days"] == 1
        new_vac = ww.get_leave_balances("EMP-90210")["vacation_remaining_days"]
        assert new_vac == init_vac - 1.0

    def test_submit_leave_request_insufficient_balance(self):
        ww = get_workweek_client()
        with pytest.raises(ValueError, match="Insufficient leave balance"):
            # Request 30 days when balance is ~15
            ww.submit_leave_request("EMP-90210", "Vacation", "2026-11-01", "2026-12-15")

class TestWorkWeek3PhaseStaging:
    def test_staging_lifecycle(self):
        ww = get_workweek_client()
        initial_address = ww.get_employee_profile("EMP-90210")["home_address"]

        # Phase 1: Stage contact update
        res = ww.stage_contact_update("EMP-90210", "10 Downing Street, London")
        assert res["status"] == "STAGED"
        staged_id = res["staged_id"]
        assert staged_id.startswith("STAGE-")
        # Master profile MUST remain untouched
        assert ww.get_employee_profile("EMP-90210")["home_address"] == initial_address

        # Phase 2: Rollback staged update (Compensating action)
        abort_res = ww.rollback_staged_update("EMP-90210", staged_id)
        assert abort_res["status"] == "ABORTED_ROLLBACK_COMPLETE"
        assert abort_res["staged_id"] == staged_id
        # Master profile still initial address
        assert ww.get_employee_profile("EMP-90210")["home_address"] == initial_address
