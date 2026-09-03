"""
Unit Test Loop: Distributed Saga Coordinator & Compensating Workflows
Hermetic unit tests verifying Saga write-ahead logging (WAL), state transitions, and compensation.
"""

from hr_agentic.saga.coordinator import get_saga_coordinator
from hr_agentic.saga.workflows import (
    execute_equipment_procurement_saga,
    execute_medical_leave_saga,
    execute_relocation_saga,
)


class TestSagaCoordinatorCore:
    def test_saga_lifecycle_success(self):
        coord = get_saga_coordinator()
        saga_id = coord.start_saga("TEST_WORKFLOW", "EMP-90210")
        assert saga_id.startswith("SAGA-")
        assert coord._sagas[saga_id]["status"] == "INITIATED"

        # Record step 1
        coord.log_step(saga_id, "STEP_1", "WorkWeek", {"status": "SUCCESS"})
        assert len(coord._sagas[saga_id]["steps"]) == 1

        # Commit saga
        coord.commit_saga(saga_id)
        assert coord._sagas[saga_id]["status"] == "COMMITTED"

    def test_saga_abort_lifecycle(self):
        coord = get_saga_coordinator()
        saga_id = coord.start_saga("TEST_ABORT_WORKFLOW", "EMP-90210")
        coord.log_step(saga_id, "STEP_1", "ServiceImmediately", {"status": "PENDING"})
        coord.abort_saga(saga_id, "Simulated network timeout")
        assert coord._sagas[saga_id]["status"] == "ABORTED"
        assert coord._sagas[saga_id]["abort_reason"] == "Simulated network timeout"


class TestSagaWorkflows:
    def test_equipment_procurement_saga_remote_worker(self):
        res = execute_equipment_procurement_saga("EMP-90210")
        assert res["status"] == "SUCCESS"
        assert res["ticket_id"].startswith("INC")
        assert "Section 1.3" in res["policy_citation"]

    def test_medical_leave_saga_success(self):
        res = execute_medical_leave_saga("EMP-90210", start_date="2026-09-07", days=5)
        assert res["status"] == "SUCCESS"
        assert res["leave_request_id"].startswith("LR-")
        assert res["ticket_id"].startswith("INC")
        assert res["manager"] == "Sarah Jenkins"

    def test_relocation_saga_success(self):
        res = execute_relocation_saga("EMP-90210")
        assert res["status"] == "SUCCESS"
        assert res["allowance_gbp"] == 5000.0
        assert res["staged_id"].startswith("STAGE-")
        assert res["ticket_id"].startswith("INC")

    def test_relocation_saga_compensating_rollback(self):
        res = execute_relocation_saga("EMP-90210", simulate_step3_failure=True)
        assert res["status"] == "COMPENSATED_ROLLBACK"
        assert "safely rolled back" in res["message"]
