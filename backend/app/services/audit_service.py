from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException

from app.repositories.factory import get_audit_log_repository
from app.schemas.audit_event import AuditEventCreate, AuditEventResponse


class AuditService:
    """Service managing auditable execution history via repository layer."""

    @classmethod
    def record_audit_event(cls, event: AuditEventCreate) -> AuditEventResponse:
        """Record an auditable execution history event."""
        repo = get_audit_log_repository()
        return repo.create(event)

    @classmethod
    def get_audit_by_id(cls, audit_id: UUID) -> AuditEventResponse:
        """Retrieve an audit event by its UUID."""
        repo = get_audit_log_repository()
        item = repo.get_by_id(audit_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Audit event '{audit_id}' not found.",
            )
        return item

    @classmethod
    def list_audit_events(
        cls,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
    ) -> List[AuditEventResponse]:
        """List audit events with optional entity_type and entity_id filters."""
        repo = get_audit_log_repository()
        return repo.list_all(entity_type=entity_type, entity_id=entity_id)

    @classmethod
    def clear_db(cls) -> None:
        """Reset repository store for testing isolation."""
        repo = get_audit_log_repository()
        try:
            repo.clear()
        except NotImplementedError:
            pass
