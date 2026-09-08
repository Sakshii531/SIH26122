from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.auth import AuthUser, require_planner
from app.schemas.activity import ActivityResponse

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=List[ActivityResponse])
async def list_activities(
    project_id: Optional[UUID] = Query(None, description="Optional project UUID filter"),
    schedule_id: Optional[UUID] = Query(None, description="Optional schedule UUID filter"),
    wbs_id: Optional[UUID] = Query(None, description="Optional WBS node UUID filter"),
    _user: AuthUser = Depends(require_planner),
) -> List[ActivityResponse]:
    """List schedule activities. Requires PLANNER or ADMIN."""
    return []
