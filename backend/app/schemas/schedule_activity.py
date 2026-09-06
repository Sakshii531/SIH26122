from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import ActivityLevel, ActivityStatus


class ScheduleActivityBase(BaseModel):
    """Base fields for a Baseline Schedule Activity (L5/L6)."""

    project_id: UUID = Field(..., description="Parent project UUID")
    activity_code: str = Field(..., description="Activity ID / Code from Primavera/MS Project", min_length=1)
    name: str = Field(..., description="Activity description or title", min_length=1)
    wbs_code: str = Field(..., description="Work Breakdown Structure code", min_length=1)
    wbs_path: Optional[str] = Field(None, description="Full WBS hierarchy path")
    level: ActivityLevel = Field(default=ActivityLevel.L5, description="Schedule level: L5 or L6")
    discipline: str = Field(..., description="Engineering discipline (Civil, Electrical, Piping, etc.)")
    location: Optional[str] = Field(None, description="Physical site location / section")

    planned_start_date: Optional[date] = Field(None, description="Planned start date")
    planned_finish_date: Optional[date] = Field(None, description="Planned completion date")
    actual_start_date: Optional[date] = Field(None, description="Actual start date")
    actual_finish_date: Optional[date] = Field(None, description="Actual completion date")

    status: ActivityStatus = Field(default=ActivityStatus.NOT_STARTED, description="Current activity status")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Completion percentage (0.0 - 100.0)")


class ScheduleActivityCreate(ScheduleActivityBase):
    """Schema for creating a Schedule Activity."""

    pass


class ScheduleActivityUpdate(BaseModel):
    """Schema for updating a Schedule Activity."""

    name: Optional[str] = None
    wbs_code: Optional[str] = None
    wbs_path: Optional[str] = None
    level: Optional[ActivityLevel] = None
    discipline: Optional[str] = None
    location: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_finish_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_finish_date: Optional[date] = None
    status: Optional[ActivityStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)


class ScheduleActivityResponse(ScheduleActivityBase):
    """Schema for Schedule Activity responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique activity UUID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
