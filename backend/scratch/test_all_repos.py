from app.db.supabase_client import get_service_role_client

client = get_service_role_client()

tables = [
    ("projects", "project_id"),
    ("schedules", "schedule_id"),
    ("wbs", "wbs_id"),
    ("activities", "activity_id"),
    ("field_reports", "report_id"),
    ("evidence", "evidence_id"),
    ("extracted_progress_events", "event_id"),
    ("activity_matches", "match_id"),
    ("planner_reviews", "review_id"),
    ("conflicts", "conflict_id"),
    ("actual_progress", "progress_id"),
    ("audit_logs", "audit_id"),
    ("users", "user_id"),
]

for table_name, pk_col in tables:
    try:
        res = client.table(table_name).select("*").limit(1).execute()
        if res.data:
            print(f"Table '{table_name}': PK={pk_col}, keys={list(res.data[0].keys())}")
        else:
            print(f"Table '{table_name}': EMPTY")
    except Exception as e:
        print(f"Table '{table_name}': ERROR -> {e}")
