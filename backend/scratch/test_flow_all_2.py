from uuid import uuid4
from datetime import datetime, date
from app.db.supabase_client import get_service_role_client
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.schemas.wbs import WBSCreate, WBSResponse, WBSUpdate
from app.schemas.activity import ScheduleActivityCreate, ScheduleActivityResponse, ScheduleActivityUpdate
from app.schemas.field_report import FieldReportCreate, FieldReportResponse
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.schemas.extracted_progress_event import ExtractedProgressEventCreate, ExtractedProgressEventResponse
from app.schemas.activity_match import ActivityMatchCreate, ActivityMatchResponse
from app.schemas.review_workflow import ReviewItemCreate, ReviewItemResponse
from app.schemas.conflict import ConflictCreate, ConflictResponse, ConflictUpdate
from app.schemas.progress_event import ProgressEventResponse
from app.schemas.audit_log import AuditEventCreate, AuditEventResponse
from app.schemas.enums import ProgressStatus, ReviewStatus, MatchStatus

client = get_service_role_client()

print("Testing raw table operations for 5 flows against Supabase...")

# Flow 1: Project -> Schedule -> WBS -> Activity
print("\n--- Flow 1: Project -> Schedule -> WBS -> Activity ---")
p_id = str(uuid4())
s_id = str(uuid4())
w_id = str(uuid4())
a_id = str(uuid4())

client.table("projects").insert({"project_id": p_id, "name": "Flow 1 Project", "description": "Flow 1 Test"}).execute()
client.table("schedules").insert({"schedule_id": s_id, "project_id": p_id, "name": "Baseline Sched", "source_type": "CSV"}).execute()
client.table("wbs").insert({"wbs_id": w_id, "schedule_id": s_id, "code": "1.1", "name": "Foundation", "level": 1}).execute()
client.table("activities").insert({"activity_id": a_id, "wbs_id": w_id, "activity_code": "ACT-001", "name": "Excavation", "status": "Planned"}).execute()

# Read Flow 1
p_res = client.table("projects").select("*").eq("project_id", p_id).execute()
s_res = client.table("schedules").select("*").eq("project_id", p_id).execute()
w_res = client.table("wbs").select("*").eq("schedule_id", s_id).execute()
a_res = client.table("activities").select("*").eq("wbs_id", w_id).execute()

print("Project read:", p_res.data[0]["name"])
print("Schedule read:", s_res.data[0]["name"])
print("WBS read:", w_res.data[0]["name"])
print("Activity read:", a_res.data[0]["name"])

# Flow 2: Field Report -> Evidence -> Extracted Progress Event
print("\n--- Flow 2: Field Report -> Evidence -> Extracted Progress Event ---")
r_id = str(uuid4())
e_id = str(uuid4())
ev_id = str(uuid4())

client.table("field_reports").insert({"report_id": r_id, "project_id": p_id, "report_type": "TEXT", "raw_text": "Completed excavation", "status": "Submitted"}).execute()
client.table("evidence").insert({"evidence_id": e_id, "report_id": r_id, "evidence_type": "Photo", "file_url": "http://example.com/site.jpg"}).execute()
client.table("extracted_progress_events").insert({"event_id": ev_id, "report_id": r_id, "activity_description": "Excavation", "progress_value": 50, "status": "In Progress"}).execute()

r_res = client.table("field_reports").select("*").eq("report_id", r_id).execute()
e_res = client.table("evidence").select("*").eq("report_id", r_id).execute()
ev_res = client.table("extracted_progress_events").select("*").eq("report_id", r_id).execute()

print("Report read:", r_res.data[0]["raw_text"])
print("Evidence read:", e_res.data[0]["file_url"])
print("Extracted Event read:", ev_res.data[0]["activity_description"])

# Flow 3: Activity Match -> Planner Review
print("\n--- Flow 3: Activity Match -> Planner Review ---")
m_id = str(uuid4())
rev_id = str(uuid4())

client.table("activity_matches").insert({"match_id": m_id, "event_id": ev_id, "activity_id": a_id, "confidence_score": 0.95, "match_status": "Matched"}).execute()
client.table("planner_reviews").insert({"review_id": rev_id, "match_id": m_id, "decision": "Approved"}).execute()

m_res = client.table("activity_matches").select("*").eq("match_id", m_id).execute()
rev_res = client.table("planner_reviews").select("*").eq("review_id", rev_id).execute()

print("Match read:", m_res.data[0]["confidence_score"])
print("Review read:", rev_res.data[0]["decision"])

# Flow 4: Approved Review -> Actual Progress -> Audit Log
print("\n--- Flow 4: Approved Review -> Actual Progress -> Audit Log ---")
prog_id = str(uuid4())
audit_id = str(uuid4())

client.table("actual_progress").insert({"progress_id": prog_id, "activity_id": a_id, "progress_value": 50, "status": "In Progress"}).execute()
client.table("audit_logs").insert({"audit_id": audit_id, "entity_type": "actual_progress", "entity_id": prog_id, "action": "CREATE", "details": "Progress event logged"}).execute()

prog_res = client.table("actual_progress").select("*").eq("progress_id", prog_id).execute()
audit_res = client.table("audit_logs").select("*").eq("audit_id", audit_id).execute()

print("Actual Progress read:", prog_res.data[0]["progress_value"])
print("Audit Log read:", audit_res.data[0]["action"])

# Flow 5: Conflict Creation / Read
print("\n--- Flow 5: Conflict Creation / Read ---")
c_id = str(uuid4())

client.table("conflicts").insert({"conflict_id": c_id, "activity_id": a_id, "event_id": ev_id, "conflict_type": "Mismatch", "description": "Date conflict", "status": "Open"}).execute()
c_res = client.table("conflicts").select("*").eq("conflict_id", c_id).execute()

print("Conflict read:", c_res.data[0]["description"])

# Cleanup all flow test records in reverse order
print("\n--- Cleaning up all flow records ---")
client.table("conflicts").delete().eq("conflict_id", c_id).execute()
client.table("audit_logs").delete().eq("audit_id", audit_id).execute()
client.table("actual_progress").delete().eq("progress_id", prog_id).execute()
client.table("planner_reviews").delete().eq("review_id", rev_id).execute()
client.table("activity_matches").delete().eq("match_id", m_id).execute()
client.table("extracted_progress_events").delete().eq("event_id", ev_id).execute()
client.table("evidence").delete().eq("evidence_id", e_id).execute()
client.table("field_reports").delete().eq("report_id", r_id).execute()
client.table("activities").delete().eq("activity_id", a_id).execute()
client.table("wbs").delete().eq("wbs_id", w_id).execute()
client.table("schedules").delete().eq("schedule_id", s_id).execute()
client.table("projects").delete().eq("project_id", p_id).execute()
print("Cleanup complete!")
