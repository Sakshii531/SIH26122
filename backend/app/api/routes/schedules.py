from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.schedule_import import ScheduleImportSummaryResponse
from app.services.schedule_ingestion_service import ScheduleIngestionService

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("/import", response_model=ScheduleImportSummaryResponse)
async def import_schedule(
    file: UploadFile = File(..., description="Excel (.xlsx, .xls) or CSV schedule file"),
    project_id: Optional[UUID] = Form(None, description="Optional target project UUID"),
) -> ScheduleImportSummaryResponse:
    """Import and validate schedule activities from an uploaded Excel or CSV file."""
    content = await file.read()
    filename = file.filename or "uploaded_schedule.csv"
    return ScheduleIngestionService.parse_and_validate_schedule(
        file_bytes=content,
        filename=filename,
        project_id=project_id,
    )
