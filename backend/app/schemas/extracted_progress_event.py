from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ExtractedProgressEventBase(BaseModel):
    """Base fields for an AI-extracted progress event from a field report."""

    report_id: UUID = Field(..., description="Source field report UUID")
    extracted_activity_name: Optional[str] = Field(None, description="AI-extracted activity description")
    extracted_progress_percentage: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="AI-extracted completion percentage"
    )
    extracted_status: Optional[str] = Field(None, description="AI-extracted status text")
    extracted_start_date: Optional[date] = Field(None, description="AI-extracted start date")
    extracted_finish_date: Optional[date] = Field(None, description="AI-extracted completion date")
    extracted_quantity: Optional[float] = Field(None, ge=0.0, description="AI-extracted physical quantity")
    extracted_unit: Optional[str] = Field(None, description="AI-extracted unit of measure")
    extraction_confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score (0.0 - 1.0)")
    discipline: Optional[str] = Field(None, description="Extracted or report-provided discipline")
    location: Optional[str] = Field(None, description="Extracted or report-provided location")


class ExtractedProgressEventCreate(ExtractedProgressEventBase):
    """Schema for creating an extracted progress event."""

    pass


class ExtractedProgressEventResponse(ExtractedProgressEventBase):
    """Schema for extracted progress event responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique extracted event UUID")
    matches: Optional[List[dict]] = Field(None, description="Associated AI activity matches")
    conflicts: Optional[List[dict]] = Field(None, description="Associated conflicts")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def event_id(self) -> UUID:
        """ER diagram terminology alias for event ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)

