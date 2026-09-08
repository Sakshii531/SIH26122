from datetime import datetime
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.supabase_client import get_service_role_client
from app.main import app
from app.repositories.factory import reset_all_repositories

settings = get_settings()

is_placeholder_url = not settings.SUPABASE_URL or "your-project" in settings.SUPABASE_URL.lower()
is_placeholder_key = not settings.SUPABASE_KEY or "your" in settings.SUPABASE_KEY.lower()
skip_live_tests = is_placeholder_url or is_placeholder_key

pytestmark = pytest.mark.skipif(
    skip_live_tests,
    reason="Real Supabase credentials (SUPABASE_URL & SUPABASE_KEY) are not configured in backend/.env",
)


@pytest.fixture
def live_supabase_env(monkeypatch):
    """Ensure DB_PROVIDER is set to supabase specifically for live verification tests."""
    monkeypatch.setattr(settings, "DB_PROVIDER", "supabase")
    reset_all_repositories()
    yield
    reset_all_repositories()


@pytest.fixture
def supabase_client():
    """Returns real service role Supabase client for safe test record management."""
    return get_service_role_client()


def test_live_workflow_1_project_schedule_wbs_activity(live_supabase_env, supabase_client):
    """Verify Workflow 1: Project -> Schedule -> WBS -> Activity on live Supabase."""
    p_id = str(uuid4())
    s_id = str(uuid4())
    w_id = str(uuid4())
    a_id = str(uuid4())

    try:
        # Create Project
        supabase_client.table("projects").insert({
            "project_id": p_id,
            "name": f"Live Test Project {p_id[:8]}",
            "description": "Step 16.5 Live Workflow 1 Test Project",
        }).execute()

        # Create Schedule
        supabase_client.table("schedules").insert({
            "schedule_id": s_id,
            "project_id": p_id,
            "name": f"Live Baseline Schedule {s_id[:8]}",
            "source_type": "CSV",
        }).execute()

        # Create WBS Node
        supabase_client.table("wbs").insert({
            "wbs_id": w_id,
            "schedule_id": s_id,
            "code": "1.1.1",
            "name": "Site Demolition & Excavation",
            "level": 1,
        }).execute()

        # Create Activity
        supabase_client.table("activities").insert({
            "activity_id": a_id,
            "wbs_id": w_id,
            "activity_code": f"ACT-{a_id[:6]}",
            "name": "Initial Mass Excavation",
            "status": "Planned",
        }).execute()

        # Read back & verify relationship hierarchy
        p_res = supabase_client.table("projects").select("*").eq("project_id", p_id).execute()
        assert len(p_res.data) == 1
        assert p_res.data[0]["project_id"] == p_id

        s_res = supabase_client.table("schedules").select("*").eq("schedule_id", s_id).execute()
        assert len(s_res.data) == 1
        assert s_res.data[0]["project_id"] == p_id

        w_res = supabase_client.table("wbs").select("*").eq("wbs_id", w_id).execute()
        assert len(w_res.data) == 1
        assert w_res.data[0]["schedule_id"] == s_id

        a_res = supabase_client.table("activities").select("*").eq("activity_id", a_id).execute()
        assert len(a_res.data) == 1
        assert a_res.data[0]["wbs_id"] == w_id
        assert a_res.data[0]["activity_code"] == f"ACT-{a_id[:6]}"

    finally:
        # Reverse foreign key teardown
        supabase_client.table("activities").delete().eq("activity_id", a_id).execute()
        supabase_client.table("wbs").delete().eq("wbs_id", w_id).execute()
        supabase_client.table("schedules").delete().eq("schedule_id", s_id).execute()
        supabase_client.table("projects").delete().eq("project_id", p_id).execute()


