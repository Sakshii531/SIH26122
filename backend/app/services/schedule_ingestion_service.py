from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.enums import ActivityLevel, ActivityStatus
from app.schemas.schedule_activity import ScheduleActivityCreate, ScheduleActivityResponse
from app.schemas.schedule_import import ScheduleImportSummaryResponse, ScheduleRowValidationError


class ScheduleIngestionService:
    """Service handling file parsing, column normalization, and validation of schedule files."""

    # Mandatory column canonical names
    REQUIRED_COLUMNS = ["activity_id", "activity_name", "wbs", "discipline"]

    # Header aliases mapping to canonical field names
    COLUMN_ALIASES: Dict[str, List[str]] = {
        "activity_id": ["activity id", "activity_id", "activity code", "activity_code", "code", "id", "activityid"],
        "activity_name": [
            "activity name",
            "activity_name",
            "activity description",
            "description",
            "name",
            "activityname",
        ],
        "wbs": ["wbs", "wbs_code", "wbs code", "wbscode"],
        "wbs_path": ["wbs_path", "wbs path", "wbspath", "wbs hierarchy"],
        "discipline": ["discipline", "trade", "department"],
        "activity_level": ["activity level", "activity_level", "level", "l5/l6", "l5_l6", "activitylevel"],
        "location": ["location", "site", "area", "section", "zone"],
        "planned_start": [
            "planned start",
            "planned_start",
            "planned_start_date",
            "start date",
            "start_date",
            "plannedstart",
        ],
        "planned_end": [
            "planned end",
            "planned_end",
            "planned_finish",
            "planned_finish_date",
            "end date",
            "finish date",
            "end_date",
            "finish_date",
            "plannedend",
            "plannedfinish",
        ],
        "status": ["status", "activity status", "activity_status", "state"],
        "progress_percentage": [
            "progress_percentage",
            "progress",
            "% complete",
            "percent_complete",
            "progress %",
            "progress_percent",
            "completion %",
        ],
    }

    @classmethod
    def parse_and_validate_schedule(
        cls,
        file_bytes: bytes,
        filename: str,
        project_id: Optional[UUID] = None,
    ) -> ScheduleImportSummaryResponse:
        """Parse raw file bytes (.csv, .xlsx, .xls), validate headers and rows, and return import summary."""
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        if ext not in ["csv", "xlsx", "xls"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed formats: .csv, .xlsx, .xls",
            )

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        rows = cls._extract_raw_rows(file_bytes, ext)
        if not rows:
            raise HTTPException(status_code=400, detail="File contains no data or header row.")

        header_row = rows[0]
        data_rows = rows[1:]

        column_mapping = cls._map_headers(header_row)

        target_project_id = project_id or uuid4()

        valid_activities: List[ScheduleActivityResponse] = []
        validation_errors: List[ScheduleRowValidationError] = []

        total_rows = len(data_rows)

        for idx, row in enumerate(data_rows, start=2):  # row 1 is header, data starts at row 2
            # Skip completely empty rows
            if not any(cell for cell in row if cell is not None and str(cell).strip() != ""):
                total_rows -= 1
                continue

            row_dict = cls._row_to_dict(row, column_mapping)
            activity_code = cls._clean_str(row_dict.get("activity_id"))

            try:
                activity_create = cls._build_activity_create(row_dict, target_project_id)
                activity_resp = ScheduleActivityResponse.model_validate(activity_create.model_dump())
                valid_activities.append(activity_resp)
            except ValidationError as ve:
                err_msgs = [f"{e['loc'][-1]}: {e['msg']}" for e in ve.errors()]
                validation_errors.append(
                    ScheduleRowValidationError(
                        row_number=idx,
                        activity_code=activity_code if activity_code else None,
                        errors=err_msgs,
                    )
                )
            except Exception as ex:
                validation_errors.append(
                    ScheduleRowValidationError(
                        row_number=idx,
                        activity_code=activity_code if activity_code else None,
                        errors=[str(ex)],
                    )
                )

        return ScheduleImportSummaryResponse(
            total_rows=total_rows,
            valid_count=len(valid_activities),
            rejected_count=len(validation_errors),
            activities=valid_activities,
            validation_errors=validation_errors,
        )

    @classmethod
    def _extract_raw_rows(cls, file_bytes: bytes, ext: str) -> List[List[Any]]:
        """Extract raw string/object cells from CSV or Excel bytes."""
        if ext == "csv":
            # Attempt UTF-8 decoding with fallback to latin-1
            text = None
            for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
                try:
                    text = file_bytes.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if text is None:
                raise HTTPException(status_code=400, detail="Failed to decode CSV file encoding.")

            f = io.StringIO(text)
            reader = csv.reader(f)
            return [row for row in reader]

        elif ext in ["xlsx", "xls"]:
            try:
                import openpyxl

                wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
                ws = wb.active
                rows = []
                for row in ws.iter_rows(values_only=True):
                    rows.append(list(row))
                return rows
            except Exception as err:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse Excel file: {str(err)}",
                )

        return []

    @classmethod
    def _map_headers(cls, header_row: List[Any]) -> Dict[int, str]:
        """Map row indices to canonical column names."""
        normalized_headers = [str(cell).strip().lower() if cell is not None else "" for cell in header_row]

        mapping: Dict[int, str] = {}
        found_canonical: set[str] = set()

        for idx, raw_header in enumerate(normalized_headers):
            for canonical, aliases in cls.COLUMN_ALIASES.items():
                if canonical not in found_canonical and raw_header in aliases:
                    mapping[idx] = canonical
                    found_canonical.add(canonical)
                    break

        missing = [col for col in cls.REQUIRED_COLUMNS if col not in found_canonical]
        if missing:
            display_missing = [m.replace("_", " ").title() for m in missing]
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(display_missing)}",
            )

        return mapping

    @classmethod
    def _row_to_dict(cls, row: List[Any], column_mapping: Dict[int, str]) -> Dict[str, Any]:
        """Extract canonical key-value pairs from raw row cells."""
        result: Dict[str, Any] = {}
        for idx, canonical_field in column_mapping.items():
            if idx < len(row):
                cell_val = row[idx]
                result[canonical_field] = cell_val
        return result

    @classmethod
    def _clean_str(cls, val: Any) -> str:
        """Clean string representation of cell value, mapping None or empty cells to empty string."""
        if val is None:
            return ""
        return str(val).strip()

    @classmethod
    def _build_activity_create(cls, row_dict: Dict[str, Any], project_id: UUID) -> ScheduleActivityCreate:
        """Construct and normalize ScheduleActivityCreate from raw row dictionary."""
        activity_id = cls._clean_str(row_dict.get("activity_id"))
        activity_name = cls._clean_str(row_dict.get("activity_name"))
        wbs = cls._clean_str(row_dict.get("wbs"))
        discipline = cls._clean_str(row_dict.get("discipline"))
        wbs_path = cls._clean_str(row_dict.get("wbs_path")) or wbs
        location = cls._clean_str(row_dict.get("location")) or None

        if not activity_id:
            raise ValueError("Activity ID is required.")
        if not activity_name:
            raise ValueError("Activity Name is required.")
        if not wbs:
            raise ValueError("WBS is required.")
        if not discipline:
            raise ValueError("Discipline is required.")

        level = cls._normalize_level(row_dict.get("activity_level"))
        status = cls._normalize_status(row_dict.get("status"))

        planned_start = cls._parse_date(row_dict.get("planned_start"))
        planned_end = cls._parse_date(row_dict.get("planned_end"))

        progress_percentage = cls._parse_float(row_dict.get("progress_percentage")) or 0.0

        return ScheduleActivityCreate(
            project_id=project_id,
            activity_code=activity_id,
            name=activity_name,
            wbs_code=wbs,
            wbs_path=wbs_path,
            level=level,
            discipline=discipline,
            location=location,
            planned_start_date=planned_start,
            planned_finish_date=planned_end,
            status=status,
            progress_percentage=progress_percentage,
        )

    @classmethod
    def _normalize_level(cls, val: Any) -> ActivityLevel:
        """Normalize activity level string to L5 or L6."""
        if not val:
            return ActivityLevel.L5
        s = str(val).strip().upper()
        if "6" in s:
            return ActivityLevel.L6
        return ActivityLevel.L5

    @classmethod
    def _normalize_status(cls, val: Any) -> ActivityStatus:
        """Normalize status string to ActivityStatus enum."""
        if not val:
            return ActivityStatus.NOT_STARTED
        s = str(val).strip().upper().replace(" ", "_")
        for status_enum in ActivityStatus:
            if status_enum.value == s:
                return status_enum
        if "IN" in s or "PROGRESS" in s:
            return ActivityStatus.IN_PROGRESS
        if "COMPLET" in s or "DONE" in s:
            return ActivityStatus.COMPLETED
        if "DELAY" in s:
            return ActivityStatus.DELAYED
        if "SUSPEND" in s or "PAUS" in s:
            return ActivityStatus.SUSPENDED
        return ActivityStatus.NOT_STARTED

    @classmethod
    def _parse_float(cls, val: Any) -> Optional[float]:
        """Parse float value."""
        if val is None or str(val).strip() == "":
            return None
        try:
            return float(str(val).strip().replace("%", ""))
        except ValueError:
            return None

    @classmethod
    def _parse_date(cls, val: Any) -> Optional[date]:
        """Parse raw date, datetime, or date string into datetime.date."""
        if val is None or str(val).strip() == "":
            return None
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val

        s = str(val).strip()
        # Attempt common date formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%Y-%m-%dT%H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Invalid date format for value '{s}'")
