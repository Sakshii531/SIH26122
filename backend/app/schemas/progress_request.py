from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.enums import ProgressStatus


class ProgressFromReviewCreate(BaseModel):
    """Payload to create a validated ProgressEvent from a finalized human review."""

    review_id: UUID = Field(..., description="Finalized review item UUID (APPROVED or MODIFIED)")
    project_id: Optional[UUID] = Field(None, description="Optional project UUID override")
    schedule_activity_id: Optional[UUID] = Field(None, description="Optional schedule activity UUID override")
    status: ProgressStatus = Field(default=ProgressStatus.IN_PROGRESS, description="Validated progress status")

    actual_start_date: Optional[date] = Field(None, description="Validated actual start date")
    actual_finish_date: Optional[date] = Field(None, description="Validated actual completion date")

    quantity_completed: Optional[float] = Field(None, ge=0.0, description="Physical quantity executed")
    unit_of_measure: Optional[str] = Field(None, description="Unit of measurement (e.g. m3, meters)")
    remarks: Optional[str] = Field(None, description="Additional progress remarks")