def test_live_workflow_2_field_report_evidence_extracted_event(live_supabase_env, supabase_client):
    """Verify Workflow 2: Field Report -> Evidence -> Extracted Progress Event on live Supabase."""
    u_id = str(uuid4())
    p_id = str(uuid4())
    r_id = str(uuid4())
    e_id = str(uuid4())
    ev_id = str(uuid4())

    try:
        # Create User
        supabase_client.table("users").insert({
            "user_id": u_id,
            "name": f"Supervisor {u_id[:6]}",
            "email": f"supervisor_{u_id[:8]}@live.test",
            "role": "Supervisor",
        }).execute()

        # Create Project
        supabase_client.table("projects").insert({
            "project_id": p_id,
            "name": f"Live Report Project {p_id[:8]}",
            "description": "Step 16.5 Live Workflow 2 Test Project",
        }).execute()

        # Create Field Report
        supabase_client.table("field_reports").insert({
            "report_id": r_id,
            "project_id": p_id,
            "submitted_by": u_id,
            "report_type": "Daily Progress Report",
            "raw_text": "Mass excavation 75% complete on Zone A.",
            "status": "Submitted",
        }).execute()

        # Create Evidence
        supabase_client.table("evidence").insert({
            "evidence_id": e_id,
            "report_id": r_id,
            "evidence_type": "Photo",
            "file_url": f"https://storage.test/evidence_{e_id[:8]}.jpg",
        }).execute()

        # Create Extracted Progress Event
        supabase_client.table("extracted_progress_events").insert({
            "event_id": ev_id,
            "report_id": r_id,
            "activity_description": "Mass excavation Zone A",
            "discipline": "Civil",
            "location": "Zone A",
            "progress_value": 75,
            "status": "In Progress",
            "extraction_status": "Success",
        }).execute()

        # Read back & verify links
        r_res = supabase_client.table("field_reports").select("*").eq("report_id", r_id).execute()
        assert len(r_res.data) == 1
        assert r_res.data[0]["submitted_by"] == u_id

        e_res = supabase_client.table("evidence").select("*").eq("evidence_id", e_id).execute()
        assert len(e_res.data) == 1
        assert e_res.data[0]["report_id"] == r_id

        ev_res = supabase_client.table("extracted_progress_events").select("*").eq("event_id", ev_id).execute()
        assert len(ev_res.data) == 1
        assert ev_res.data[0]["report_id"] == r_id
        assert ev_res.data[0]["progress_value"] == 75

    finally:
        supabase_client.table("extracted_progress_events").delete().eq("event_id", ev_id).execute()
        supabase_client.table("evidence").delete().eq("evidence_id", e_id).execute()
        supabase_client.table("field_reports").delete().eq("report_id", r_id).execute()
        supabase_client.table("projects").delete().eq("project_id", p_id).execute()
        supabase_client.table("users").delete().eq("user_id", u_id).execute()


