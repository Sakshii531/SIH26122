from uuid import uuid4
from datetime import datetime
from app.db.supabase_client import get_service_role_client
from app.repositories.supabase_repos import (
    SupabaseProjectRepository,
    SupabaseScheduleRepository,
    SupabaseWBSRepository,
    SupabaseActivityRepository,
    SupabaseFieldReportRepository,
    SupabaseEvidenceRepository,
    SupabaseExtractedProgressEventRepository,
    SupabaseActivityMatchRepository,
    SupabasePlannerReviewRepository,
    SupabaseConflictRepository,
    SupabaseActualProgressRepository,
    SupabaseAuditLogRepository,
    SupabaseUserRepository,
)

client = get_service_role_client()

repos = [
    ("projects", SupabaseProjectRepository(client=client)),
    ("schedules", SupabaseScheduleRepository(client=client)),
    ("wbs", SupabaseWBSRepository(client=client)),
    ("activities", SupabaseActivityRepository(client=client)),
    ("field_reports", SupabaseFieldReportRepository(client=client)),
    ("evidence", SupabaseEvidenceRepository(client=client)),
    ("extracted_progress_events", SupabaseExtractedProgressEventRepository(client=client)),
    ("activity_matches", SupabaseActivityMatchRepository(client=client)),
    ("planner_reviews", SupabasePlannerReviewRepository(client=client)),
    ("conflicts", SupabaseConflictRepository(client=client)),
    ("actual_progress", SupabaseActualProgressRepository(client=client)),
    ("audit_logs", SupabaseAuditLogRepository(client=client)),
    ("users", SupabaseUserRepository(client=client)),
]

print("Testing list_all() on all 13 Supabase repos...")
for name, repo in repos:
    try:
        items = repo.list_all()
        print(f"Repo '{name}': SUCCESS -> count={len(items)}")
    except Exception as e:
        print(f"Repo '{name}': ERROR -> {e}")
