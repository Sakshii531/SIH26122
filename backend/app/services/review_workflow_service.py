from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException

from app.repositories.factory import get_planner_review_repository
from app.schemas.enums import ReviewDecision, ReviewStatus
from app.schemas.review_workflow import (
    ReviewDecisionRequest,
    ReviewItemCreate,
    ReviewItemResponse,
)


class ReviewWorkflowService:
    """Service managing the Human Review & Confidence Workflow via repository layer."""

    @classmethod
    def create_review_item(cls, payload: ReviewItemCreate) -> ReviewItemResponse:
        """Create a new human review item for an AI extraction/match result (initial status PENDING)."""
        repo = get_planner_review_repository()
        return repo.create(payload)

    @classmethod
    def get_review_item(cls, review_id: UUID) -> ReviewItemResponse:
        """Retrieve a review item by its UUID."""
        repo = get_planner_review_repository()
        item = repo.get_by_id(review_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Review item '{review_id}' not found.",
            )
        return item

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

        repo = get_planner_review_repository()
        return repo.update(review_id, updated_review)

    @classmethod
    def list_reviews(cls, status: Optional[ReviewStatus] = None) -> List[ReviewItemResponse]:
        """List review items with optional status filtering."""
        repo = get_planner_review_repository()
        return repo.list_all(status=status)

    @classmethod
    def clear_db(cls) -> None:
        """Reset repository store for testing isolation."""
        repo = get_planner_review_repository()
        try:
            repo.clear()
        except NotImplementedError:
            pass