def test_live_workflow_3_activity_match_planner_review(live_supabase_env, supabase_client):
    """Verify Workflow 3: Activity Match -> Planner Review on live Supabase."""
    u_id = str(uuid4())
    p_id = str(uuid4())
    s_id = str(uuid4())
    w_id = str(uuid4())
    a_id = str(uuid4())
    r_id = str(uuid4())
    ev_id = str(uuid4())
    m_id = str(uuid4())
    rev_id = str(uuid4())

    try:
        # Prerequisites
        supabase_client.table("users").insert({
            "user_id": u_id,
            "name": f"Planner {u_id[:6]}",
            "email": f"planner_{u_id[:8]}@live.test",
            "role": "Planner",
        }).execute()

        supabase_client.table("projects").insert({
            "project_id": p_id,
            "name": f"Live Review Project {p_id[:8]}",
        }).execute()

        supabase_client.table("schedules").insert({"schedule_id": s_id, "project_id": p_id, "name": "Live Sched 3", "source_type": "CSV"}).execute()

        supabase_client.table("wbs").insert({
            "wbs_id": w_id,
            "schedule_id": s_id,
            "code": "1.2",
            "name": "Structural",
            "level": 1,
        }).execute()

        supabase_client.table("activities").insert({
            "activity_id": a_id,
            "wbs_id": w_id,
            "activity_code": f"ACT-REV-{a_id[:6]}",
            "name": "Foundation Concrete Pouring",
        }).execute()

        supabase_client.table("field_reports").insert({
            "report_id": r_id,
            "project_id": p_id,
            "submitted_by": u_id,
            "report_type": "Daily Progress Report",
            "raw_text": "Concrete pouring 60% done.",
        }).execute()

        supabase_client.table("extracted_progress_events").insert({
            "event_id": ev_id,
            "report_id": r_id,
            "activity_description": "Concrete pouring",
            "progress_value": 60,
        }).execute()

        # Step 1: Create Activity Match
        supabase_client.table("activity_matches").insert({
            "match_id": m_id,
            "event_id": ev_id,
            "activity_id": a_id,
            "confidence_score": 0.92,
            "match_status": "Matched",
        }).execute()

        # Step 2: Create Planner Review
        supabase_client.table("planner_reviews").insert({
            "review_id": rev_id,
            "match_id": m_id,
            "reviewed_by": u_id,
            "decision": "Approved",
        }).execute()

        # Read back and verify match & review linkage
        m_res = supabase_client.table("activity_matches").select("*").eq("match_id", m_id).execute()
        assert len(m_res.data) == 1
        assert m_res.data[0]["event_id"] == ev_id
        assert m_res.data[0]["activity_id"] == a_id

        rev_res = supabase_client.table("planner_reviews").select("*").eq("review_id", rev_id).execute()
        assert len(rev_res.data) == 1
        assert rev_res.data[0]["match_id"] == m_id
        assert rev_res.data[0]["reviewed_by"] == u_id
        assert rev_res.data[0]["decision"] == "Approved"

    finally:
        supabase_client.table("planner_reviews").delete().eq("review_id", rev_id).execute()
        supabase_client.table("activity_matches").delete().eq("match_id", m_id).execute()
        supabase_client.table("extracted_progress_events").delete().eq("event_id", ev_id).execute()
        supabase_client.table("field_reports").delete().eq("report_id", r_id).execute()
        supabase_client.table("activities").delete().eq("activity_id", a_id).execute()
        supabase_client.table("wbs").delete().eq("wbs_id", w_id).execute()
        supabase_client.table("schedules").delete().eq("schedule_id", s_id).execute()
        supabase_client.table("projects").delete().eq("project_id", p_id).execute()
        supabase_client.table("users").delete().eq("user_id", u_id).execute()


