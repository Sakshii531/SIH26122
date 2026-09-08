from __future__ import annotations

from typing import Dict, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import AuthUser, get_current_user, require_planner
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory store for projects
_projects_db: Dict[UUID, ProjectResponse] = {}


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    payload: ProjectCreate,
    _user: AuthUser = Depends(require_planner),
) -> ProjectResponse:
    """Create a new project entry. Requires PLANNER or ADMIN."""
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
async def list_projects(
    _user: AuthUser = Depends(get_current_user),
) -> List[ProjectResponse]:
    """List all projects. Requires authentication."""
    return list(_projects_db.values())


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    _user: AuthUser = Depends(get_current_user),
) -> ProjectResponse:
    """Retrieve a project by UUID. Requires authentication."""
    if project_id not in _projects_db:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    return _projects_db[project_id]
