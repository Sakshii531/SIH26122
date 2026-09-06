from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import ProgressStatus


class ProgressEventBase(BaseModel):
    """Base fields for a Validated Progress Event."""

    project_id: UUID = Field(..., description="Project UUID")
    schedule_activity_id: UUID = Field(..., description="Target schedule activity UUID")
    field_report_id: Optional[UUID] = Field(None, description="Source field report UUID (if applicable)")
    review_id: Optional[UUID] = Field(None, description="Associated planner review UUID (if validated via human review)")

    status: ProgressStatus = Field(default=ProgressStatus.IN_PROGRESS, description="Validated activity progress status")
    actual_start_date: Optional[date] = Field(None, description="Validated actual start date")
    actual_finish_date: Optional[date] = Field(None, description="Validated actual completion date")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Validated completion percentage")

    quantity_completed: Optional[float] = Field(None, ge=0.0, description="Physical quantity executed")
    unit_of_measure: Optional[str] = Field(None, description="Unit of measurement (e.g., m3, meters, tons)")
    remarks: Optional[str] = Field(None, description="Additional progress remarks")


class ProgressEventCreate(ProgressEventBase):
    """Schema for recording a Validated Progress Event."""

    pass


class ProgressEventResponse(ProgressEventBase):
    """Schema for Progress Event responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique progress event UUID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
