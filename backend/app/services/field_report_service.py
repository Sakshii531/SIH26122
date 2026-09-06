from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.schemas.enums import FieldReportFormat
from app.schemas.field_report import EvidenceItem, FieldReportCreate, FieldReportResponse


class FieldReportService:
    """Service handling field progress report ingestion and normalization."""

    ALLOWED_EXTENSIONS: Dict[FieldReportFormat, Set[str]] = {
        FieldReportFormat.DPR: {"pdf", "doc", "docx"},
        FieldReportFormat.TEXT: {"txt"},
        FieldReportFormat.EXCEL: {"xlsx", "xls", "csv"},
        FieldReportFormat.VOICE: {"mp3", "wav", "m4a", "ogg", "aac", "flac"},
        FieldReportFormat.PHOTO: {"jpg", "jpeg", "png", "webp"},
    }

    ALL_ALLOWED_EXTENSIONS: Set[str] = {
        ext for ext_set in ALLOWED_EXTENSIONS.values() for ext in ext_set
    }

    @classmethod
    def process_text_report(cls, payload: FieldReportCreate) -> FieldReportResponse:
        """Validate and normalize a structured text/metadata field report."""
        reporter_id = (payload.reporter_id or "").strip()
        if not reporter_id:
            raise HTTPException(status_code=400, detail="Reporter ID is required.")

        raw_content = (payload.raw_content or "").strip()
        if not raw_content:
            raise HTTPException(status_code=400, detail="Report text content cannot be empty.")

        project_id = payload.project_id or uuid4()
        report_id = uuid4()
        now = datetime.utcnow()

        return FieldReportResponse(
            id=report_id,
            project_id=project_id,
            source_format=payload.source_format or FieldReportFormat.TEXT,
            reporter_id=reporter_id,
            raw_content=raw_content,
            discipline=payload.discipline,
            location=payload.location,
            evidence=payload.evidence or [],
            created_at=now,
        )

    @classmethod
    def process_file_report(
        cls,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str],
        reporter_id: str,
        project_id: Optional[UUID] = None,
        discipline: Optional[str] = None,
        location: Optional[str] = None,
        user_format: Optional[FieldReportFormat] = None,
    ) -> FieldReportResponse:
        """Validate file format, generate evidence item, and normalize file/audio field report."""
        clean_reporter_id = (reporter_id or "").strip()
        if not clean_reporter_id:
            raise HTTPException(status_code=400, detail="Reporter ID is required.")

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        ext = filename.lower().split(".")[-1] if "." in filename else ""
        if ext not in cls.ALL_ALLOWED_EXTENSIONS:
            allowed_fmt_str = ", ".join(sorted(cls.ALL_ALLOWED_EXTENSIONS))
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '.{ext}'. Allowed extensions: {allowed_fmt_str}",
            )

        detected_format = user_format or cls._detect_format_from_extension(ext)
        target_project_id = project_id or uuid4()
        report_id = uuid4()
        now = datetime.utcnow()

        # Attempt decoding text for plain text files
        raw_content = f"[File Upload: {filename} ({len(file_bytes)} bytes)]"
        if ext == "txt":
            try:
                decoded = file_bytes.decode("utf-8").strip()
                if decoded:
                    raw_content = decoded
            except Exception:
                pass

        evidence_item = EvidenceItem(
            id=uuid4(),
            file_name=filename,
            file_url=f"/storage/reports/{report_id}/{filename}",
            mime_type=content_type or f"application/{ext}",
            description=f"Field report file ({detected_format.value})",
        )

        return FieldReportResponse(
            id=report_id,
            project_id=target_project_id,
            source_format=detected_format,
            reporter_id=clean_reporter_id,
            raw_content=raw_content,
            discipline=discipline,
            location=location,
            evidence=[evidence_item],
            created_at=now,
        )

    @classmethod
    def _detect_format_from_extension(cls, ext: str) -> FieldReportFormat:
        """Detect FieldReportFormat from file extension."""
        for fmt, ext_set in cls.ALLOWED_EXTENSIONS.items():
            if ext in ext_set:
                return fmt
        return FieldReportFormat.DPR
