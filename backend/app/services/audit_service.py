from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.schemas.audit_event import AuditEventCreate, AuditEventResponse


class AuditService:
    """In-memory service managing auditable execution history."""

    _audit_db: Dict[UUID, AuditEventResponse] = {}

    @classmethod
    def record_audit_event(cls, event: AuditEventCreate) -> AuditEventResponse:
        """Record an auditable execution history event."""
        audit_id = uuid4()
        now = datetime.utcnow()

        audit_response = AuditEventResponse(
            id=audit_id,
            project_id=event.project_id,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            actor_id=event.actor_id,
            actor_role=event.actor_role,
            description=event.description,
            payload=event.payload,
            timestamp=now,
        )

        cls._audit_db[audit_id] = audit_response
        return audit_response

    @classmethod
    def get_audit_by_id(cls, audit_id: UUID) -> AuditEventResponse:
        """Retrieve an audit event by its UUID."""
        if audit_id not in cls._audit_db:
            raise HTTPException(
                status_code=404,
                detail=f"Audit event '{audit_id}' not found.",
            )
        return cls._audit_db[audit_id]

    @classmethod
    def list_audit_events(
        cls,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
    ) -> List[AuditEventResponse]:
        """List audit events with optional entity_type and entity_id filters."""
        items = list(cls._audit_db.values())

        if entity_type is not None:
            items = [item for item in items if item.entity_type.lower() == entity_type.lower()]
        if entity_id is not None:
            items = [item for item in items if item.entity_id == entity_id]

        return items

    @classmethod
    def clear_db(cls) -> None:
        """Reset in-memory audit store for testing isolation."""
        cls._audit_db.clear()
