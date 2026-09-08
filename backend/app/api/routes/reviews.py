from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.auth import AuthUser, require_planner, require_supervisor
from app.schemas.enums import ReviewStatus
from app.schemas.review_workflow import (
    ReviewDecisionRequest,
    ReviewItemCreate,
    ReviewItemResponse,
)
from app.services.review_workflow_service import ReviewWorkflowService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewItemResponse, status_code=201)
async def create_review(
    payload: ReviewItemCreate,
    _user: AuthUser = Depends(require_supervisor),
) -> ReviewItemResponse:
    """Create a new human review item for an AI extraction/matching result. Requires SUPERVISOR, PLANNER, or ADMIN."""
    return ReviewWorkflowService.create_review_item(payload)


@router.get("", response_model=List[ReviewItemResponse])
async def list_reviews(
    status: Optional[ReviewStatus] = Query(None, description="Optional status filter (PENDING, APPROVED, REJECTED, MODIFIED)"),
    _user: AuthUser = Depends(require_supervisor),
) -> List[ReviewItemResponse]:
    """List review items with optional status filtering. Requires SUPERVISOR, PLANNER, or ADMIN."""
    return ReviewWorkflowService.list_reviews(status=status)


@router.get("/{review_id}", response_model=ReviewItemResponse)
async def get_review(
    review_id: UUID,
    _user: AuthUser = Depends(require_supervisor),
) -> ReviewItemResponse:
    """Retrieve a review item by its UUID. Requires SUPERVISOR, PLANNER, or ADMIN."""
    return ReviewWorkflowService.get_review_item(review_id)


@router.post("/{review_id}/decision", response_model=ReviewItemResponse)
async def submit_review_decision(
    review_id: UUID,
    payload: ReviewDecisionRequest,
    _user: AuthUser = Depends(require_planner),
) -> ReviewItemResponse:
    """Submit a reviewer decision (APPROVED, REJECTED, MODIFIED). Requires PLANNER or ADMIN."""
    return ReviewWorkflowService.submit_decision(review_id, payload)
