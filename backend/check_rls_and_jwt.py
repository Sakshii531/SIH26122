"""
Phase 2 diagnostic: query RLS via pg_catalog using rpc/raw-sql,
and probe anon-key RLS enforcement empirically.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.db.supabase_client import get_service_role_client, get_supabase_client, reset_clients
reset_clients()

svc = get_service_role_client()
anon = get_supabase_client()

tables = [
    "users","projects","schedules","wbs","activities",
    "field_reports","evidence","extracted_progress_events",
    "activity_matches","planner_reviews","actual_progress",
    "audit_logs","conflicts",
]

print("=== RLS ENFORCEMENT TEST (anon key vs service role key) ===")
print("Tables accessible with anon key (no auth header):\n")

for t in tables:
    try:
        r_anon = anon.table(t).select("*").limit(1).execute()
        anon_count = len(r_anon.data) if r_anon.data else 0
        anon_status = f"OK ({anon_count} rows visible)"
    except Exception as e:
        anon_status = f"BLOCKED - {str(e)[:80]}"

    try:
        r_svc = svc.table(t).select("*").limit(1).execute()
        svc_count = len(r_svc.data) if r_svc.data else 0
        svc_status = f"OK ({svc_count} rows visible)"
    except Exception as e:
        svc_status = f"ERROR - {str(e)[:80]}"

    rls_enforced = "RLS active" if "BLOCKED" in anon_status and "OK" in svc_status else "open (no RLS)"
    print(f"  {t:<35} anon={anon_status:<25} svc={svc_status:<25} → {rls_enforced}")

print()

# Test actual anon insert block
print("=== INSERT BLOCK TEST (anon key on users table) ===")
import uuid
fake_id = str(uuid.uuid4())
try:
    r = anon.table("users").insert({
        "user_id": fake_id,
        "name": "RLS Test Probe",
        "email": f"probe_{fake_id[:8]}@test.local",
        "role": "Supervisor",
    }).execute()
    if r.data:
        print(f"  WARN: Anon insert SUCCEEDED on users table — RLS NOT enforced for INSERT")
        # Clean up
        svc.table("users").delete().eq("user_id", fake_id).execute()
        print(f"  (test record cleaned up)")
    else:
        print(f"  Anon insert returned no data (may be blocked)")
except Exception as e:
    print(f"  Anon insert BLOCKED (expected): {str(e)[:120]}")

print()
print("=== SUPABASE AUTH USERS (auth.uid() mapping) ===")
print("Users table auth_user_id → maps to Supabase auth.users.id:")
try:
    r = svc.table("users").select("user_id,name,email,role,auth_user_id").execute()
    for row in (r.data or []):
        print(f"  user_id={row['user_id'][:8]}..  auth_user_id={row.get('auth_user_id','NULL')}  role={row['role']}  email={row['email']}")
except Exception as e:
    print(f"  Failed: {e}")

print("\n=== DONE ===")
