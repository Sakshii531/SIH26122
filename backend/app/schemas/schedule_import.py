from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schedule_activity import ScheduleActivityResponse


class ScheduleRowValidationError(BaseModel):
    """Details for a single row failing schedule activity validation."""

    row_number: int = Field(..., description="1-based index of row in uploaded file")
    activity_code: Optional[str] = Field(None, description="Activity code if parsed from row")
    errors: List[str] = Field(..., description="List of validation error messages")


class ScheduleImportSummaryResponse(BaseModel):
    """Summary output for schedule import endpoint."""

    total_rows: int = Field(..., description="Total rows parsed from file")
    valid_count: int = Field(..., description="Count of successfully validated activities")
    rejected_count: int = Field(..., description="Count of rejected rows due to validation errors")
    activities: List[ScheduleActivityResponse] = Field(default_factory=list, description="Validated schedule activity objects")
    validation_errors: List[ScheduleRowValidationError] = Field(default_factory=list, description="List of row validation failures")
