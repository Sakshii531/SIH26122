from uuid import uuid4
from datetime import datetime, date
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
from app.schemas.project import ProjectCreate
from app.schemas.schedule import ScheduleCreate
from app.schemas.wbs import WBSCreate
from app.schemas.activity import ScheduleActivityCreate
from app.schemas.field_report import FieldReportCreate
from app.schemas.evidence import EvidenceCreate
from app.schemas.extracted_progress_event import ExtractedProgressEventCreate
from app.schemas.activity_match import ActivityMatchCreate
from app.schemas.review_workflow import ReviewItemCreate
from app.schemas.conflict import ConflictCreate
from app.schemas.audit_log import AuditEventCreate
from app.schemas.user import UserCreate

client = get_service_role_client()

print("Testing all 5 Flows against live Supabase...")

# Flow 1: Project -> Schedule -> WBS -> Activity
print("\n--- Flow 1: Project -> Schedule -> WBS -> Activity ---")
proj_repo = SupabaseProjectRepository(client=client)
sched_repo = SupabaseScheduleRepository(client=client)
wbs_repo = SupabaseWBSRepository(client=client)
act_repo = SupabaseActivityRepository(client=client)

p_id = uuid4()
s_id = uuid4()
w_id = uuid4()
a_id = uuid4()

print("Creating Project...")
p_created = proj_repo.create(ProjectCreate(name=f"Flow1 Project {uuid4().hex[:6]}", code="F1-001"))
print("Created Project:", p_created.id)

print("Creating Schedule...")
s_created = sched_repo.create(ScheduleCreate(project_id=p_created.id, name="Flow1 Schedule"))
print("Created Schedule:", s_created.id)

print("Creating WBS...")
w_created = wbs_repo.create(WBSCreate(schedule_id=s_created.id, wbs_code="1.1", wbs_name="Foundation", level=1))
print("Created WBS:", w_created.id)

print("Creating Activity...")
a_created = act_repo.create(ScheduleActivityCreate(
    project_id=p_created.id,
    schedule_id=s_created.id,
    wbs_id=w_created.id,
    activity_code="ACT-F1",
    name="Excavation Flow 1",
))
print("Created Activity:", a_created.id)

# Cleanup Flow 1
print("Cleaning up Flow 1...")
act_repo.delete(a_created.id)
wbs_repo.delete(w_created.id)
sched_repo.delete(s_created.id)
proj_repo.delete(p_created.id)
print("Flow 1 Cleanup complete!")
