"""
Progress Event Extraction Schema Module for SIH26122.

Defines Pydantic models and Enums representing progress events extracted by AI
from raw, unstructured field reports.
"""

import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ExtractionStatus(str, Enum):
    """Extraction quality and review status for an extracted progress event."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    AMBIGUOUS = "ambiguous"
    NEEDS_REVIEW = "needs_review"


class EventDiscipline(str, Enum):
    """Engineering and construction disciplines."""
    CIVIL = "Civil"
    STRUCTURAL = "Structural"
    PIPING = "Piping"
    MECHANICAL = "Mechanical"
    ELECTRICAL = "Electrical"
    INSTRUMENTATION = "Instrumentation"


class EventStatus(str, Enum):
    """Schedule execution status."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ExtractedProgressEvent(BaseModel):
    """
    Pydantic schema representing structured progress event information extracted
    from unstructured field report text.
    """
    report_id: str = Field(
        ...,
        description="ID of the source field report (e.g., REP-001)"
    )
    activity_description: str = Field(
        ...,
        description="Natural language summary or description of the work activity performed"
    )
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.COMPLETE,
        description="Status indicating whether extraction is complete, partial, ambiguous, or needs human review"
    )
    discipline: Optional[str] = Field(
        default=None,
        description="Engineering discipline (e.g., Civil, Structural, Piping, Mechanical, Electrical, Instrumentation)"
    )
    status: Optional[str] = Field(
        default=None,
        description="Extracted progress status (Not Started, In Progress, Completed)"
    )
    actual_start: Optional[datetime.date] = Field(
        default=None,
        description="Extracted actual start date"
    )
    actual_finish: Optional[datetime.date] = Field(
        default=None,
        description="Extracted actual finish date"
    )
    location: Optional[str] = Field(
        default=None,
        description="Physical site location, area, or grid reference extracted from report"
    )
    progress_value: Optional[float] = Field(
        default=None,
        description="Extracted progress percentage (0.0 to 100.0)"
    )
    extracted_text: Optional[str] = Field(
        default=None,
        description="Exact text quote or snippet extracted from the raw report text"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional optional extraction metadata"
    )

    @field_validator("progress_value")
    @classmethod
    def validate_progress_value(cls, v: Optional[float]) -> Optional[float]:
        """Validate progress percentage is between 0.0 and 100.0 inclusive."""
        if v is not None:
            if v < 0.0 or v > 100.0:
                raise ValueError(f"progress_value must be between 0.0 and 100.0 (got {v})")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "ExtractedProgressEvent":
        """Validate actual_start <= actual_finish when both dates are present."""
        if self.actual_start and self.actual_finish:
            if self.actual_start > self.actual_finish:
                raise ValueError(
                    f"actual_start ({self.actual_start}) cannot be after actual_finish ({self.actual_finish})"
                )
        return self
