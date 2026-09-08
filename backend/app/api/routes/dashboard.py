from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.auth import AuthUser, get_current_user
from app.schemas.dashboard import (
    ActivityReportResponse,
    DashboardSummaryResponse,
    ProjectExecutionSummary,
    RecentActivityResponse,
)
from app.schemas.enums import ActivityLevel
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Global execution metrics",
)
def get_summary(user: AuthUser = Depends(get_current_user)) -> DashboardSummaryResponse:
    """
    Return aggregated project-wide execution metrics. Requires authentication.

    - Activity counts (total / completed / in-progress / delayed)
    - Review queue counts (pending / approved / rejected / modified)
    - Total progress events recorded
    - Average AI match confidence across all review items
    """
    return DashboardService.get_summary()


@router.get(
    "/projects/{project_id}",
    response_model=ProjectExecutionSummary,
    summary="Per-project execution summary",
)
def get_project_summary(
    project_id: UUID,
    user: AuthUser = Depends(get_current_user),
) -> ProjectExecutionSummary:
    """
    Return execution KPIs scoped to a single project. Requires authentication.

    - Number of progress events
    - Average completion percentage
    - Number of audit log entries
    """
    return DashboardService.get_project_summary(project_id)


@router.get(
    "/activities",
    response_model=ActivityReportResponse,
    summary="Activity progress reporting list",
)
def get_activities(
    project_id: Optional[UUID] = Query(None, description="Filter by project UUID"),
    activity_level: Optional[ActivityLevel] = Query(
        None, description="Filter by schedule level: L5 or L6"
    ),
    status: Optional[str] = Query(
        None, description="Filter by progress status (e.g. IN_PROGRESS, COMPLETED, PAUSED)"
    ),
    discipline: Optional[str] = Query(
        None, description="Filter by engineering discipline (case-insensitive)"
    ),
    user: AuthUser = Depends(get_current_user),
) -> ActivityReportResponse:
    """
    Return normalised per-activity progress data. Requires authentication.

    All query parameters are optional and combinable. Returns an empty list
    when no data matches — never raises 404.
    """
    return DashboardService.get_activities(
        project_id=project_id,
        activity_level=activity_level,
        status=status,
        discipline=discipline,
    )


@router.get(
    "/recent-activity",
    response_model=RecentActivityResponse,
    summary="Recent progress / review / audit feed",
)
def get_recent_activity(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of events to return (1–100)"),
    user: AuthUser = Depends(get_current_user),
) -> RecentActivityResponse:
    """
    Return the most recent events merged from progress events, review decisions,
    and audit entries — sorted newest-first. Requires authentication.

    Frontend-friendly: each item carries `event_kind`, `description`,
    `actor_id`, `timestamp`, and a `metadata` bag for extra context.
    """
    return DashboardService.get_recent_activity(limit=limit)
