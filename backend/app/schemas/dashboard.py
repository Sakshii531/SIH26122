from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.enums import ActivityLevel, ActivityStatus, AuditEventType, ReviewStatus


# ── Summary (GET /dashboard/summary) ─────────────────────────────────────────


class ReviewSummary(BaseModel):
    """Breakdown of review items by status."""

    total: int = Field(0, description="Total review items")
    pending: int = Field(0, description="PENDING reviews awaiting decision")
    approved: int = Field(0, description="APPROVED reviews")
    rejected: int = Field(0, description="REJECTED reviews")
    modified: int = Field(0, description="MODIFIED reviews")


class DashboardSummaryResponse(BaseModel):
    """Aggregated project-wide execution metrics incorporating ER concepts."""

    # ── Activity / Schedule counts (ER: activities) ─────────────────────────
    total_activities: int = Field(0, description="Total schedule activities imported")
    completed_activities: int = Field(0, description="Activities with COMPLETED status")
    in_progress_activities: int = Field(0, description="Activities currently IN_PROGRESS")
    delayed_activities: int = Field(0, description="Activities marked DELAYED")

    # ── Review queue (ER: planner_reviews) ──────────────────────────────────
    pending_reviews: int = Field(0, description="Review items awaiting a decision")
    approved_reviews: int = Field(0, description="APPROVED review items")
    rejected_reviews: int = Field(0, description="REJECTED review items")
    modified_reviews: int = Field(0, description="MODIFIED review items")

    # ── Progress events & Actual Progress (ER: actual_progress) ─────────────
    total_progress_events: int = Field(0, description="Total validated progress events recorded")
    total_actual_progress: int = Field(0, description="Total actual progress records (ER concept)")
    average_match_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Mean AI confidence score across all review items (null when no reviews)"
    )

    # ── Conflicts & Audit Logs (ER: conflicts, audit_logs) ──────────────────
    total_conflicts: int = Field(0, description="Total detected conflicts (ER concept)")
    total_audit_logs: int = Field(0, description="Total audit log entries recorded (ER concept)")

    model_config = ConfigDict(from_attributes=True)


# ── Project-level summary (GET /dashboard/projects/{project_id}) ──────────────


class ProjectExecutionSummary(BaseModel):
    """Per-project execution KPIs derived from progress events, reviews, conflicts, and audit logs."""

    project_id: UUID = Field(..., description="Project UUID")
    total_progress_events: int = Field(0, description="Total progress events for this project")
    total_actual_progress: int = Field(0, description="Total actual progress records for this project")
    average_progress_percentage: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Mean progress percentage across events (null when no events)"
    )
    total_audit_logs: int = Field(0, description="Total audit log entries for this project (ER: audit_logs)")
    total_conflicts: int = Field(0, description="Total conflicts for this project (ER: conflicts)")

    model_config = ConfigDict(from_attributes=True)


# ── Activity reporting (GET /dashboard/activities) ────────────────────────────


class ActivityReportItem(BaseModel):
    """Normalised per-activity progress record for frontend reporting."""

    schedule_activity_id: UUID = Field(..., description="Schedule activity UUID")
    project_id: UUID = Field(..., description="Project UUID")
    wbs_id: Optional[UUID] = Field(None, description="Associated WBS node UUID (if available)")

    # Latest confirmed progress values (from newest progress event)
    latest_progress_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Most recent validated completion %")
    progress_status: str = Field(..., description="Progress status from the latest event")
    total_events: int = Field(0, description="Number of progress events for this activity")

    # Populated from review item metadata where available
    discipline: Optional[str] = Field(None, description="Engineering discipline")
    activity_level: Optional[str] = Field(None, description="Activity level (L5/L6) — if available")

    last_updated: datetime = Field(..., description="Timestamp of the most recent progress event")

    @computed_field
    @property
    def activity_id(self) -> UUID:
        """ER diagram terminology alias for activity ID."""
        return self.schedule_activity_id

    model_config = ConfigDict(from_attributes=True)



class ActivityReportResponse(BaseModel):
    """Paginated activity reporting list."""

    total: int = Field(..., description="Total matching activities")
    items: List[ActivityReportItem] = Field(default_factory=list)


# ── Recent activity feed (GET /dashboard/recent-activity) ────────────────────


class RecentActivityItem(BaseModel):
    """Single entry in the recent-activity feed."""

    id: UUID = Field(..., description="Event UUID")
    event_kind: str = Field(
        ...,
        description=(
            "Event category: 'progress' | 'review_decision' | 'audit'"
        ),
    )
    project_id: Optional[UUID] = Field(None)
    description: str = Field(..., description="Human-readable summary")
    actor_id: Optional[str] = Field(None, description="Actor who triggered the event")
    timestamp: datetime = Field(..., description="Event timestamp (UTC)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional extra context")

    model_config = ConfigDict(from_attributes=True)


class RecentActivityResponse(BaseModel):
    """Frontend-friendly recent-activity feed."""

    total: int = Field(..., description="Number of events returned")
    items: List[RecentActivityItem] = Field(default_factory=list)
