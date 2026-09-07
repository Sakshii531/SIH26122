from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class EvidenceBase(BaseModel):
    """Base fields for an Evidence entity supporting field reports."""

    report_id: Optional[UUID] = Field(None, description="Associated field report UUID")
    file_name: str = Field(..., description="Uploaded file name")
    file_url: str = Field(..., description="Storage URL / path")
    mime_type: Optional[str] = Field(None, description="MIME content type")
    description: Optional[str] = Field(None, description="Evidence notes or context")


class EvidenceCreate(EvidenceBase):
    """Schema for creating an Evidence item."""

    pass


class EvidenceResponse(EvidenceBase):
    """Schema for Evidence item responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique evidence item UUID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def evidence_id(self) -> UUID:
        """ER diagram terminology alias for evidence ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)


# Backward compatibility alias
EvidenceItem = EvidenceResponse