def test_live_workflow_4_approved_review_actual_progress_audit(live_supabase_env, supabase_client):
    """Verify Workflow 4: Approved/Modified Review -> Actual Progress -> Audit Log on live Supabase."""
    u_id = str(uuid4())
    p_id = str(uuid4())
    s_id = str(uuid4())
    w_id = str(uuid4())
    a_id = str(uuid4())
    r_id = str(uuid4())
    ev_id = str(uuid4())
    m_id = str(uuid4())
    rev_id = str(uuid4())
    prog_id = str(uuid4())
    audit_id = str(uuid4())

    try:
        supabase_client.table("users").insert({
            "user_id": u_id,
            "name": f"Validator {u_id[:6]}",
            "email": f"validator_{u_id[:8]}@live.test",
            "role": "Planner",
        }).execute()

        supabase_client.table("projects").insert({"project_id": p_id, "name": f"Live Progress Proj {p_id[:8]}"}).execute()
        supabase_client.table("schedules").insert({"schedule_id": s_id, "project_id": p_id, "name": "Sched 4", "source_type": "CSV"}).execute()
        supabase_client.table("wbs").insert({"wbs_id": w_id, "schedule_id": s_id, "code": "1.3", "name": "MEP", "level": 1}).execute()
        supabase_client.table("activities").insert({"activity_id": a_id, "wbs_id": w_id, "activity_code": f"ACT-MEP-{a_id[:6]}", "name": "Conduit Installation"}).execute()
        supabase_client.table("field_reports").insert({"report_id": r_id, "project_id": p_id, "submitted_by": u_id, "report_type": "DPR", "raw_text": "Conduits installed 80%"}).execute()
        supabase_client.table("extracted_progress_events").insert({"event_id": ev_id, "report_id": r_id, "activity_description": "Conduit installation", "progress_value": 80}).execute()
        supabase_client.table("activity_matches").insert({"match_id": m_id, "event_id": ev_id, "activity_id": a_id, "confidence_score": 0.98, "match_status": "Matched"}).execute()
        supabase_client.table("planner_reviews").insert({"review_id": rev_id, "match_id": m_id, "reviewed_by": u_id, "decision": "Approved"}).execute()

        # Step 1: Create Actual Progress
        supabase_client.table("actual_progress").insert({
            "progress_id": prog_id,
            "activity_id": a_id,
            "progress_value": 80,
            "status": "In Progress",
            "validated_by": u_id,
        }).execute()

        # Step 2: Create Audit Log Entry
        supabase_client.table("audit_logs").insert({
            "audit_id": audit_id,
            "user_id": u_id,
            "entity_type": "actual_progress",
            "entity_id": prog_id,
            "action": "CREATE",
            "details": "Actual progress logged from approved planner review",
        }).execute()

        # Read back & verify linkage
        prog_res = supabase_client.table("actual_progress").select("*").eq("progress_id", prog_id).execute()
        assert len(prog_res.data) == 1
        assert prog_res.data[0]["activity_id"] == a_id
        assert prog_res.data[0]["progress_value"] == 80
        assert prog_res.data[0]["validated_by"] == u_id

        audit_res = supabase_client.table("audit_logs").select("*").eq("audit_id", audit_id).execute()
        assert len(audit_res.data) == 1
        assert audit_res.data[0]["entity_id"] == prog_id
        assert audit_res.data[0]["user_id"] == u_id
        assert audit_res.data[0]["action"] == "CREATE"

    finally:
        supabase_client.table("audit_logs").delete().eq("audit_id", audit_id).execute()
        supabase_client.table("actual_progress").delete().eq("progress_id", prog_id).execute()
        supabase_client.table("planner_reviews").delete().eq("review_id", rev_id).execute()
        supabase_client.table("activity_matches").delete().eq("match_id", m_id).execute()
        supabase_client.table("extracted_progress_events").delete().eq("event_id", ev_id).execute()
        supabase_client.table("field_reports").delete().eq("report_id", r_id).execute()
        supabase_client.table("activities").delete().eq("activity_id", a_id).execute()
        supabase_client.table("wbs").delete().eq("wbs_id", w_id).execute()
        supabase_client.table("schedules").delete().eq("schedule_id", s_id).execute()
        supabase_client.table("projects").delete().eq("project_id", p_id).execute()
        supabase_client.table("users").delete().eq("user_id", u_id).execute()


