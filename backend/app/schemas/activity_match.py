from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.schemas.enums import MatchStatus


class ActivityMatchBase(BaseModel):
    """Base fields for an AI Activity Match recommendation."""

    event_id: UUID = Field(..., description="Source extracted progress event UUID")
    report_id: UUID = Field(..., description="Source field report UUID")
    field_report_id: UUID = Field(..., description="Source field report UUID (alias)")
    activity_id: Optional[UUID] = Field(None, description="Matched activity UUID (if any)")
    schedule_activity_id: Optional[UUID] = Field(None, description="Matched activity UUID (alias)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence score between 0.0 and 1.0")
    match_status: MatchStatus = Field(default=MatchStatus.NEEDS_REVIEW, description="Match status")
    rationale: Optional[str] = Field(None, description="AI reasoning / rationale for match")
    suggested_activity_code: Optional[str] = Field(None, description="Suggested activity code")

    @model_validator(mode="before")
    @classmethod
    def sync_id_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            rep_id = data.get("report_id") or data.get("field_report_id")
            if rep_id:
                data["report_id"] = rep_id
                data["field_report_id"] = rep_id
            act_id = data.get("activity_id") or data.get("schedule_activity_id")
            if act_id:
                data["activity_id"] = act_id
                data["schedule_activity_id"] = act_id
        return data


class ActivityMatchCreate(ActivityMatchBase):
    """Schema for creating an Activity Match recommendation."""

    pass


class ActivityMatchResponse(ActivityMatchBase):
    """Schema for Activity Match responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique activity match UUID")
    reviews: Optional[List[dict]] = Field(None, description="Associated planner reviews")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def match_id(self) -> UUID:
        """ER diagram terminology alias for match ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)
