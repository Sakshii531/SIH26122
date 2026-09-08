from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.auth import AuthUser, require_supervisor
from app.core.config import get_settings
from app.core.uploads import read_upload_with_limit
from app.schemas.ai_contract import (
    ActivityMatchingRequest,
    ActivityMatchingResponse,
    FieldReportExtractionRequest,
    FieldReportExtractionResponse,
)
from app.schemas.enums import FieldReportFormat
from app.schemas.field_report import FieldReportCreate, FieldReportResponse
from app.services.ai_integration_service import AIIntegrationService
from app.services.field_report_service import FieldReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=FieldReportResponse, status_code=201)
async def create_text_report(
    payload: FieldReportCreate,
    _user: AuthUser = Depends(require_supervisor),
) -> FieldReportResponse:
    """Submit a structured text or metadata field progress report. Requires SUPERVISOR, PLANNER, or ADMIN."""
    return FieldReportService.process_text_report(payload)


@router.post("/upload", response_model=FieldReportResponse, status_code=201)
async def upload_field_report(
    file: UploadFile = File(..., description="Document (PDF/DOCX), audio (MP3/WAV), spreadsheet (XLSX/CSV), or image file"),
    reporter_id: str = Form(..., description="ID or name of field reporter/supervisor"),
    project_id: Optional[UUID] = Form(None, description="Optional target project UUID"),
    discipline: Optional[str] = Form(None, description="Optional engineering discipline"),
    location: Optional[str] = Form(None, description="Optional site location"),
    source_format: Optional[FieldReportFormat] = Form(None, description="Optional explicit source format"),
    _user: AuthUser = Depends(require_supervisor),
) -> FieldReportResponse:
    """Upload a file or audio recording as a field progress report. Requires SUPERVISOR, PLANNER, or ADMIN."""
    max_bytes = get_settings().MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await read_upload_with_limit(file, max_bytes)
    filename = file.filename or "uploaded_report.bin"
    return FieldReportService.process_file_report(
        file_bytes=content,
        filename=filename,
        content_type=file.content_type,
        reporter_id=reporter_id,
        project_id=project_id,
        discipline=discipline,
        location=location,
        user_format=source_format,
    )


@router.post("/{report_id}/extraction", response_model=FieldReportExtractionResponse)
async def extract_report(
    report_id: UUID,
    payload: FieldReportExtractionRequest,
    _user: AuthUser = Depends(require_supervisor),
) -> FieldReportExtractionResponse:
    """AI contract endpoint to trigger extraction from a field report. Requires SUPERVISOR, PLANNER, or ADMIN."""
    return AIIntegrationService.extract_report_data(report_id, payload)


@router.post("/{report_id}/matching", response_model=ActivityMatchingResponse)
async def match_report_activity(
    report_id: UUID,
    payload: ActivityMatchingRequest,
    _user: AuthUser = Depends(require_supervisor),
) -> ActivityMatchingResponse:
    """AI contract endpoint to match extracted report info to schedule activities. Requires SUPERVISOR, PLANNER, or ADMIN."""
    return AIIntegrationService.match_activity(report_id, payload)
