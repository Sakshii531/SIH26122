from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ProjectBase(BaseModel):
    """Base fields for a Project."""

    name: str = Field(..., description="Project name", min_length=1, max_length=255)
    code: str = Field(..., description="Unique project code/identifier", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Detailed description of the project")
    location: Optional[str] = Field(None, description="Geographic or site location")


class ProjectCreate(ProjectBase):
    """Schema for creating a Project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a Project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for Project responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique project UUID")
    schedules: Optional[List[dict]] = Field(None, description="Associated project schedules")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def project_id(self) -> UUID:
        """ER diagram terminology alias for project ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)

