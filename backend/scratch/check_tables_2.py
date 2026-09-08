from app.db.supabase_client import get_service_role_client

client = get_service_role_client()

tables_to_test = ["wbs", "wbs_nodes", "activities", "schedule_activities"]

for t in tables_to_test:
    try:
        res = client.table(t).select("*").limit(1).execute()
        print(f"Table '{t}': SUCCESS -> {res.data}")
    except Exception as e:
        print(f"Table '{t}': ERROR -> {e}")
