from __future__ import annotations

from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.schemas.ai_contract import (
    ActivityMatchingRequest,
    ActivityMatchingResponse,
    AlternativeCandidateMatch,
    FieldReportExtractionRequest,
    FieldReportExtractionResponse,
)
from app.schemas.enums import MatchStatus


class AIIntegrationService:
    """Service stub establishing boundary contract between FastAPI backend and AI/ML pipeline."""

    @classmethod
    def extract_report_data(
        cls,
        report_id: UUID,
        payload: FieldReportExtractionRequest,
    ) -> FieldReportExtractionResponse:
        """Process field report extraction request (integration boundary stub)."""
        if payload.report_id != report_id:
            raise HTTPException(
                status_code=400,
                detail=f"Report ID mismatch: path '{report_id}' vs body '{payload.report_id}'",
            )

        # Mock extraction placeholder (AI model implementation boundary)
        return FieldReportExtractionResponse(
            report_id=report_id,
            extracted_activity_name="Foundation Excavation & Pouring",
            extracted_progress_percentage=45.0,
            extracted_status="IN_PROGRESS",
            location=payload.metadata.get("location", "Zone 1"),
            discipline=payload.metadata.get("discipline", "Civil"),
            evidence=[],
            extraction_confidence=0.88,
            warnings=["Extracted based on structured text placeholder interface."],
            processing_status="SUCCESS",
        )

    @classmethod
    def match_activity(
        cls,
        report_id: UUID,
        payload: ActivityMatchingRequest,
    ) -> ActivityMatchingResponse:
        """Process L5/L6 activity matching request (integration boundary stub)."""
        if payload.report_id != report_id:
            raise HTTPException(
                status_code=400,
                detail=f"Report ID mismatch: path '{report_id}' vs body '{payload.report_id}'",
            )

        matched_id: Optional[UUID] = None
        matched_code: Optional[str] = None
        alternatives: List[AlternativeCandidateMatch] = []

        if payload.candidate_activities:
            primary = payload.candidate_activities[0]
            matched_id = primary.activity_id
            matched_code = primary.activity_code

            for cand in payload.candidate_activities[1:]:
                alternatives.append(
                    AlternativeCandidateMatch(
                        activity_id=cand.activity_id,
                        activity_code=cand.activity_code,
                        confidence_score=0.72,
                        rationale=f"Secondary semantic candidate match for {cand.name}",
                    )
                )

        confidence = 0.85 if matched_id else 0.50
        status = MatchStatus.AUTO_MATCHED if confidence >= 0.80 else MatchStatus.NEEDS_REVIEW

        return ActivityMatchingResponse(
            report_id=report_id,
            matched_activity_id=matched_id,
            matched_activity_code=matched_code,
            match_confidence=confidence,
            match_status=status,
            reasoning=f"Matched against top candidate using semantic placeholder contract.",
            alternative_candidates=alternatives,
        )
