from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

from app.schemas.dashboard import (
    ActivityReportItem,
    ActivityReportResponse,
    DashboardSummaryResponse,
    ProjectExecutionSummary,
    RecentActivityItem,
    RecentActivityResponse,
)
from app.schemas.enums import ActivityLevel, ProgressStatus, ReviewStatus
from app.services.audit_service import AuditService
from app.services.progress_workflow_service import ProgressWorkflowService
from app.services.review_workflow_service import ReviewWorkflowService


class DashboardService:
    """
    Read-only aggregation service for dashboard reporting.

    All data is sourced exclusively from the in-memory stores of the existing
    workflow services:
      - ReviewWorkflowService._reviews_db
      - ProgressWorkflowService._progress_db  / _review_progress_map
      - AuditService._audit_db

    No independent data store is created here.  No hardcoded / mock values.
    Empty datasets always return valid zero / empty responses.
    """

    # ── 1. Global summary ─────────────────────────────────────────────────────

    @classmethod
    def get_summary(cls) -> DashboardSummaryResponse:
        """Aggregate project-wide execution metrics from all in-memory stores.

        Reads:
          • ReviewWorkflowService  → review counts & average confidence
          • ProgressWorkflowService → total events & activity-level counts
        """

        # ── Review counts ─────────────────────────────────────────────────────
        all_reviews = ReviewWorkflowService.list_reviews()

        pending = sum(1 for r in all_reviews if r.status == ReviewStatus.PENDING)
        approved = sum(1 for r in all_reviews if r.status == ReviewStatus.APPROVED)
        rejected = sum(1 for r in all_reviews if r.status == ReviewStatus.REJECTED)
        modified = sum(1 for r in all_reviews if r.status == ReviewStatus.MODIFIED)

        # Average confidence across ALL review items (not just decided ones)
        avg_confidence: Optional[float] = None
        if all_reviews:
            avg_confidence = round(
                sum(r.confidence_score for r in all_reviews) / len(all_reviews), 4
            )

        # ── Progress events ───────────────────────────────────────────────────
        all_progress = ProgressWorkflowService.list_progress()

        # Each unique schedule_activity_id is represented by its *latest*
        # progress event (highest timestamp).
        latest_per_activity: Dict[UUID, object] = {}
        for pe in all_progress:
            existing = latest_per_activity.get(pe.schedule_activity_id)
            if existing is None or pe.timestamp > existing.timestamp:  # type: ignore[union-attr]
                latest_per_activity[pe.schedule_activity_id] = pe

        total_activities = len(latest_per_activity)

        completed = sum(
            1
            for pe in latest_per_activity.values()
            if pe.progress_percentage == 100.0  # type: ignore[union-attr]
        )
        in_progress = sum(
            1
            for pe in latest_per_activity.values()
            if 0.0 < pe.progress_percentage < 100.0  # type: ignore[union-attr]
        )
        # "Delayed" = the latest progress event for that activity has status PAUSED
        # Use enum comparison (ProgressStatus is a str-enum so == works directly).
        delayed = sum(
            1
            for pe in latest_per_activity.values()
            if pe.status == ProgressStatus.PAUSED  # type: ignore[union-attr]
        )

        return DashboardSummaryResponse(
            total_activities=total_activities,
            completed_activities=completed,
            in_progress_activities=in_progress,
            delayed_activities=delayed,
            pending_reviews=pending,
            approved_reviews=approved,
            rejected_reviews=rejected,
            modified_reviews=modified,
            total_progress_events=len(all_progress),
            average_match_confidence=avg_confidence,
        )

    # ── 2. Project-level summary ──────────────────────────────────────────────

    @classmethod
    def get_project_summary(cls, project_id: UUID) -> ProjectExecutionSummary:
        """Return execution KPIs scoped to a single project.

        Filters ProgressWorkflowService and AuditService by project_id.
        Never raises 404 — returns zeros for unknown projects.
        """

        project_events = [
            pe
            for pe in ProgressWorkflowService.list_progress()
            if pe.project_id == project_id
        ]

        avg_pct: Optional[float] = None
        if project_events:
            avg_pct = round(
                sum(pe.progress_percentage for pe in project_events) / len(project_events), 2
            )

        project_audit_events = [
            a
            for a in AuditService.list_audit_events()
            if a.project_id == project_id
        ]

        return ProjectExecutionSummary(
            project_id=project_id,
            total_progress_events=len(project_events),
            average_progress_percentage=avg_pct,
            total_audit_events=len(project_audit_events),
        )

    # ── 3. Activity reporting list ────────────────────────────────────────────

    @classmethod
    def get_activities(
        cls,
        project_id: Optional[UUID] = None,
        activity_level: Optional[ActivityLevel] = None,
        status: Optional[str] = None,
        discipline: Optional[str] = None,
    ) -> ActivityReportResponse:
        """Return normalised per-activity reporting data.

        All data is sourced from ProgressWorkflowService and
        ReviewWorkflowService — no independent store.

        Filters (all optional, all AND-combined):
          • project_id      — exact match on progress event project_id
          • activity_level  — L5/L6 level; not stored on progress events.
                              When supplied the filter always returns empty
                              (ScheduleIngestionService has no persistent _db).
          • status          — case-insensitive match on ProgressStatus value
          • discipline      — case-insensitive match from linked review item
        """

        # Short-circuit: activity_level requires a persistent schedule store
        # that does not yet exist.  Return an empty result cleanly.
        if activity_level is not None:
            return ActivityReportResponse(total=0, items=[])

        all_progress = ProgressWorkflowService.list_progress()
        all_reviews = ReviewWorkflowService.list_reviews()

        # Build a lookup: schedule_activity_id → most-recent review item
        review_by_activity: Dict[UUID, object] = {}
        for rev in all_reviews:
            if rev.schedule_activity_id is None:
                continue
            existing = review_by_activity.get(rev.schedule_activity_id)
            if existing is None or rev.created_at > existing.created_at:  # type: ignore[union-attr]
                review_by_activity[rev.schedule_activity_id] = rev

        # Bucket progress events by activity; keep latest per activity
        latest_per_activity: Dict[UUID, object] = {}
        all_per_activity: Dict[UUID, List[object]] = {}
        for pe in all_progress:
            all_per_activity.setdefault(pe.schedule_activity_id, []).append(pe)
            existing = latest_per_activity.get(pe.schedule_activity_id)
            if existing is None or pe.timestamp > existing.timestamp:  # type: ignore[union-attr]
                latest_per_activity[pe.schedule_activity_id] = pe

        items: List[ActivityReportItem] = []
        for act_id, latest_pe in latest_per_activity.items():

            # ── project_id filter ─────────────────────────────────────────────
            if project_id is not None and latest_pe.project_id != project_id:  # type: ignore[union-attr]
                continue

            # ── status filter — compare against ProgressStatus enum value ─────
            # pe.status is a ProgressStatus str-enum; .value gives the raw string.
            pe_status_str: str = latest_pe.status.value  # type: ignore[union-attr]
            if status is not None and pe_status_str.upper() != status.upper():
                continue

            # ── discipline — from the linked review item ──────────────────────
            rev = review_by_activity.get(act_id)
            item_discipline: Optional[str] = rev.discipline if rev else None  # type: ignore[union-attr]

            if discipline is not None:
                if item_discipline is None or item_discipline.lower() != discipline.lower():
                    continue

            event_count = len(all_per_activity.get(act_id, []))

            items.append(
                ActivityReportItem(
                    schedule_activity_id=act_id,
                    project_id=latest_pe.project_id,  # type: ignore[union-attr]
                    latest_progress_percentage=latest_pe.progress_percentage,  # type: ignore[union-attr]
                    progress_status=pe_status_str,
                    total_events=event_count,
                    discipline=item_discipline,
                    activity_level=None,  # populated once activities are persisted
                    last_updated=latest_pe.timestamp,  # type: ignore[union-attr]
                )
            )

        # Sort newest-first by last_updated
        items.sort(key=lambda x: x.last_updated, reverse=True)

        return ActivityReportResponse(total=len(items), items=items)

    # ── 4. Recent-activity feed ───────────────────────────────────────────────

    @classmethod
    def get_recent_activity(cls, limit: int = 20) -> RecentActivityResponse:
        """Return the most recent `limit` events merged from:
          • Validated progress events  (event_kind="progress")
          • Finalized review decisions (event_kind="review_decision")
          • Audit events               (event_kind="audit")

        Sorted newest-first.  Only PENDING reviews are excluded (they have no
        decision_at timestamp yet).

        All data comes from the existing in-memory stores — no fabricated values.
        """
        feed: List[RecentActivityItem] = []

        # ── Progress events ───────────────────────────────────────────────────
        for pe in ProgressWorkflowService.list_progress():
            feed.append(
                RecentActivityItem(
                    id=pe.id,
                    event_kind="progress",
                    project_id=pe.project_id,
                    description=(
                        f"Progress event recorded: {pe.progress_percentage:.1f}% "
                        f"on activity {pe.schedule_activity_id}"
                    ),
                    actor_id=None,
                    timestamp=pe.timestamp,
                    metadata={
                        "progress_percentage": pe.progress_percentage,
                        "status": pe.status.value,
                        "schedule_activity_id": str(pe.schedule_activity_id),
                        "review_id": str(pe.review_id) if pe.review_id else None,
                    },
                )
            )

        # ── Decided review items (exclude PENDING — no decision_at yet) ───────
        for rev in ReviewWorkflowService.list_reviews():
            if rev.status == ReviewStatus.PENDING or rev.decision_at is None:
                continue

            # Extract project_id from metadata if present
            raw_pid = rev.metadata.get("project_id") if rev.metadata else None
            review_project_id: Optional[UUID] = None
            if raw_pid is not None:
                try:
                    review_project_id = UUID(str(raw_pid))
                except (ValueError, AttributeError):
                    review_project_id = None

            feed.append(
                RecentActivityItem(
                    id=rev.id,
                    event_kind="review_decision",
                    project_id=review_project_id,
                    description=(
                        f"Review {rev.status.value} by {rev.reviewer_id or 'unknown'} "
                        f"(confidence {rev.confidence_score:.2f})"
                    ),
                    actor_id=rev.reviewer_id,
                    timestamp=rev.decision_at,
                    metadata={
                        "status": rev.status.value,
                        "decision": rev.decision.value if rev.decision else None,
                        "confidence_score": rev.confidence_score,
                        "discipline": rev.discipline,
                        "matched_activity_code": rev.matched_activity_code,
                    },
                )
            )

        # ── Audit events ──────────────────────────────────────────────────────
        for ae in AuditService.list_audit_events():
            feed.append(
                RecentActivityItem(
                    id=ae.id,
                    event_kind="audit",
                    project_id=ae.project_id,
                    description=ae.description,
                    actor_id=ae.actor_id,
                    timestamp=ae.timestamp,
                    metadata={
                        "event_type": ae.event_type.value,
                        "entity_type": ae.entity_type,
                        "entity_id": str(ae.entity_id),
                        "actor_role": ae.actor_role,
                    },
                )
            )

        # Sort descending by timestamp, then cap at limit
        feed.sort(key=lambda x: x.timestamp, reverse=True)
        feed = feed[:limit]

        return RecentActivityResponse(total=len(feed), items=feed)
