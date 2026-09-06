from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AuditEventType


class AuditEventBase(BaseModel):
    """Base fields for an Auditable Execution History event."""

    project_id: UUID = Field(..., description="Project UUID")
    event_type: AuditEventType = Field(..., description="Audit event category")
    entity_type: str = Field(..., description="Target entity type (e.g. FieldReport, ActivityMatch, Review)")
    entity_id: UUID = Field(..., description="Target entity UUID")
    actor_id: str = Field(..., description="Actor / User ID performing the action")
    actor_role: Optional[str] = Field(None, description="Role of the actor (e.g., SUPERVISOR, PLANNER, SYSTEM_AI)")
    description: str = Field(..., description="Human-readable audit log entry")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured snapshot / state metadata")


class AuditEventCreate(AuditEventBase):
    """Schema for creating an Audit Event."""

    pass


class AuditEventResponse(AuditEventBase):
    """Schema for Audit Event responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique audit event UUID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log timestamp")

    model_config = ConfigDict(from_attributes=True)
