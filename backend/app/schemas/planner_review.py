from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.schemas.enums import ReviewDecision


class PlannerReviewBase(BaseModel):
    """Base fields for a Human Planner Review decision."""

    match_id: Optional[UUID] = Field(None, description="Target activity match UUID")
    activity_match_id: Optional[UUID] = Field(None, description="Target activity match UUID (alias)")
    planner_id: str = Field(..., description="ID / Username of reviewing planner")
    decision: ReviewDecision = Field(..., description="Planner review decision (APPROVED, REJECTED, etc.)")
    corrected_activity_id: Optional[UUID] = Field(None, description="Corrected activity UUID if planner overrides AI")
    comments: Optional[str] = Field(None, description="Planner comments or review notes")
    override_reason: Optional[str] = Field(None, description="Explicit reason if AI match was overridden or rejected")

    @model_validator(mode="before")
    @classmethod
    def sync_id_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            m_id = data.get("match_id") or data.get("activity_match_id")
            if m_id:
                data["match_id"] = m_id
                data["activity_match_id"] = m_id
        return data

    @model_validator(mode="after")
    def ensure_match_id(self) -> PlannerReviewBase:
        if not self.match_id and self.activity_match_id:
            self.match_id = self.activity_match_id
        elif not self.activity_match_id and self.match_id:
            self.activity_match_id = self.match_id
        return self


class PlannerReviewCreate(PlannerReviewBase):
    """Schema for submitting a Planner Review decision."""

    pass


class PlannerReviewResponse(PlannerReviewBase):
    """Schema for Planner Review responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique review decision UUID")
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def review_id(self) -> UUID:
        """ER diagram terminology alias for review ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)


# Backward compatibility aliases
ReviewBase = PlannerReviewBase
ReviewCreate = PlannerReviewCreate
ReviewResponse = PlannerReviewResponse
