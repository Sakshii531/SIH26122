from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import FieldReportFormat, MatchStatus
from app.schemas.field_report import EvidenceItem


class FieldReportExtractionRequest(BaseModel):
    """Payload sent to AI/ML service for field report entity & progress extraction."""

    report_id: UUID = Field(..., description="Target field report UUID")
    project_id: Optional[UUID] = Field(None, description="Associated project UUID")
    source_format: FieldReportFormat = Field(default=FieldReportFormat.TEXT, description="Format of report (TEXT, VOICE, DPR, EXCEL, PHOTO)")
    raw_content: str = Field(..., description="Normalized text, transcript, or parsed content reference")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")


class FieldReportExtractionResponse(BaseModel):
    """Response returned by AI/ML service containing extracted progress info."""

    report_id: UUID = Field(..., description="Target field report UUID")
    extracted_activity_name: Optional[str] = Field(None, description="Extracted activity description or title")
    extracted_progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Extracted progress percentage (0.0 - 100.0)")
    extracted_status: Optional[str] = Field(None, description="Extracted activity execution status")
    location: Optional[str] = Field(None, description="Extracted site location or section")
    discipline: Optional[str] = Field(None, description="Extracted engineering discipline")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Associated supporting evidence items")
    extraction_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall AI extraction confidence score (0.0 - 1.0)")
    warnings: List[str] = Field(default_factory=list, description="AI extraction warnings or ambiguity notes")
    processing_status: str = Field(default="SUCCESS", description="Extraction status: SUCCESS, PARTIAL, or FAILED")

    model_config = ConfigDict(from_attributes=True)


class CandidateActivity(BaseModel):
    """Candidate schedule activity provided to AI/ML matching engine."""

    activity_id: UUID = Field(..., description="Schedule activity UUID")
    activity_code: str = Field(..., description="Schedule activity code (e.g. ACT-101)")
    name: str = Field(..., description="Schedule activity description")
    wbs_code: str = Field(..., description="Schedule WBS code")
    discipline: str = Field(..., description="Engineering discipline")


class ActivityMatchingRequest(BaseModel):
    """Payload sent to AI/ML service for semantic L5/L6 activity matching."""

    report_id: UUID = Field(..., description="Target field report UUID")
    extracted_information: Dict[str, Any] = Field(..., description="Extracted activity information dictionary")
    candidate_activities: List[CandidateActivity] = Field(default_factory=list, description="Candidate schedule activities for matching")


class AlternativeCandidateMatch(BaseModel):
    """Alternative candidate match recommendation."""

    activity_id: UUID = Field(..., description="Alternative activity UUID")
    activity_code: str = Field(..., description="Alternative activity code")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Match confidence score (0.0 - 1.0)")
    rationale: Optional[str] = Field(None, description="Matching rationale")


class ActivityMatchingResponse(BaseModel):
    """Response returned by AI/ML activity matching service."""

    report_id: UUID = Field(..., description="Target field report UUID")
    matched_activity_id: Optional[UUID] = Field(None, description="Matched schedule activity UUID (if found)")
    matched_activity_code: Optional[str] = Field(None, description="Matched schedule activity code")
    match_confidence: float = Field(..., ge=0.0, le=1.0, description="Matching confidence score (0.0 - 1.0)")
    match_status: MatchStatus = Field(default=MatchStatus.NEEDS_REVIEW, description="Match status (AUTO_MATCHED, NEEDS_REVIEW, etc.)")
    reasoning: Optional[str] = Field(None, description="AI matching rationale or evidence explanation")
    alternative_candidates: List[AlternativeCandidateMatch] = Field(default_factory=list, description="Top alternative candidate matches")

    model_config = ConfigDict(from_attributes=True)
