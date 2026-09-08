from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.schemas.enums import AuditEventType


class AuditLogBase(BaseModel):
    """Base fields for an Audit Log entry."""

    project_id: UUID = Field(..., description="Project UUID")
    event_type: AuditEventType = Field(..., description="Audit event category")
    entity_type: str = Field(..., description="Target entity type (e.g. FieldReport, ActivityMatch, PlannerReview)")
    entity_id: UUID = Field(..., description="Target entity UUID")
    actor_id: Optional[str] = Field(None, description="Actor / User ID performing the action")
    user_id: Optional[str] = Field(None, description="Actor / User ID performing the action (alias)")
    actor_role: Optional[str] = Field(None, description="Role of the actor (e.g., SUPERVISOR, PLANNER, SYSTEM_AI)")
    description: str = Field(..., description="Human-readable audit log entry")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured snapshot / state metadata")

    @model_validator(mode="before")
    @classmethod
    def sync_id_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            u_id = data.get("actor_id") or data.get("user_id")
            if u_id:
                data["actor_id"] = u_id
                data["user_id"] = u_id
        return data

    @model_validator(mode="after")
    def ensure_user_id(self) -> AuditLogBase:
        if not self.actor_id and self.user_id:
            self.actor_id = self.user_id
        elif not self.user_id and self.actor_id:
            self.user_id = self.actor_id
        return self


class AuditLogCreate(AuditLogBase):
    """Schema for creating an Audit Log entry."""

    pass


class AuditLogResponse(AuditLogBase):
    """Schema for Audit Log responses."""

    project_id: Optional[UUID] = Field(None, description="Project UUID when supplied by the source system")
    id: UUID = Field(default_factory=uuid4, description="Unique audit log UUID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log timestamp")

    @computed_field
    @property
    def audit_id(self) -> UUID:
        """ER diagram terminology alias for audit ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)


# Backward compatibility aliases
AuditEventBase = AuditLogBase
AuditEventCreate = AuditLogCreate
AuditEventResponse = AuditLogResponse
