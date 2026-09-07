from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.enums import ActivityLevel, ActivityStatus


class ActivityBase(BaseModel):
    """Base fields for a Schedule Activity (L5/L6 from Primavera/MS Project)."""

    project_id: UUID = Field(..., description="Parent project UUID")
    schedule_id: UUID = Field(..., description="Parent schedule UUID")
    wbs_id: UUID = Field(..., description="Associated WBS node UUID")
    
    activity_code: str = Field(..., description="Activity ID / Code from scheduling system", min_length=1)
    name: str = Field(..., description="Activity description or title", min_length=1)
    level: ActivityLevel = Field(default=ActivityLevel.L5, description="Schedule level: L5 or L6")
    discipline: str = Field(..., description="Engineering discipline (Civil, Electrical, Piping, etc.)")
    location: Optional[str] = Field(None, description="Physical site location / section")

    planned_start_date: Optional[date] = Field(None, description="Planned start date")
    planned_finish_date: Optional[date] = Field(None, description="Planned completion date")
    actual_start_date: Optional[date] = Field(None, description="Actual start date")
    actual_finish_date: Optional[date] = Field(None, description="Actual completion date")

    status: ActivityStatus = Field(default=ActivityStatus.NOT_STARTED, description="Current activity status")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Completion percentage (0.0 - 100.0)")


class ActivityCreate(ActivityBase):
    """Schema for creating an Activity."""

    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an Activity."""

    name: Optional[str] = None
    wbs_id: Optional[UUID] = None
    level: Optional[ActivityLevel] = None
    discipline: Optional[str] = None
    location: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_finish_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_finish_date: Optional[date] = None
    status: Optional[ActivityStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)


class ActivityResponse(ActivityBase):
    """Schema for Activity responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique activity UUID")
    actual_progress_records: Optional[List[dict]] = Field(None, description="Associated actual progress records")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def activity_id(self) -> UUID:
        """ER diagram terminology alias for activity ID."""
        return self.id

    @computed_field
    @property
    def schedule_activity_id(self) -> UUID:
        """Backward compatibility alias for activity ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)



# Backward compatibility aliases
ScheduleActivityBase = ActivityBase
ScheduleActivityCreate = ActivityCreate
ScheduleActivityUpdate = ActivityUpdate
ScheduleActivityResponse = ActivityResponse
