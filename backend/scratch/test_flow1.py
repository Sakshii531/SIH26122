from uuid import uuid4
from datetime import datetime
from app.core.config import get_settings
from app.db.supabase_client import get_service_role_client
from app.repositories.supabase_repos import (
    SupabaseProjectRepository,
    SupabaseScheduleRepository,
    SupabaseWBSRepository,
    SupabaseActivityRepository,
)

client = get_service_role_client()

project_repo = SupabaseProjectRepository(client=client)
schedule_repo = SupabaseScheduleRepository(client=client)
wbs_repo = SupabaseWBSRepository(client=client)
activity_repo = SupabaseActivityRepository(client=client)

print("--- Testing Flow 1: Project -> Schedule -> WBS -> Activity ---")

# 1. Read existing data
projects = project_repo.list_all()
print(f"Projects found: {len(projects)}")
for p in projects:
    print(f"  Project: id={p.id}, name={p.name}")
    schedules = schedule_repo.list_by_project(p.id)
    print(f"    Schedules found: {len(schedules)}")
    for s in schedules:
        print(f"      Schedule: id={s.id}, name={s.name}")
        wbs_items = wbs_repo.list_by_schedule(s.id)
        print(f"        WBS items found: {len(wbs_items)}")
        for w in wbs_items:
            print(f"          WBS: id={w.id}, code={w.code}, name={w.name}")
    activities = activity_repo.list_by_project(p.id)
    print(f"    Activities found: {len(activities)}")
    for a in activities:
        print(f"      Activity: id={a.id}, code={a.activity_code}, name={a.name}")
