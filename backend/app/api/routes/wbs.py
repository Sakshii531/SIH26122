from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.auth import AuthUser, require_planner
from app.schemas.wbs import WBSResponse

router = APIRouter(prefix="/wbs", tags=["wbs"])


@router.get("", response_model=List[WBSResponse])
async def list_wbs_nodes(
    schedule_id: Optional[UUID] = Query(None, description="Optional schedule UUID filter"),
    _user: AuthUser = Depends(require_planner),
) -> List[WBSResponse]:
    """List Work Breakdown Structure (WBS) nodes. Requires PLANNER or ADMIN."""
    return []
