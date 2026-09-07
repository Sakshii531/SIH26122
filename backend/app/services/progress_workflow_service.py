from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.schemas.audit_event import AuditEventCreate
from app.schemas.enums import AuditEventType, ReviewStatus
from app.schemas.progress_event import ProgressEventResponse
from app.schemas.progress_request import ProgressFromReviewCreate
from app.services.audit_service import AuditService
from app.services.review_workflow_service import ReviewWorkflowService


class ProgressWorkflowService:
    """Service managing validated actual progress events and audit trail triggers."""

    _progress_db: Dict[UUID, ProgressEventResponse] = {}
    _review_progress_map: Dict[UUID, UUID] = {}

    @classmethod
    def create_progress_from_review(cls, payload: ProgressFromReviewCreate) -> ProgressEventResponse:
        """Convert an APPROVED or MODIFIED human review into a validated ProgressEvent."""
        review = ReviewWorkflowService.get_review_item(payload.review_id)

        # 1. Reject PENDING or REJECTED reviews
        if review.status in [ReviewStatus.PENDING, ReviewStatus.REJECTED]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot create progress event for review with status '{review.status.value}'. Only APPROVED or MODIFIED reviews are allowed.",
            )

        # 2. Block duplicate progress creation from same review
        if payload.review_id in cls._review_progress_map:
            existing_id = cls._review_progress_map[payload.review_id]
            raise HTTPException(
                status_code=400,
                detail=f"Progress event '{existing_id}' already created for review '{payload.review_id}'.",
            )

        # 3. Resolve target activity ID & progress percentage based on decision (APPROVED vs MODIFIED)
        if review.status == ReviewStatus.APPROVED:
            target_activity_id = payload.schedule_activity_id or review.schedule_activity_id
            progress_pct = (
                review.extracted_progress_percentage
                if review.extracted_progress_percentage is not None
                else 100.0
            )
        else:  # MODIFIED
            target_activity_id = (
                payload.schedule_activity_id or review.corrected_activity_id or review.schedule_activity_id
            )
            progress_pct = (
                review.corrected_progress_percentage
                if review.corrected_progress_percentage is not None
                else (review.extracted_progress_percentage if review.extracted_progress_percentage is not None else 0.0)
            )

        if not target_activity_id:
            raise HTTPException(
                status_code=400,
                detail="Schedule activity ID is required to record progress event.",
            )

        project_id = payload.project_id or review.metadata.get("project_id") or uuid4()
        if isinstance(project_id, str):
            try:
                project_id = UUID(project_id)
            except ValueError:
                project_id = uuid4()

        progress_id = uuid4()
        now = datetime.utcnow()

        progress_event = ProgressEventResponse(
            id=progress_id,
            activity_id=target_activity_id,
            project_id=project_id,
            report_id=review.report_id,
            review_id=review.id,
            status=payload.status,
            actual_start_date=payload.actual_start_date,
            actual_finish_date=payload.actual_finish_date,
            progress_percentage=progress_pct,
            quantity_completed=payload.quantity_completed,
            unit_of_measure=payload.unit_of_measure,
            remarks=payload.remarks or review.comments,
            validated_by=review.reviewer_id or getattr(payload, "validated_by", None),
            timestamp=now,
            created_at=now,
        )

        cls._progress_db[progress_id] = progress_event
        cls._review_progress_map[payload.review_id] = progress_id

        # 4. Automatically record Audit Event
        AuditService.record_audit_event(
            AuditEventCreate(
                project_id=project_id,
                event_type=AuditEventType.PROGRESS_UPDATED,
                entity_type="ProgressEvent",
                entity_id=progress_id,
                actor_id=review.reviewer_id or "PLANNER",
                actor_role="PLANNER",
                description=f"Progress event created from {review.status.value} review for activity '{target_activity_id}'",
                payload={
                    "review_id": str(review.id),
                    "report_id": str(review.report_id),
                    "schedule_activity_id": str(target_activity_id),
                    "progress_percentage": progress_pct,
                    "status": payload.status.value,
                    "review_status": review.status.value,
                },
            )
        )

        return progress_event

    @classmethod
    def get_progress_by_id(cls, progress_id: UUID) -> ProgressEventResponse:
        """Retrieve a progress event by its UUID."""
        if progress_id not in cls._progress_db:
            raise HTTPException(
                status_code=404,
                detail=f"Progress event '{progress_id}' not found.",
            )
        return cls._progress_db[progress_id]

    @classmethod
    def list_progress(
        cls,
        activity_id: Optional[UUID] = None,
        report_id: Optional[UUID] = None,
    ) -> List[ProgressEventResponse]:
        """List progress events with optional activity_id and report_id filters."""
        items = list(cls._progress_db.values())
        if activity_id is not None:
            items = [item for item in items if item.schedule_activity_id == activity_id]
        if report_id is not None:
            items = [item for item in items if item.field_report_id == report_id]
        return items

    @classmethod
    def clear_db(cls) -> None:
        """Reset in-memory progress store for testing isolation."""
        cls._progress_db.clear()
        cls._review_progress_map.clear()
