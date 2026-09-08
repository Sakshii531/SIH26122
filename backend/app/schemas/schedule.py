from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ScheduleBase(BaseModel):
    """Base fields for a Project Schedule (Baseline from Primavera/MS Project)."""

    project_id: UUID = Field(..., description="Parent project UUID")
    name: str = Field(..., description="Schedule name/title", min_length=1)
    version: str = Field(..., description="Schedule version/revision identifier")
    baseline_date: Optional[datetime] = Field(None, description="Baseline approval date")
    description: Optional[str] = Field(None, description="Schedule description or notes")
    source_file: Optional[str] = Field(None, description="Original import file name")


class ScheduleCreate(ScheduleBase):
    """Schema for creating a new Schedule."""

    pass


class ScheduleUpdate(BaseModel):
    """Schema for updating a Schedule."""

    name: Optional[str] = Field(None, min_length=1)
    version: Optional[str] = None
    baseline_date: Optional[datetime] = None
    description: Optional[str] = None
    source_file: Optional[str] = None


class ScheduleResponse(ScheduleBase):
    """Schema for Schedule responses."""

    version: Optional[str] = Field(None, description="Optional schedule version when supplied by the source system")
    id: UUID = Field(default_factory=uuid4, description="Unique schedule UUID")
    wbs_nodes: Optional[List[dict]] = Field(None, description="Associated WBS nodes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def schedule_id(self) -> UUID:
        """ER diagram terminology alias for schedule ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)

