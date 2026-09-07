from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.enums import FieldReportFormat
from app.schemas.evidence import EvidenceItem, EvidenceResponse


class FieldReportBase(BaseModel):
    """Base fields for a Field Progress Report."""

    project_id: UUID = Field(..., description="Associated project UUID")
    source_format: FieldReportFormat = Field(..., description="Format of reported data (TEXT, VOICE, DPR, etc.)")
    reporter_id: str = Field(..., description="ID / Name of field supervisor or reporter")
    raw_content: str = Field(..., description="Raw text, transcript, or parsed content")
    discipline: Optional[str] = Field(None, description="Engineering discipline mentioned in report")
    location: Optional[str] = Field(None, description="Site location or section mentioned")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Attached evidence items")


class FieldReportCreate(BaseModel):
    """Schema for submitting a new Field Report."""

    project_id: Optional[UUID] = Field(None, description="Optional associated project UUID")
    source_format: FieldReportFormat = Field(default=FieldReportFormat.TEXT, description="Format of reported data")
    reporter_id: str = Field(..., description="ID / Name of field supervisor or reporter")
    raw_content: str = Field(..., description="Raw text, transcript, or parsed content")
    discipline: Optional[str] = Field(None, description="Engineering discipline mentioned in report")
    location: Optional[str] = Field(None, description="Site location or section mentioned")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Attached evidence items")


class FieldReportResponse(FieldReportBase):
    """Schema for Field Report responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique field report UUID")
    extracted_events: Optional[List[dict]] = Field(None, description="Associated extracted progress events")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def report_id(self) -> UUID:
        """ER diagram primary key alias: report_id → id."""
        return self.id

    model_config = ConfigDict(from_attributes=True)

