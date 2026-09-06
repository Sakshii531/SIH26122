from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import ReviewDecision, ReviewStatus
from app.schemas.field_report import EvidenceItem


class ReviewItemCreate(BaseModel):
    """Payload to create a human review item for an AI extraction/match result."""

    report_id: UUID = Field(..., description="Target field report UUID")
    schedule_activity_id: Optional[UUID] = Field(None, description="AI-matched schedule activity UUID (if any)")
    matched_activity_code: Optional[str] = Field(None, description="AI-matched activity code")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence score between 0.0 and 1.0")
    extracted_progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="AI-extracted progress percentage")
    extracted_status: Optional[str] = Field(None, description="AI-extracted status string")
    discipline: Optional[str] = Field(None, description="Discipline")
    location: Optional[str] = Field(None, description="Location")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Evidence items attached to report")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional review metadata")


class ReviewDecisionRequest(BaseModel):
    """Payload for submitting a reviewer decision on a review item."""

    decision: ReviewDecision = Field(..., description="Review decision: APPROVED, REJECTED, or MODIFIED")
    reviewer_id: str = Field(..., description="ID or username of reviewing planner", min_length=1)
    corrected_activity_id: Optional[UUID] = Field(None, description="Corrected schedule activity UUID if MODIFIED")
    corrected_progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Corrected progress percentage if MODIFIED")
    comments: Optional[str] = Field(None, description="Reviewer notes or comments")
    corrected_evidence: Optional[List[EvidenceItem]] = Field(None, description="Updated evidence items if MODIFIED")


class ReviewItemResponse(BaseModel):
    """Full detail response model for a human review item."""

    id: UUID = Field(default_factory=uuid4, description="Unique review item UUID")
    report_id: UUID = Field(..., description="Target field report UUID")
    schedule_activity_id: Optional[UUID] = Field(None, description="Associated schedule activity UUID")
    matched_activity_code: Optional[str] = Field(None, description="Associated activity code")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, description="Review item status (PENDING, APPROVED, REJECTED, MODIFIED)")

    decision: Optional[ReviewDecision] = Field(None, description="Submitted reviewer decision")
    reviewer_id: Optional[str] = Field(None, description="ID of reviewing planner")
    corrected_activity_id: Optional[UUID] = Field(None, description="Corrected activity UUID")
    corrected_progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Corrected progress percentage")
    comments: Optional[str] = Field(None, description="Reviewer comments")

    extracted_progress_percentage: Optional[float] = Field(None, description="AI-extracted progress percentage")
    extracted_status: Optional[str] = Field(None, description="AI-extracted status string")
    discipline: Optional[str] = Field(None, description="Discipline")
    location: Optional[str] = Field(None, description="Location")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Attached evidence items")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Review metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Review item creation timestamp")
    decision_at: Optional[datetime] = Field(None, description="Decision submission timestamp")

    model_config = ConfigDict(from_attributes=True)
