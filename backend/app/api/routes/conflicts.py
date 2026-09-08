from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.auth import AuthUser, require_planner
from app.schemas.conflict import ConflictCreate, ConflictResponse, ConflictUpdate
from app.services.conflict_service import ConflictService

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


@router.post("", response_model=ConflictResponse, status_code=201)
async def create_conflict(
    payload: ConflictCreate,
    _user: AuthUser = Depends(require_planner),
) -> ConflictResponse:
    """Record a detected conflict between progress events. Requires PLANNER or ADMIN."""
    return ConflictService.create_conflict(payload)


@router.get("", response_model=List[ConflictResponse])
async def list_conflicts(
    event_id: Optional[UUID] = Query(None, description="Optional filter by progress event UUID"),
    status: Optional[str] = Query(None, description="Optional resolution status filter"),
    _user: AuthUser = Depends(require_planner),
) -> List[ConflictResponse]:
    """List conflicts with optional filters. Requires PLANNER or ADMIN."""
    return ConflictService.list_conflicts(event_id=event_id, resolution_status=status)


@router.get("/{conflict_id}", response_model=ConflictResponse)
async def get_conflict(
    conflict_id: UUID,
    _user: AuthUser = Depends(require_planner),
) -> ConflictResponse:
    """Retrieve a conflict by UUID. Requires PLANNER or ADMIN."""
    return ConflictService.get_conflict(conflict_id)


@router.patch("/{conflict_id}", response_model=ConflictResponse)
async def update_conflict(
    conflict_id: UUID,
    payload: ConflictUpdate,
    _user: AuthUser = Depends(require_planner),
) -> ConflictResponse:
    """Update conflict resolution details. Requires PLANNER or ADMIN."""
    return ConflictService.update_conflict(conflict_id, payload)