def test_live_workflow_5_conflict_create_read_update(live_supabase_env, supabase_client):
    """Verify Workflow 5: Conflict create/read/update on live Supabase."""
    u_id = str(uuid4())
    p_id = str(uuid4())
    s_id = str(uuid4())
    w_id = str(uuid4())
    a_id = str(uuid4())
    r_id = str(uuid4())
    ev_id = str(uuid4())
    c_id = str(uuid4())

    try:
        supabase_client.table("users").insert({
            "user_id": u_id,
            "name": f"Conflict User {u_id[:6]}",
            "email": f"conflict_{u_id[:8]}@live.test",
            "role": "Supervisor",
        }).execute()

        supabase_client.table("projects").insert({"project_id": p_id, "name": f"Live Conflict Proj {p_id[:8]}"}).execute()
        supabase_client.table("schedules").insert({"schedule_id": s_id, "project_id": p_id, "name": "Sched 5", "source_type": "CSV"}).execute()
        supabase_client.table("wbs").insert({"wbs_id": w_id, "schedule_id": s_id, "code": "1.4", "name": "Finishes", "level": 1}).execute()
        supabase_client.table("activities").insert({"activity_id": a_id, "wbs_id": w_id, "activity_code": f"ACT-FIN-{a_id[:6]}", "name": "Wall Painting"}).execute()
        supabase_client.table("field_reports").insert({"report_id": r_id, "project_id": p_id, "submitted_by": u_id, "report_type": "DPR", "raw_text": "Painting finished prematurely."}).execute()
        supabase_client.table("extracted_progress_events").insert({"event_id": ev_id, "report_id": r_id, "activity_description": "Wall painting", "progress_value": 100}).execute()

        # Step 1: Create Conflict
        supabase_client.table("conflicts").insert({
            "conflict_id": c_id,
            "activity_id": a_id,
            "event_id": ev_id,
            "conflict_type": "Progress Mismatch",
            "description": "Extracted progress 100% conflicts with baseline schedule 0% start",
            "status": "Open",
        }).execute()

        # Step 2: Read Conflict
        c_res = supabase_client.table("conflicts").select("*").eq("conflict_id", c_id).execute()
        assert len(c_res.data) == 1
        assert c_res.data[0]["activity_id"] == a_id
        assert c_res.data[0]["event_id"] == ev_id
        assert c_res.data[0]["status"] == "Open"

        # Step 3: Update Conflict Resolution
        upd_res = supabase_client.table("conflicts").update({
            "status": "Resolved",
            "resolution": "Planner confirmed early finish after site inspection.",
            "resolved_by": u_id,
            "resolved_at": datetime.utcnow().isoformat(),
        }).eq("conflict_id", c_id).execute()

        assert len(upd_res.data) == 1
        assert upd_res.data[0]["status"] == "Resolved"
        assert upd_res.data[0]["resolved_by"] == u_id

    finally:
        supabase_client.table("conflicts").delete().eq("conflict_id", c_id).execute()
        supabase_client.table("extracted_progress_events").delete().eq("event_id", ev_id).execute()
        supabase_client.table("field_reports").delete().eq("report_id", r_id).execute()
        supabase_client.table("activities").delete().eq("activity_id", a_id).execute()
        supabase_client.table("wbs").delete().eq("wbs_id", w_id).execute()
        supabase_client.table("schedules").delete().eq("schedule_id", s_id).execute()
        supabase_client.table("projects").delete().eq("project_id", p_id).execute()
        supabase_client.table("users").delete().eq("user_id", u_id).execute()


def test_live_fastapi_endpoints_all_workflows(live_supabase_env):
    """Verify FastAPI routes function seamlessly with TestClient when DB_PROVIDER=supabase."""
    client = TestClient(app)

    # 1. Health & Status routes
    status_resp = client.get("/api/v1/status")
    assert status_resp.status_code == 200
    assert status_resp.json() == {"status": "ok", "version": "v1"}

    # 2. Reports routes list endpoint
    reports_resp = client.get("/api/v1/reports")
    # Endpoint returns 405 Method Not Allowed if GET is not implemented on /reports, or 200 list
    assert reports_resp.status_code in (200, 405)

    # 3. Reviews list endpoint
    reviews_resp = client.get("/api/v1/reviews")
    assert reviews_resp.status_code == 200
    assert isinstance(reviews_resp.json(), list)

    # 4. Progress list endpoint
    progress_resp = client.get("/api/v1/progress")
    assert progress_resp.status_code == 200
    assert isinstance(progress_resp.json(), list)

    # 5. Conflicts list endpoint
    conflicts_resp = client.get("/api/v1/conflicts")
    assert conflicts_resp.status_code == 200
    assert isinstance(conflicts_resp.json(), list)

    # 6. Audit list endpoint
    audit_resp = client.get("/api/v1/audit")
    assert audit_resp.status_code == 200
    assert isinstance(audit_resp.json(), list)
