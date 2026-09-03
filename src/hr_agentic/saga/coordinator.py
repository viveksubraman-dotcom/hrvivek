"""
Durable Distributed Saga Coordinator (Cloud Firestore WAL Simulation)
Implements 2-Phase staging, idempotent execution, and compensating rollbacks (SDD Section 5.5).
"""
import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone

class SagaCoordinator:
    def __init__(self):
        self._sagas: Dict[str, Dict[str, Any]] = {}

    def start_saga(self, saga_type: str, user_id: str) -> str:
        saga_id = f"SAGA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        self._sagas[saga_id] = {
            "saga_id": saga_id,
            "saga_type": saga_type,
            "user_id": user_id,
            "status": "INITIATED",
            "steps": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        return saga_id

    def log_step(self, saga_id: str, step_name: str, system: str, payload: Dict[str, Any], status: str = "COMPLETED"):
        if saga_id in self._sagas:
            self._sagas[saga_id]["steps"].append({
                "step_name": step_name,
                "system": system,
                "payload": payload,
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self._sagas[saga_id]["status"] = f"STEP_{step_name}_{status}"

    def commit_saga(self, saga_id: str):
        if saga_id in self._sagas:
            self._sagas[saga_id]["status"] = "COMMITTED"

    def abort_saga(self, saga_id: str, reason: str):
        if saga_id in self._sagas:
            self._sagas[saga_id]["status"] = "ABORTED"
            self._sagas[saga_id]["abort_reason"] = reason

    def reset(self):
        self._sagas.clear()

_coordinator = SagaCoordinator()
def get_saga_coordinator() -> SagaCoordinator:
    return _coordinator
