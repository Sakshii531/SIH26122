from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import FieldReportFormat


class EvidenceItem(BaseModel):
    """Supporting evidence item (photo, document, voice recording)."""

    id: UUID = Field(default_factory=uuid4, description="Evidence item UUID")
    file_name: str = Field(..., description="Uploaded file name")
    file_url: str = Field(..., description="Storage URL / path")
    mime_type: Optional[str] = Field(None, description="MIME content type")
    description: Optional[str] = Field(None, description="Evidence notes or context")

    model_config = ConfigDict(from_attributes=True)


class FieldReportBase(BaseModel):
    """Base fields for a Field Progress Report."""

    project_id: UUID = Field(..., description="Associated project UUID")
    source_format: FieldReportFormat = Field(..., description="Format of reported data (TEXT, VOICE, DPR, etc.)")
    reporter_id: str = Field(..., description="ID / Name of field supervisor or reporter")
    raw_content: str = Field(..., description="Raw text, transcript, or parsed content")
    discipline: Optional[str] = Field(None, description="Engineering discipline mentioned in report")
    location: Optional[str] = Field(None, description="Site location or section mentioned")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Attached evidence items")


class FieldReportCreate(FieldReportBase):
    """Schema for submitting a new Field Report."""

    pass


class FieldReportResponse(FieldReportBase):
    """Schema for Field Report responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique field report UUID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
