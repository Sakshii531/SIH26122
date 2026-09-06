from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import MatchStatus


class ActivityMatchBase(BaseModel):
    """Base fields for an AI Activity Match recommendation."""

    field_report_id: UUID = Field(..., description="Source field report UUID")
    schedule_activity_id: Optional[UUID] = Field(None, description="Matched schedule activity UUID (if any)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence score between 0.0 and 1.0")
    match_status: MatchStatus = Field(default=MatchStatus.NEEDS_REVIEW, description="Match status")
    rationale: Optional[str] = Field(None, description="AI reasoning / rationale for match")
    suggested_activity_code: Optional[str] = Field(None, description="Suggested activity code")


class ActivityMatchCreate(ActivityMatchBase):
    """Schema for creating an Activity Match recommendation."""

    pass


class ActivityMatchResponse(ActivityMatchBase):
    """Schema for Activity Match responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique activity match UUID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
