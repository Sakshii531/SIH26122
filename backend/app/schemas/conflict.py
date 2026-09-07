from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ConflictBase(BaseModel):
    """Base fields for a detected conflict between extracted progress events."""

    event_id: UUID = Field(..., description="Primary extracted progress event UUID")
    conflicting_event_id: UUID = Field(..., description="Conflicting extracted progress event UUID")
    conflict_type: str = Field(
        ...,
        description="Type of conflict (e.g., 'DUPLICATE_ACTIVITY', 'OVERLAPPING_DATES', 'CONTRADICTORY_STATUS')",
    )
    severity: str = Field(
        default="MEDIUM", description="Conflict severity: LOW, MEDIUM, HIGH, CRITICAL"
    )
    description: str = Field(..., description="Human-readable conflict description")
    resolution_status: str = Field(
        default="PENDING", description="Resolution status: PENDING, RESOLVED, IGNORED"
    )
    resolved_by: Optional[str] = Field(None, description="User ID who resolved the conflict")
    resolution_notes: Optional[str] = Field(None, description="Resolution explanation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional conflict context")


class ConflictCreate(ConflictBase):
    """Schema for creating a conflict record."""

    pass


class ConflictUpdate(BaseModel):
    """Schema for updating a conflict record."""

    resolution_status: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConflictResponse(ConflictBase):
    """Schema for conflict responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique conflict UUID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def conflict_id(self) -> UUID:
        """ER diagram terminology alias for conflict ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)

