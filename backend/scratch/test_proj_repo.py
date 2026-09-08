from uuid import uuid4
from datetime import datetime
from app.db.supabase_client import get_service_role_client
from app.repositories.supabase_repos import SupabaseProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate

client = get_service_role_client()
repo = SupabaseProjectRepository(client=client)

print("Creating Project via SupabaseProjectRepository...")
p = repo.create(ProjectCreate(name=f"Test Project {uuid4().hex[:6]}", code="PRJ-TEST-1"))
print("Created:", p.id, p.name, p.code)

print("Fetching Project by ID...")
fetched = repo.get_by_id(p.id)
print("Fetched:", fetched.id, fetched.name if fetched else None)

print("Updating Project...")
updated = repo.update(p.id, ProjectUpdate(name=f"{p.name} Updated"))
print("Updated:", updated.name if updated else None)

print("Listing all Projects...")
all_projs = repo.list_all()
print(f"Total projects in list_all: {len(all_projs)}")

print("Deleting created project...")
deleted = repo.delete(p.id)
print("Deleted:", deleted)
