from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.db.supabase_client import get_request_access_token
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
from app.repositories.supabase_repos import (
    SupabaseActivityMatchRepository,
    SupabaseActivityRepository,
    SupabaseActualProgressRepository,
    SupabaseAuditLogRepository,
    SupabaseConflictRepository,
    SupabaseEvidenceRepository,
    SupabaseExtractedProgressEventRepository,
    SupabaseFieldReportRepository,
    SupabasePlannerReviewRepository,
    SupabaseProjectRepository,
    SupabaseScheduleRepository,
    SupabaseUserRepository,
    SupabaseWBSRepository,
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

# Lazy singletons for Supabase mode
_supabase_project_repo = None
_supabase_schedule_repo = None
_supabase_wbs_repo = None
_supabase_activity_repo = None
_supabase_field_report_repo = None
_supabase_evidence_repo = None
_supabase_extracted_progress_event_repo = None
_supabase_activity_match_repo = None
_supabase_planner_review_repo = None
_supabase_conflict_repo = None
_supabase_actual_progress_repo = None
_supabase_audit_log_repo = None
_supabase_user_repo = None


def _get_supabase_repository(repository_type, cache_name):
    """Use a request-bound repository when RLS must see the caller's token."""
    if get_request_access_token():
        return repository_type()
    repository = globals()[cache_name]
    if repository is None:
        repository = repository_type()
        globals()[cache_name] = repository
    return repository


def get_project_repository() -> IProjectRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseProjectRepository, "_supabase_project_repo")
    return _project_repo


def get_schedule_repository() -> IScheduleRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseScheduleRepository, "_supabase_schedule_repo")
    return _schedule_repo


def get_wbs_repository() -> IWBSRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseWBSRepository, "_supabase_wbs_repo")
    return _wbs_repo


def get_activity_repository() -> IActivityRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseActivityRepository, "_supabase_activity_repo")
    return _activity_repo


def get_field_report_repository() -> IFieldReportRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseFieldReportRepository, "_supabase_field_report_repo")
    return _field_report_repo


def get_evidence_repository() -> IEvidenceRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseEvidenceRepository, "_supabase_evidence_repo")
    return _evidence_repo


def get_extracted_progress_event_repository() -> IExtractedProgressEventRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseExtractedProgressEventRepository, "_supabase_extracted_progress_event_repo")
    return _extracted_progress_event_repo


def get_activity_match_repository() -> IActivityMatchRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseActivityMatchRepository, "_supabase_activity_match_repo")
    return _activity_match_repo


def get_planner_review_repository() -> IPlannerReviewRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabasePlannerReviewRepository, "_supabase_planner_review_repo")
    return _planner_review_repo


def get_conflict_repository() -> IConflictRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseConflictRepository, "_supabase_conflict_repo")
    return _conflict_repo


def get_actual_progress_repository() -> IActualProgressRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseActualProgressRepository, "_supabase_actual_progress_repo")
    return _actual_progress_repo


def get_audit_log_repository() -> IAuditLogRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseAuditLogRepository, "_supabase_audit_log_repo")
    return _audit_log_repo


def get_user_repository() -> IUserRepository:
    if get_settings().DB_PROVIDER == "supabase":
        return _get_supabase_repository(SupabaseUserRepository, "_supabase_user_repo")
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

    global _supabase_project_repo, _supabase_schedule_repo, _supabase_wbs_repo
    global _supabase_activity_repo, _supabase_field_report_repo, _supabase_evidence_repo
    global _supabase_extracted_progress_event_repo, _supabase_activity_match_repo
    global _supabase_planner_review_repo, _supabase_conflict_repo, _supabase_actual_progress_repo
    global _supabase_audit_log_repo, _supabase_user_repo

    _supabase_project_repo = None
    _supabase_schedule_repo = None
    _supabase_wbs_repo = None
    _supabase_activity_repo = None
    _supabase_field_report_repo = None
    _supabase_evidence_repo = None
    _supabase_extracted_progress_event_repo = None
    _supabase_activity_match_repo = None
    _supabase_planner_review_repo = None
    _supabase_conflict_repo = None
    _supabase_actual_progress_repo = None
    _supabase_audit_log_repo = None
    _supabase_user_repo = None

