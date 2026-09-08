from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.auth import AuthUser, require_planner
from app.schemas.progress_event import ProgressEventResponse
from app.schemas.progress_request import ProgressFromReviewCreate
from app.services.progress_workflow_service import ProgressWorkflowService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("", response_model=ProgressEventResponse, status_code=201)
async def create_progress(
    payload: ProgressFromReviewCreate,
    _user: AuthUser = Depends(require_planner),
) -> ProgressEventResponse:
    """Create a validated ProgressEvent from an APPROVED or MODIFIED human review. Requires PLANNER or ADMIN."""
    return ProgressWorkflowService.create_progress_from_review(payload)


@router.get("", response_model=List[ProgressEventResponse])
async def list_progress(
    activity_id: Optional[UUID] = Query(None, description="Optional schedule activity UUID filter"),
    report_id: Optional[UUID] = Query(None, description="Optional field report UUID filter"),
    _user: AuthUser = Depends(require_planner),
) -> List[ProgressEventResponse]:
    """List progress events with optional filtering. Requires PLANNER or ADMIN."""
    return ProgressWorkflowService.list_progress(activity_id=activity_id, report_id=report_id)


@router.get("/{progress_id}", response_model=ProgressEventResponse)
async def get_progress(
    progress_id: UUID,
    _user: AuthUser = Depends(require_planner),
) -> ProgressEventResponse:
    """Retrieve a progress event by its UUID. Requires PLANNER or ADMIN."""
    return ProgressWorkflowService.get_progress_by_id(progress_id)
