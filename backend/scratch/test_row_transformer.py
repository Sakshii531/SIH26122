from uuid import uuid4
from datetime import datetime, date
from app.db.supabase_client import get_service_role_client
from app.schemas.project import ProjectCreate, ProjectResponse

client = get_service_role_client()

print("Testing Project insert and read...")
p_id = str(uuid4())
p_data = {
    "project_id": p_id,
    "name": "Live Integration Test Project",
    "description": "Created for Step 16.5 live integration flow",
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
}
res = client.table("projects").insert(p_data).execute()
print("Insert project result:", res.data)

# Read back
row = res.data[0]
row["id"] = row["project_id"]
row["code"] = "PROJ-TEST"
p_resp = ProjectResponse.model_validate(row)
print("ProjectResponse parsed successfully:", p_resp.id, p_resp.name)

# Cleanup
client.table("projects").delete().eq("project_id", p_id).execute()
print("Project cleaned up!")
