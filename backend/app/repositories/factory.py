from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.repositories.in_memory import (
    InMemoryActivityMatchRepository,
    InMemoryActivityRepository,
    InMemoryActualProgressRepository,
    InMemoryAuditLogRepository,
    InMemoryConflictRepository,
    InMemoryEvidenceRepository,
    InMemoryExtractedProgressEventRepository,
    InMemoryFieldReportRepository,
    InMemoryPlannerReviewRepository,
    InMemoryProjectRepository,
    InMemoryScheduleRepository,
    InMemoryUserRepository,
    InMemoryWBSRepository,
)
from app.repositories.interfaces import (
    IActivityMatchRepository,
    IActivityRepository,
    IActualProgressRepository,
    IAuditLogRepository,
    IConflictRepository,
    IEvidenceRepository,
    IExtractedProgressEventRepository,
    IFieldReportRepository,
    IPlannerReviewRepository,
    IProjectRepository,
    IScheduleRepository,
    IUserRepository,
    IWBSRepository,
)

# Global singleton repository instances for in-memory mode
_project_repo = InMemoryProjectRepository()
_schedule_repo = InMemoryScheduleRepository()
_wbs_repo = InMemoryWBSRepository()
_activity_repo = InMemoryActivityRepository()
_field_report_repo = InMemoryFieldReportRepository()
_evidence_repo = InMemoryEvidenceRepository()
_extracted_progress_event_repo = InMemoryExtractedProgressEventRepository()
_activity_match_repo = InMemoryActivityMatchRepository()
_planner_review_repo = InMemoryPlannerReviewRepository()
_conflict_repo = InMemoryConflictRepository()
_actual_progress_repo = InMemoryActualProgressRepository()
_audit_log_repo = InMemoryAuditLogRepository()
_user_repo = InMemoryUserRepository()


def get_project_repository() -> IProjectRepository:
    return _project_repo


def get_schedule_repository() -> IScheduleRepository:
    return _schedule_repo


def get_wbs_repository() -> IWBSRepository:
    return _wbs_repo


def get_activity_repository() -> IActivityRepository:
    return _activity_repo


def get_field_report_repository() -> IFieldReportRepository:
    return _field_report_repo


def get_evidence_repository() -> IEvidenceRepository:
    return _evidence_repo


def get_extracted_progress_event_repository() -> IExtractedProgressEventRepository:
    return _extracted_progress_event_repo


def get_activity_match_repository() -> IActivityMatchRepository:
    return _activity_match_repo


def get_planner_review_repository() -> IPlannerReviewRepository:
    return _planner_review_repo


def get_conflict_repository() -> IConflictRepository:
    return _conflict_repo


def get_actual_progress_repository() -> IActualProgressRepository:
    return _actual_progress_repo


def get_audit_log_repository() -> IAuditLogRepository:
    return _audit_log_repo


def get_user_repository() -> IUserRepository:
    return _user_repo


def reset_all_repositories() -> None:
    """Reset state across all repositories."""
    _project_repo.clear()
    _schedule_repo.clear()
    _wbs_repo.clear()
    _activity_repo.clear()
    _field_report_repo.clear()
    _evidence_repo.clear()
    _extracted_progress_event_repo.clear()
    _activity_match_repo.clear()
    _planner_review_repo.clear()
    _conflict_repo.clear()
    _actual_progress_repo.clear()
    _audit_log_repo.clear()
    _user_repo.clear()
