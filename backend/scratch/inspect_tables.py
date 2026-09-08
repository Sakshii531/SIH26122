from app.db.supabase_client import get_service_role_client

client = get_service_role_client()

tables = [
    "projects", "schedules", "wbs_nodes", "schedule_activities",
    "field_reports", "evidence", "extracted_progress_events",
    "activity_matches", "planner_reviews", "conflicts",
    "actual_progress", "audit_logs", "users"
]

for t in tables:
    try:
        res = client.table(t).select("*").limit(1).execute()
        print(f"Table '{t}': EXISTS - sample row: {res.data}")
    except Exception as e:
        print(f"Table '{t}': ERROR -> {e}")
