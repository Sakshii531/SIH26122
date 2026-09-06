from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.schemas.enums import ReviewDecision, ReviewStatus
from app.schemas.review_workflow import (
    ReviewDecisionRequest,
    ReviewItemCreate,
    ReviewItemResponse,
)


class ReviewWorkflowService:
    """In-memory service managing the Human Review & Confidence Workflow."""

    # In-memory store for development/testing
    _reviews_db: Dict[UUID, ReviewItemResponse] = {}

    @classmethod
    def create_review_item(cls, payload: ReviewItemCreate) -> ReviewItemResponse:
        """Create a new human review item for an AI extraction/match result (initial status PENDING)."""
        review_id = uuid4()
        now = datetime.utcnow()

        item = ReviewItemResponse(
            id=review_id,
            report_id=payload.report_id,
            schedule_activity_id=payload.schedule_activity_id,
            matched_activity_code=payload.matched_activity_code,
            confidence_score=payload.confidence_score,
            status=ReviewStatus.PENDING,
            extracted_progress_percentage=payload.extracted_progress_percentage,
            extracted_status=payload.extracted_status,
            discipline=payload.discipline,
            location=payload.location,
            evidence=payload.evidence,
            metadata=payload.metadata,
            created_at=now,
        )

        cls._reviews_db[review_id] = item
        return item

    @classmethod
    def get_review_item(cls, review_id: UUID) -> ReviewItemResponse:
        """Retrieve a review item by its UUID."""
        if review_id not in cls._reviews_db:
            raise HTTPException(
                status_code=404,
                detail=f"Review item '{review_id}' not found.",
            )
        return cls._reviews_db[review_id]

    @classmethod
    def submit_decision(cls, review_id: UUID, payload: ReviewDecisionRequest) -> ReviewItemResponse:
        """Submit a reviewer decision (APPROVED, REJECTED, MODIFIED) for a pending review item."""
        review = cls.get_review_item(review_id)

        if review.status != ReviewStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Review '{review_id}' is already finalized with status '{review.status.value}'.",
            )

        reviewer_id = (payload.reviewer_id or "").strip()
        if not reviewer_id:
            raise HTTPException(status_code=400, detail="Reviewer ID is required.")

        now = datetime.utcnow()

        # Map decision to status
        if payload.decision == ReviewDecision.APPROVED:
            target_status = ReviewStatus.APPROVED
        elif payload.decision == ReviewDecision.REJECTED:
            target_status = ReviewStatus.REJECTED
        else:  # MODIFIED, CORRECTED, OVERRIDDEN
            target_status = ReviewStatus.MODIFIED

        updated_evidence = payload.corrected_evidence if payload.corrected_evidence is not None else review.evidence

        updated_review = review.model_copy(
            update={
                "status": target_status,
                "decision": payload.decision,
                "reviewer_id": reviewer_id,
                "corrected_activity_id": payload.corrected_activity_id or review.schedule_activity_id,
                "corrected_progress_percentage": (
                    payload.corrected_progress_percentage
                    if payload.corrected_progress_percentage is not None
                    else review.extracted_progress_percentage
                ),
                "comments": payload.comments,
                "evidence": updated_evidence,
                "decision_at": now,
            }
        )

        cls._reviews_db[review_id] = updated_review
        return updated_review

    @classmethod
    def list_reviews(cls, status: Optional[ReviewStatus] = None) -> List[ReviewItemResponse]:
        """List review items with optional status filtering."""
        items = list(cls._reviews_db.values())
        if status is not None:
            items = [item for item in items if item.status == status]
        return items

    @classmethod
    def clear_db(cls) -> None:
        """Reset in-memory database for testing isolation."""
        cls._reviews_db.clear()
