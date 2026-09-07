from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.schemas.enums import ProgressStatus


class ActualProgressBase(BaseModel):
    """Base fields for validated actual progress on an activity."""

    activity_id: Optional[UUID] = Field(None, description="Target schedule activity UUID")
    schedule_activity_id: Optional[UUID] = Field(None, description="Target schedule activity UUID (alias)")
    project_id: UUID = Field(..., description="Project UUID")
    report_id: Optional[UUID] = Field(None, description="Source field report UUID (if applicable)")
    field_report_id: Optional[UUID] = Field(None, description="Source field report UUID (alias)")
    review_id: Optional[UUID] = Field(None, description="Associated planner review UUID (if validated via review)")

    status: ProgressStatus = Field(default=ProgressStatus.IN_PROGRESS, description="Validated progress status")
    actual_start_date: Optional[date] = Field(None, description="Validated actual start date")
    actual_finish_date: Optional[date] = Field(None, description="Validated actual completion date")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Validated completion percentage")

    quantity_completed: Optional[float] = Field(None, ge=0.0, description="Physical quantity executed")
    unit_of_measure: Optional[str] = Field(None, description="Unit of measurement (e.g., m3, meters, tons)")
    remarks: Optional[str] = Field(None, description="Additional progress remarks")
    validated_by: Optional[str] = Field(None, description="Planner/user ID who validated this progress")

    @model_validator(mode="before")
    @classmethod
    def sync_id_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            act_id = data.get("activity_id") or data.get("schedule_activity_id")
            if act_id:
                data["activity_id"] = act_id
                data["schedule_activity_id"] = act_id
            rep_id = data.get("report_id") or data.get("field_report_id")
            if rep_id is not None:
                data["report_id"] = rep_id
                data["field_report_id"] = rep_id
        return data

    @model_validator(mode="after")
    def ensure_required_ids(self) -> ActualProgressBase:
        if not self.activity_id and self.schedule_activity_id:
            self.activity_id = self.schedule_activity_id
        elif not self.schedule_activity_id and self.activity_id:
            self.schedule_activity_id = self.activity_id
        if not self.report_id and self.field_report_id:
            self.report_id = self.field_report_id
        elif not self.field_report_id and self.report_id:
            self.field_report_id = self.report_id
        return self


class ActualProgressCreate(ActualProgressBase):
    """Schema for recording validated actual progress."""

    pass


class ActualProgressResponse(ActualProgressBase):
    """Schema for actual progress responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique actual progress UUID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Record timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def progress_id(self) -> UUID:
        """ER diagram terminology alias for progress ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)
