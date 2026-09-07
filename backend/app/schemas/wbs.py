from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class WBSBase(BaseModel):
    """Base fields for Work Breakdown Structure node."""

    schedule_id: UUID = Field(..., description="Parent schedule UUID")
    parent_wbs_id: Optional[UUID] = Field(None, description="Parent WBS node UUID (null for root nodes)")
    wbs_code: str = Field(..., description="WBS code (e.g., 1.2.3)", min_length=1)
    wbs_name: str = Field(..., description="WBS node name", min_length=1)
    level: int = Field(..., ge=1, description="WBS hierarchy level (1 = root)")
    path: Optional[str] = Field(None, description="Full hierarchy path for display")


class WBSCreate(WBSBase):
    """Schema for creating a WBS node."""

    pass


class WBSUpdate(BaseModel):
    """Schema for updating a WBS node."""

    parent_wbs_id: Optional[UUID] = None
    wbs_code: Optional[str] = Field(None, min_length=1)
    wbs_name: Optional[str] = Field(None, min_length=1)
    level: Optional[int] = Field(None, ge=1)
    path: Optional[str] = None


class WBSResponse(WBSBase):
    """Schema for WBS node responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique WBS node UUID")
    activities: Optional[List[dict]] = Field(None, description="Associated schedule activities")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def wbs_id(self) -> UUID:
        """ER diagram terminology alias for WBS ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)

