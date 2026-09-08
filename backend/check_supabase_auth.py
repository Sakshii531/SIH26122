"""
One-shot diagnostic: queries Supabase to determine:
1. Whether JWT_SECRET is needed (project JWT settings endpoint)
2. What auth configuration is live (alg, issuer)
3. Whether any tables have RLS enabled (via pg_tables + pg_policies)
4. What the actual users table looks like
5. Confirm service-role key can connect at all
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import get_settings
from app.db.supabase_client import get_service_role_client, reset_clients

reset_clients()
settings = get_settings()

print("=== ENV CONFIG ===")
print(f"SUPABASE_URL   : {settings.SUPABASE_URL}")
print(f"SUPABASE_KEY   : {'SET (' + settings.SUPABASE_KEY[:12] + '...)' if settings.SUPABASE_KEY else 'NOT SET'}")
print(f"SVC_ROLE_KEY   : {'SET (' + settings.SUPABASE_SERVICE_ROLE_KEY[:12] + '...)' if settings.SUPABASE_SERVICE_ROLE_KEY else 'NOT SET'}")
print(f"JWT_SECRET     : {'SET' if settings.JWT_SECRET else 'NOT SET ← CRITICAL'}")
print(f"JWT_ALGORITHM  : {settings.JWT_ALGORITHM}")
print(f"AUTH_ENABLED   : {settings.AUTH_ENABLED}")
print()

try:
    client = get_service_role_client()
    print("=== SERVICE ROLE CLIENT: Connected ===\n")
except Exception as e:
    print(f"SERVICE ROLE CLIENT FAILED: {e}")
    sys.exit(1)

# 1. Query RLS status on all relevant tables
print("=== RLS STATUS (pg_tables) ===")
tables_of_interest = [
    "users","projects","schedules","wbs","activities",
    "field_reports","evidence","extracted_progress_events",
    "activity_matches","planner_reviews","actual_progress",
    "audit_logs","conflicts",
]
try:
    rls_q = client.rpc("query_rls_status", {}).execute()
    print(json.dumps(rls_q.data, indent=2))
except Exception:
    # Fall back to direct pg_tables query
    try:
        r = client.from_("pg_tables").select("tablename,rowsecurity").eq("schemaname","public").execute()
        rls_info = {row["tablename"]: row.get("rowsecurity", "?") for row in (r.data or [])}
        for t in tables_of_interest:
            print(f"  {t:<35} RLS={rls_info.get(t, 'NOT FOUND')}")
    except Exception as e2:
        print(f"  Could not query pg_tables: {e2}")

print()

# 2. Query RLS policies
print("=== RLS POLICIES (pg_policies) ===")
try:
    r = client.from_("pg_policies").select("tablename,policyname,roles,cmd,qual,with_check").eq("schemaname","public").execute()
    if r.data:
        for p in r.data:
            print(f"  Table={p['tablename']}  Policy={p['policyname']}  Roles={p['roles']}  Cmd={p['cmd']}")
    else:
        print("  No policies found (or pg_policies not accessible)")
except Exception as e:
    print(f"  pg_policies query failed: {e}")

print()

# 3. Check users table structure
print("=== USERS TABLE (first 3 rows, service role) ===")
try:
    r = client.table("users").select("*").limit(3).execute()
    if r.data:
        print(f"  Columns: {list(r.data[0].keys())}")
        for row in r.data:
            print(f"  {row}")
    else:
        print("  No rows (table may be empty)")
except Exception as e:
    print(f"  users query failed: {e}")

print()

# 4. Check what column the PK actually uses
print("=== PRIMARY KEY COLUMN NAMES ===")
pk_tests = {
    "projects": ("project_id", "id"),
    "users": ("user_id", "id"),
    "schedules": ("schedule_id", "id"),
}
for table, (col1, col2) in pk_tests.items():
    try:
        r1 = client.table(table).select(col1).limit(1).execute()
        print(f"  {table}.{col1}: EXISTS (data={r1.data[:1]})")
    except Exception as e:
        print(f"  {table}.{col1}: FAILED - {e}")
    try:
        r2 = client.table(table).select(col2).limit(1).execute()
        print(f"  {table}.{col2}: EXISTS (data={r2.data[:1]})")
    except Exception as e:
        print(f"  {table}.{col2}: FAILED - {e}")

print("\n=== DONE ===")
