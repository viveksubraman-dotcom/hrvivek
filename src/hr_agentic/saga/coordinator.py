"""
Durable Distributed Saga Coordinator (Cloud Firestore Native State Synchronization)
Implements physical schema mapping, 2-Phase staging, idempotent execution,
and compensating rollbacks (SDD Section 5.5).
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .firestore_store import FirestoreSagaStore, SagaDocumentSchema


class SagaCoordinator:
    def __init__(self, store: Optional[FirestoreSagaStore] = None):
        self.store = store or FirestoreSagaStore()

    def start_saga(self, saga_type: str, user_id: str) -> str:
        saga_id = f"SAGA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        saga_doc = SagaDocumentSchema(
            saga_id=saga_id,
            saga_type=saga_type,
            user_id=user_id,
            status="INITIATED",
            steps=[],
            created_at=now_iso,
            updated_at=now_iso,
        )
        self.store.persist_saga(saga_doc)
        return saga_id

    def log_step(
        self,
        saga_id: str,
        step_name: str,
        system: str,
        payload: Dict[str, Any],
        status: str = "COMPLETED",
    ):
        self.store.log_step(
            saga_id=saga_id,
            step_name=step_name,
            system=system,
            payload=payload,
            status=status,
        )

    def commit_saga(self, saga_id: str):
        self.store.finalize_saga(saga_id, status="COMMITTED")

    def abort_saga(self, saga_id: str, reason: str):
        self.store.finalize_saga(saga_id, status="ABORTED", abort_reason=reason)

    def get_saga(self, saga_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_saga(saga_id)

    def reset(self):
        self.store.clear()

    @property
    def _sagas(self) -> Dict[str, Any]:
        return self.store._memory_cache


_coordinator = SagaCoordinator()


def get_saga_coordinator() -> SagaCoordinator:
    return _coordinator
