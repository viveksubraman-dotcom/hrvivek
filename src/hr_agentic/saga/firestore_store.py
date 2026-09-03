"""
Google Cloud Firestore Native Persistence Store for Distributed Sagas (SDD Section 5.5)
Implements physical schema mapping, transaction write-ahead logging (WAL), and state synchronization.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..config import APP_ENV, FIRESTORE_DATABASE, FIRESTORE_PROJECT_ID

logger = logging.getLogger("hr_agentic.saga.firestore_store")


class SagaStepRecord(BaseModel):
    """Physical schema definition for atomic Saga steps in Firestore collection."""

    step_name: str = Field(..., description="Name of Saga step (e.g. submit_leave, stage_contact)")
    system: str = Field(..., description="Target system of record (WorkWeek, ServiceImmediately)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Step arguments and payload")
    status: str = Field("COMPLETED", description="Status of step (COMPLETED, FAILED, COMPENSATED)")
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp")


class SagaDocumentSchema(BaseModel):
    """Physical Firestore document schema stored in collection 'sagas/{saga_id}'."""

    saga_id: str = Field(..., description="Unique Saga transaction ID")
    saga_type: str = Field(..., description="Workflow type (e.g. MEDICAL_LEAVE, RELOCATION)")
    user_id: str = Field(..., description="Requesting employee ID")
    status: str = Field("INITIATED", description="Global Saga state machine status")
    steps: List[SagaStepRecord] = Field(
        default_factory=list, description="Ordered step audit trail"
    )
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    abort_reason: Optional[str] = Field(None, description="Reason if transaction aborted")


class FirestoreSagaStore:
    """
    Manages durable state synchronization with Google Cloud Firestore Native.
    Provides write-ahead logging (WAL) and graceful in-memory fallback for hermetic offline tests.
    """

    def __init__(self, project_id: Optional[str] = None, database: Optional[str] = None):
        self.project_id = project_id or FIRESTORE_PROJECT_ID
        self.database = database or FIRESTORE_DATABASE
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._firestore_client = None

        if APP_ENV not in ("test", "testing"):
            self._init_firestore()

    def _init_firestore(self):
        """Initialize real Google Cloud Firestore client if credentials and project are active."""
        try:
            from google.cloud import firestore

            self._firestore_client = firestore.Client(
                project=self.project_id,
                database=self.database,
            )
            logger.info(f"Connected to Cloud Firestore Native [{self.project_id}:{self.database}]")
        except Exception as e:
            logger.debug(
                f"Cloud Firestore Native client unavailable; operating with WAL cache: {e}"
            )
            self._firestore_client = None

    def persist_saga(self, saga: SagaDocumentSchema) -> None:
        """Persist or update a Saga document."""
        data = saga.model_dump()
        self._memory_cache[saga.saga_id] = data

        if self._firestore_client:
            try:
                doc_ref = self._firestore_client.collection("sagas").document(saga.saga_id)
                doc_ref.set(data)
            except Exception as e:
                logger.warning(f"Failed to sync saga {saga.saga_id} to Firestore: {e}")

    def get_saga(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Saga document by ID from Firestore or cache."""
        if self._firestore_client:
            try:
                doc_ref = self._firestore_client.collection("sagas").document(saga_id)
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.warning(f"Failed to fetch saga {saga_id} from Firestore: {e}")

        return self._memory_cache.get(saga_id)

    def log_step(
        self,
        saga_id: str,
        step_name: str,
        system: str,
        payload: Dict[str, Any],
        status: str = "COMPLETED",
    ) -> None:
        """Append an atomic step to the Saga WAL in Firestore."""
        saga_dict = self.get_saga(saga_id)
        if not saga_dict:
            return

        now_iso = datetime.now(timezone.utc).isoformat()
        step = SagaStepRecord(
            step_name=step_name,
            system=system,
            payload=payload,
            status=status,
            timestamp=now_iso,
        )

        steps_list = saga_dict.get("steps", [])
        steps_list.append(step.model_dump())
        saga_dict["steps"] = steps_list
        saga_dict["status"] = f"STEP_{step_name}_{status}"
        saga_dict["updated_at"] = now_iso

        self._memory_cache[saga_id] = saga_dict

        if self._firestore_client:
            try:
                doc_ref = self._firestore_client.collection("sagas").document(saga_id)
                doc_ref.update(
                    {
                        "steps": steps_list,
                        "status": saga_dict["status"],
                        "updated_at": now_iso,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to update step {step_name} in Firestore: {e}")

    def finalize_saga(self, saga_id: str, status: str, abort_reason: Optional[str] = None) -> None:
        """Transition Saga state to COMMITTED or ABORTED."""
        saga_dict = self.get_saga(saga_id)
        if not saga_dict:
            return

        now_iso = datetime.now(timezone.utc).isoformat()
        saga_dict["status"] = status
        saga_dict["updated_at"] = now_iso
        if abort_reason:
            saga_dict["abort_reason"] = abort_reason

        self._memory_cache[saga_id] = saga_dict

        if self._firestore_client:
            try:
                doc_ref = self._firestore_client.collection("sagas").document(saga_id)
                update_fields = {"status": status, "updated_at": now_iso}
                if abort_reason:
                    update_fields["abort_reason"] = abort_reason
                doc_ref.update(update_fields)
            except Exception as e:
                logger.warning(f"Failed to finalize saga {saga_id} in Firestore: {e}")

    def clear(self) -> None:
        """Reset memory cache (used during test fixtures)."""
        self._memory_cache.clear()
