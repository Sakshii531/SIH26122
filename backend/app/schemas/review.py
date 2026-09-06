from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import ReviewDecision


class ReviewBase(BaseModel):
    """Base fields for a Human Planner Review."""

    activity_match_id: UUID = Field(..., description="Target activity match UUID")
    planner_id: str = Field(..., description="ID / Username of reviewing planner")
    decision: ReviewDecision = Field(..., description="Planner review decision (APPROVED, REJECTED, etc.)")
    corrected_activity_id: Optional[UUID] = Field(None, description="Corrected schedule activity UUID if planner overrides AI")
    comments: Optional[str] = Field(None, description="Planner comments or review notes")
    override_reason: Optional[str] = Field(None, description="Explicit reason if AI match was overridden or rejected")


class ReviewCreate(ReviewBase):
    """Schema for submitting a Review decision."""

    pass


class ReviewResponse(ReviewBase):
    """Schema for Review responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique review decision UUID")
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
