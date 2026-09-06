from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query

from app.schemas.audit_event import AuditEventResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=List[AuditEventResponse])
async def list_audit_events(
    entity_type: Optional[str] = Query(None, description="Optional target entity_type filter (e.g. ProgressEvent)"),
    entity_id: Optional[UUID] = Query(None, description="Optional target entity_id UUID filter"),
) -> List[AuditEventResponse]:
    """List auditable execution history events with optional filters."""
    return AuditService.list_audit_events(entity_type=entity_type, entity_id=entity_id)


@router.get("/{audit_id}", response_model=AuditEventResponse)
async def get_audit_event(audit_id: UUID) -> AuditEventResponse:
    """Retrieve an audit event entry by its UUID."""
    return AuditService.get_audit_by_id(audit_id)
