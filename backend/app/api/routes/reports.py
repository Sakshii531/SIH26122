from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.enums import FieldReportFormat
from app.schemas.field_report import FieldReportCreate, FieldReportResponse
from app.services.field_report_service import FieldReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=FieldReportResponse, status_code=201)
async def create_text_report(payload: FieldReportCreate) -> FieldReportResponse:
    """Submit a structured text or metadata field progress report."""
    return FieldReportService.process_text_report(payload)


@router.post("/upload", response_model=FieldReportResponse, status_code=201)
async def upload_field_report(
    file: UploadFile = File(..., description="Document (PDF/DOCX), audio (MP3/WAV), spreadsheet (XLSX/CSV), or image file"),
    reporter_id: str = Form(..., description="ID or name of field reporter/supervisor"),
    project_id: Optional[UUID] = Form(None, description="Optional target project UUID"),
    discipline: Optional[str] = Form(None, description="Optional engineering discipline"),
    location: Optional[str] = Form(None, description="Optional site location"),
    source_format: Optional[FieldReportFormat] = Form(None, description="Optional explicit source format"),
) -> FieldReportResponse:
    """Upload a file or audio recording as a field progress report."""
    content = await file.read()
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
