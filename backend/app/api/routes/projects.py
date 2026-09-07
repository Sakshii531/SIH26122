from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory store for projects
_projects_db: Dict[UUID, ProjectResponse] = {}


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(payload: ProjectCreate) -> ProjectResponse:
    """Create a new project entry."""
    pid = uuid4()
    resp = ProjectResponse(
        id=pid,
        name=payload.name,
        code=payload.code,
        description=payload.description,
        location=payload.location,
    )
    _projects_db[pid] = resp
    return resp


@router.get("", response_model=List[ProjectResponse])
async def list_projects() -> List[ProjectResponse]:
    """List all projects."""
    return list(_projects_db.values())


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID) -> ProjectResponse:
    """Retrieve a project by UUID."""
    if project_id not in _projects_db:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    return _projects_db[project_id]
