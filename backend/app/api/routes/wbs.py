from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query

from app.schemas.wbs import WBSCreate, WBSResponse
from app.services.schedule_ingestion_service import ScheduleIngestionService

router = APIRouter(prefix="/wbs", tags=["wbs"])


@router.get("", response_model=List[WBSResponse])
async def list_wbs_nodes(
    schedule_id: Optional[UUID] = Query(None, description="Optional schedule UUID filter"),
) -> List[WBSResponse]:
    """List Work Breakdown Structure (WBS) nodes."""
    return []
