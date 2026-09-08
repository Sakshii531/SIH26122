from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.db.supabase_client import get_supabase_client
from app.repositories.base import BaseRepository
from app.repositories.interfaces import (
    IActivityMatchRepository,
    IActivityRepository,
    IActualProgressRepository,
    IAuditLogRepository,
    IConflictRepository,
    IEvidenceRepository,
    IExtractedProgressEventRepository,
    IFieldReportRepository,
    IPlannerReviewRepository,
    IProjectRepository,
    IScheduleRepository,
    IUserRepository,
    IWBSRepository,
)
from app.schemas.activity import ScheduleActivityCreate, ScheduleActivityResponse, ScheduleActivityUpdate
from app.schemas.activity_match import ActivityMatchCreate, ActivityMatchResponse
from app.schemas.audit_log import AuditEventCreate, AuditEventResponse
from app.schemas.conflict import ConflictCreate, ConflictResponse, ConflictUpdate
from app.schemas.enums import ProgressStatus, ReviewStatus
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.schemas.extracted_progress_event import ExtractedProgressEventCreate, ExtractedProgressEventResponse
from app.schemas.field_report import FieldReportCreate, FieldReportResponse
from app.schemas.progress_event import ProgressEventResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.review_workflow import ReviewItemCreate, ReviewItemResponse
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.wbs import WBSCreate, WBSResponse, WBSUpdate


def _row_for_model(row: dict, primary_key: str, aliases: Optional[dict[str, str]] = None) -> dict:
    """Translate database naming into the API model's stable ``id`` field."""
    data = dict(row)
    if primary_key in data:
        data["id"] = data[primary_key]
    for model_field, database_field in (aliases or {}).items():
        if model_field not in data and database_field in data:
            data[model_field] = data[database_field]
    if primary_key == "user_id" and isinstance(data.get("role"), str):
        data["role"] = data["role"].upper()
    if primary_key == "activity_id":
        if data.get("level") is None:
            data["level"] = "L5"
        elif isinstance(data.get("level"), int):
            data["level"] = "L5" if data["level"] <= 5 else "L6"
        if data.get("status") == "Planned":
            data["status"] = "NOT_STARTED"
        elif data.get("status") == "In Progress":
            data["status"] = "IN_PROGRESS"
    if primary_key == "report_id" and data.get("source_format") == "Daily Progress Report":
        data["source_format"] = "DPR"
    if primary_key == "match_id" and data.get("match_status") == "Matched":
        data["match_status"] = "AUTO_MATCHED"
    if primary_key == "review_id" and data.get("decision") == "Approved":
        data["decision"] = "APPROVED"
    if primary_key == "progress_id" and data.get("status") == "In Progress":
        data["status"] = "IN_PROGRESS"
    if primary_key == "audit_id":
        data["event_type"] = {
            "CREATE": "REPORT_SUBMITTED",
            "APPROVE": "REVIEW_SUBMITTED",
            "UPDATE": "PROGRESS_UPDATED",
            "VALIDATE": "PROGRESS_UPDATED",
        }.get(data.get("action"), data.get("event_type"))
    return data


def _payload_for_table(data: dict, primary_key: str, aliases: Optional[dict[str, str]] = None) -> dict:
    """Translate API model fields into the database table contract."""
    payload = dict(data)
    payload.pop("id", None)
    for model_field, database_field in (aliases or {}).items():
        if model_field in payload:
            payload[database_field] = payload.pop(model_field)
    return payload


# 1. Projects Supabase Repository
class SupabaseProjectRepository(BaseRepository[ProjectResponse], IProjectRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "projects"

    def create(self, project: ProjectCreate) -> ProjectResponse:
        project_id = uuid4()
        now = datetime.utcnow()
        data = project.model_dump(mode="json")
        data = _payload_for_table(data, "project_id")
        data["project_id"] = str(project_id)
        data.pop("code", None)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ProjectResponse.model_validate(_row_for_model(res.data[0], "project_id"))

    def save(self, entity: ProjectResponse) -> ProjectResponse:
        data = _payload_for_table(entity.model_dump(mode="json"), "project_id")
        data.pop("code", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ProjectResponse.model_validate(_row_for_model(res.data[0], "project_id"))

    def get_by_id(self, entity_id: UUID) -> Optional[ProjectResponse]:
        res = self._client.table(self.table_name).select("*").eq("project_id", str(entity_id)).execute()
        return ProjectResponse.model_validate(_row_for_model(res.data[0], "project_id")) if res.data else None

    def list_all(self) -> List[ProjectResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ProjectResponse.model_validate(_row_for_model(r, "project_id")) for r in res.data]

    def update(self, project_id: UUID, payload: ProjectUpdate) -> Optional[ProjectResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        updates = _payload_for_table(updates, "project_id")
        updates.pop("code", None)
        res = self._client.table(self.table_name).update(updates).eq("project_id", str(project_id)).execute()
        return ProjectResponse.model_validate(_row_for_model(res.data[0], "project_id")) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("project_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 2. Schedules Supabase Repository
class SupabaseScheduleRepository(BaseRepository[ScheduleResponse], IScheduleRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "schedules"

    def create(self, schedule: ScheduleCreate) -> ScheduleResponse:
        schedule_id = uuid4()
        now = datetime.utcnow()
        data = schedule.model_dump(mode="json")
        data = _payload_for_table(data, "schedule_id")
        data["schedule_id"] = str(schedule_id)
        data["source_type"] = data.pop("source_file", None) or "API"
        data.pop("version", None)
        data.pop("description", None)
        data.pop("updated_at", None)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ScheduleResponse.model_validate(_row_for_model(res.data[0], "schedule_id"))

    def save(self, entity: ScheduleResponse) -> ScheduleResponse:
        data = _payload_for_table(entity.model_dump(mode="json"), "schedule_id")
        data["source_type"] = data.pop("source_file", None) or "API"
        data.pop("version", None)
        data.pop("description", None)
        data.pop("updated_at", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ScheduleResponse.model_validate(_row_for_model(res.data[0], "schedule_id"))

    def get_by_id(self, entity_id: UUID) -> Optional[ScheduleResponse]:
        res = self._client.table(self.table_name).select("*").eq("schedule_id", str(entity_id)).execute()
        return ScheduleResponse.model_validate(_row_for_model(res.data[0], "schedule_id")) if res.data else None

    def list_by_project(self, project_id: UUID) -> List[ScheduleResponse]:
        res = self._client.table(self.table_name).select("*").eq("project_id", str(project_id)).execute()
        return [ScheduleResponse.model_validate(_row_for_model(r, "schedule_id")) for r in res.data]

    def list_all(self) -> List[ScheduleResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ScheduleResponse.model_validate(_row_for_model(r, "schedule_id")) for r in res.data]

    def update(self, schedule_id: UUID, payload: ScheduleUpdate) -> Optional[ScheduleResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        updates = _payload_for_table(updates, "schedule_id")
        updates.pop("version", None)
        updates.pop("description", None)
        updates.pop("source_file", None)
        updates.pop("updated_at", None)
        res = self._client.table(self.table_name).update(updates).eq("schedule_id", str(schedule_id)).execute()
        return ScheduleResponse.model_validate(_row_for_model(res.data[0], "schedule_id")) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("schedule_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 3. WBS Supabase Repository
class SupabaseWBSRepository(BaseRepository[WBSResponse], IWBSRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "wbs"

    def create(self, wbs: WBSCreate) -> WBSResponse:
        wbs_id = uuid4()
        now = datetime.utcnow()
        data = wbs.model_dump(mode="json")
        data = _payload_for_table(data, "wbs_id", {"wbs_code": "code", "wbs_name": "name"})
        data["wbs_id"] = str(wbs_id)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return WBSResponse.model_validate(_row_for_model(res.data[0], "wbs_id", {"wbs_code": "code", "wbs_name": "name"}))

    def save(self, entity: WBSResponse) -> WBSResponse:
        data = _payload_for_table(entity.model_dump(mode="json"), "wbs_id", {"wbs_code": "code", "wbs_name": "name"})
        res = self._client.table(self.table_name).upsert(data).execute()
        return WBSResponse.model_validate(_row_for_model(res.data[0], "wbs_id", {"wbs_code": "code", "wbs_name": "name"}))

    def get_by_id(self, entity_id: UUID) -> Optional[WBSResponse]:
        res = self._client.table(self.table_name).select("*").eq("wbs_id", str(entity_id)).execute()
        return WBSResponse.model_validate(_row_for_model(res.data[0], "wbs_id", {"wbs_code": "code", "wbs_name": "name"})) if res.data else None

    def list_by_schedule(self, schedule_id: UUID) -> List[WBSResponse]:
        res = self._client.table(self.table_name).select("*").eq("schedule_id", str(schedule_id)).execute()
        return [WBSResponse.model_validate(_row_for_model(r, "wbs_id", {"wbs_code": "code", "wbs_name": "name"})) for r in res.data]

    def list_all(self) -> List[WBSResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [WBSResponse.model_validate(_row_for_model(r, "wbs_id", {"wbs_code": "code", "wbs_name": "name"})) for r in res.data]

    def update(self, wbs_id: UUID, payload: WBSUpdate) -> Optional[WBSResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        updates = _payload_for_table(updates, "wbs_id", {"wbs_code": "code", "wbs_name": "name"})
        res = self._client.table(self.table_name).update(updates).eq("wbs_id", str(wbs_id)).execute()
        return WBSResponse.model_validate(_row_for_model(res.data[0], "wbs_id", {"wbs_code": "code", "wbs_name": "name"})) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("wbs_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 4. Activities Supabase Repository
class SupabaseActivityRepository(BaseRepository[ScheduleActivityResponse], IActivityRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "activities"

    def create(self, activity: ScheduleActivityCreate) -> ScheduleActivityResponse:
        act_id = uuid4()
        now = datetime.utcnow()
        data = activity.model_dump(mode="json")
        data = _payload_for_table(data, "activity_id")
        data["activity_id"] = str(act_id)
        data.pop("project_id", None)
        data.pop("schedule_id", None)
        data["planned_start"] = data.pop("planned_start_date", None)
        data["planned_finish"] = data.pop("planned_finish_date", None)
        data.pop("actual_start_date", None)
        data.pop("actual_finish_date", None)
        data.pop("location", None)
        if isinstance(data.get("level"), str):
            data["level"] = 5 if data["level"] == "L5" else 6
        data.pop("progress_percentage", None)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ScheduleActivityResponse.model_validate(_row_for_model(res.data[0], "activity_id"))

    def save_item(self, activity: ScheduleActivityResponse) -> ScheduleActivityResponse:
        data = _payload_for_table(activity.model_dump(mode="json"), "activity_id")
        data.pop("project_id", None)
        data.pop("schedule_id", None)
        data["planned_start"] = data.pop("planned_start_date", None)
        data["planned_finish"] = data.pop("planned_finish_date", None)
        data.pop("actual_start_date", None)
        data.pop("actual_finish_date", None)
        data.pop("location", None)
        data.pop("progress_percentage", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ScheduleActivityResponse.model_validate(_row_for_model(res.data[0], "activity_id"))

    def save(self, entity: ScheduleActivityResponse) -> ScheduleActivityResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").eq("activity_id", str(entity_id)).execute()
        return ScheduleActivityResponse.model_validate(_row_for_model(res.data[0], "activity_id")) if res.data else None

    def get_by_code(self, activity_code: str) -> Optional[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").ilike("activity_code", activity_code).execute()
        return ScheduleActivityResponse.model_validate(_row_for_model(res.data[0], "activity_id")) if res.data else None

    def list_by_project(self, project_id: UUID) -> List[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").eq("project_id", str(project_id)).execute()
        return [ScheduleActivityResponse.model_validate(_row_for_model(r, "activity_id")) for r in res.data]

    def list_all(self) -> List[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ScheduleActivityResponse.model_validate(_row_for_model(r, "activity_id")) for r in res.data]

    def update(self, activity_id: UUID, payload: ScheduleActivityUpdate) -> Optional[ScheduleActivityResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        updates = _payload_for_table(updates, "activity_id")
        updates["planned_start"] = updates.pop("planned_start_date", None)
        updates["planned_finish"] = updates.pop("planned_finish_date", None)
        updates.pop("actual_start_date", None)
        updates.pop("actual_finish_date", None)
        updates.pop("location", None)
        if isinstance(updates.get("level"), str):
            updates["level"] = 5 if updates["level"] == "L5" else 6
        updates.pop("progress_percentage", None)
        res = self._client.table(self.table_name).update(updates).eq("activity_id", str(activity_id)).execute()
        return ScheduleActivityResponse.model_validate(_row_for_model(res.data[0], "activity_id")) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("activity_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 5. Field Reports Supabase Repository
class SupabaseFieldReportRepository(BaseRepository[FieldReportResponse], IFieldReportRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "field_reports"

    def create(self, report: FieldReportCreate) -> FieldReportResponse:
        rep_id = uuid4()
        now = datetime.utcnow()
        data = report.model_dump(mode="json")
        data = _payload_for_table(data, "report_id", {"raw_content": "raw_text", "reporter_id": "submitted_by", "source_format": "report_type"})
        data["report_id"] = str(rep_id)
        data["status"] = data.pop("status", None) or "SUBMITTED"
        data.pop("evidence", None)
        if not data.get("project_id"):
            data["project_id"] = str(uuid4())
        if "evidence" not in data or data["evidence"] is None:
            data["evidence"] = []
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return FieldReportResponse.model_validate(_row_for_model(res.data[0], "report_id", {"raw_content": "raw_text", "reporter_id": "submitted_by", "source_format": "report_type"}))

    def save_item(self, report: FieldReportResponse) -> FieldReportResponse:
        data = _payload_for_table(report.model_dump(mode="json"), "report_id", {"raw_content": "raw_text", "reporter_id": "submitted_by", "source_format": "report_type"})
        data.pop("evidence", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return FieldReportResponse.model_validate(_row_for_model(res.data[0], "report_id", {"raw_content": "raw_text", "reporter_id": "submitted_by", "source_format": "report_type"}))

    def save(self, entity: FieldReportResponse) -> FieldReportResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[FieldReportResponse]:
        res = self._client.table(self.table_name).select("*").eq("report_id", str(entity_id)).execute()
        return FieldReportResponse.model_validate(_row_for_model(res.data[0], "report_id", {"raw_content": "raw_text", "reporter_id": "submitted_by", "source_format": "report_type"})) if res.data else None

    def list_by_project(self, project_id: UUID) -> List[FieldReportResponse]:
        res = self._client.table(self.table_name).select("*").eq("project_id", str(project_id)).execute()
        return [FieldReportResponse.model_validate(_row_for_model(r, "report_id", {"raw_content": "raw_text", "reporter_id": "submitted_by", "source_format": "report_type"})) for r in res.data]

    def list_all(self) -> List[FieldReportResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [FieldReportResponse.model_validate(_row_for_model(r, "report_id", {"raw_content": "raw_text", "reporter_id": "submitted_by", "source_format": "report_type"})) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("report_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 6. Evidence Supabase Repository
class SupabaseEvidenceRepository(BaseRepository[EvidenceResponse], IEvidenceRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "evidence"

    def create(self, evidence: EvidenceCreate) -> EvidenceResponse:
        ev_id = uuid4()
        now = datetime.utcnow()
        data = evidence.model_dump(mode="json")
        data = _payload_for_table(data, "evidence_id", {"file_name": "evidence_type"})
        data["evidence_id"] = str(ev_id)
        data.pop("mime_type", None)
        data.pop("description", None)
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return EvidenceResponse.model_validate(_row_for_model(res.data[0], "evidence_id", {"file_name": "evidence_type"}))

    def save_item(self, evidence: EvidenceResponse) -> EvidenceResponse:
        data = _payload_for_table(evidence.model_dump(mode="json"), "evidence_id", {"file_name": "evidence_type"})
        data.pop("mime_type", None)
        data.pop("description", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return EvidenceResponse.model_validate(_row_for_model(res.data[0], "evidence_id", {"file_name": "evidence_type"}))

    def save(self, entity: EvidenceResponse) -> EvidenceResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[EvidenceResponse]:
        res = self._client.table(self.table_name).select("*").eq("evidence_id", str(entity_id)).execute()
        return EvidenceResponse.model_validate(_row_for_model(res.data[0], "evidence_id", {"file_name": "evidence_type"})) if res.data else None

    def list_by_report(self, report_id: UUID) -> List[EvidenceResponse]:
        res = self._client.table(self.table_name).select("*").eq("report_id", str(report_id)).execute()
        return [EvidenceResponse.model_validate(_row_for_model(r, "evidence_id", {"file_name": "evidence_type"})) for r in res.data]

    def list_all(self) -> List[EvidenceResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [EvidenceResponse.model_validate(_row_for_model(r, "evidence_id", {"file_name": "evidence_type"})) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("evidence_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 7. Extracted Progress Events Supabase Repository
class SupabaseExtractedProgressEventRepository(
    BaseRepository[ExtractedProgressEventResponse], IExtractedProgressEventRepository
):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "extracted_progress_events"

    def create(self, event: ExtractedProgressEventCreate) -> ExtractedProgressEventResponse:
        ev_id = uuid4()
        now = datetime.utcnow()
        data = event.model_dump(mode="json")
        data = _payload_for_table(data, "event_id", {"extracted_activity_name": "activity_description", "extracted_progress_percentage": "progress_value"})
        data["event_id"] = str(ev_id)
        data.pop("extraction_confidence", None)
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ExtractedProgressEventResponse.model_validate(_row_for_model(res.data[0], "event_id", {"extracted_activity_name": "activity_description", "extracted_progress_percentage": "progress_value"}))

    def save_item(self, event: ExtractedProgressEventResponse) -> ExtractedProgressEventResponse:
        data = _payload_for_table(event.model_dump(mode="json"), "event_id", {"extracted_activity_name": "activity_description", "extracted_progress_percentage": "progress_value"})
        data.pop("extraction_confidence", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ExtractedProgressEventResponse.model_validate(_row_for_model(res.data[0], "event_id", {"extracted_activity_name": "activity_description", "extracted_progress_percentage": "progress_value"}))

    def save(self, entity: ExtractedProgressEventResponse) -> ExtractedProgressEventResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ExtractedProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("event_id", str(entity_id)).execute()
        return ExtractedProgressEventResponse.model_validate(_row_for_model(res.data[0], "event_id", {"extracted_activity_name": "activity_description", "extracted_progress_percentage": "progress_value"})) if res.data else None

    def list_by_report(self, report_id: UUID) -> List[ExtractedProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("report_id", str(report_id)).execute()
        return [ExtractedProgressEventResponse.model_validate(_row_for_model(r, "event_id", {"extracted_activity_name": "activity_description", "extracted_progress_percentage": "progress_value"})) for r in res.data]

    def list_all(self) -> List[ExtractedProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ExtractedProgressEventResponse.model_validate(_row_for_model(r, "event_id", {"extracted_activity_name": "activity_description", "extracted_progress_percentage": "progress_value"})) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("event_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 8. Activity Matches Supabase Repository
class SupabaseActivityMatchRepository(BaseRepository[ActivityMatchResponse], IActivityMatchRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "activity_matches"

    def create(self, match: ActivityMatchCreate) -> ActivityMatchResponse:
        m_id = uuid4()
        now = datetime.utcnow()
        data = match.model_dump(mode="json")
        data = _payload_for_table(data, "match_id")
        data["match_id"] = str(m_id)
        data.pop("report_id", None)
        data.pop("field_report_id", None)
        data.pop("schedule_activity_id", None)
        if not data.get("field_report_id"):
            data["field_report_id"] = data.get("report_id")
        if not data.get("schedule_activity_id"):
            data["schedule_activity_id"] = data.get("activity_id")
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ActivityMatchResponse.model_validate(_row_for_model(res.data[0], "match_id"))

    def save_item(self, match: ActivityMatchResponse) -> ActivityMatchResponse:
        data = _payload_for_table(match.model_dump(mode="json"), "match_id")
        data.pop("report_id", None)
        data.pop("field_report_id", None)
        data.pop("schedule_activity_id", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ActivityMatchResponse.model_validate(_row_for_model(res.data[0], "match_id"))

    def save(self, entity: ActivityMatchResponse) -> ActivityMatchResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ActivityMatchResponse]:
        res = self._client.table(self.table_name).select("*").eq("match_id", str(entity_id)).execute()
        return ActivityMatchResponse.model_validate(_row_for_model(res.data[0], "match_id")) if res.data else None

    def list_by_event(self, event_id: UUID) -> List[ActivityMatchResponse]:
        res = self._client.table(self.table_name).select("*").eq("event_id", str(event_id)).execute()
        return [ActivityMatchResponse.model_validate(_row_for_model(r, "match_id")) for r in res.data]

    def list_all(self) -> List[ActivityMatchResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ActivityMatchResponse.model_validate(_row_for_model(r, "match_id")) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("match_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 9. Planner Reviews Supabase Repository
class SupabasePlannerReviewRepository(BaseRepository[ReviewItemResponse], IPlannerReviewRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "planner_reviews"

    def create(self, payload: ReviewItemCreate) -> ReviewItemResponse:
        review_id = uuid4()
        now = datetime.utcnow()
        data = payload.model_dump(mode="json")
        data = _payload_for_table(data, "review_id")
        data["review_id"] = str(review_id)
        data.pop("report_id", None)
        data.pop("schedule_activity_id", None)
        data.pop("confidence_score", None)
        data.pop("extracted_progress_percentage", None)
        data["status"] = ReviewStatus.PENDING.value
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ReviewItemResponse.model_validate(_row_for_model(res.data[0], "review_id"))

    def save_item(self, review: ReviewItemResponse) -> ReviewItemResponse:
        data = _payload_for_table(review.model_dump(mode="json"), "review_id")
        data.pop("report_id", None)
        data.pop("schedule_activity_id", None)
        data.pop("confidence_score", None)
        data.pop("extracted_progress_percentage", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ReviewItemResponse.model_validate(_row_for_model(res.data[0], "review_id"))

    def save(self, entity: ReviewItemResponse) -> ReviewItemResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ReviewItemResponse]:
        res = self._client.table(self.table_name).select("*").eq("review_id", str(entity_id)).execute()
        return ReviewItemResponse.model_validate(_row_for_model(res.data[0], "review_id")) if res.data else None

    def list_all(self, status: Optional[ReviewStatus] = None) -> List[ReviewItemResponse]:
        query = self._client.table(self.table_name).select("*")
        if status is not None:
            query = query.eq("status", status.value if hasattr(status, "value") else str(status))
        res = query.execute()
        return [ReviewItemResponse.model_validate(_row_for_model(r, "review_id")) for r in res.data]

    def update(self, review_id: UUID, review: ReviewItemResponse) -> ReviewItemResponse:
        data = review.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ReviewItemResponse.model_validate(_row_for_model(res.data[0], "review_id")) if res.data else review

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("review_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 10. Conflicts Supabase Repository
class SupabaseConflictRepository(BaseRepository[ConflictResponse], IConflictRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "conflicts"

    def create(self, payload: ConflictCreate) -> ConflictResponse:
        conflict_id = uuid4()
        now = datetime.utcnow()
        data = payload.model_dump(mode="json")
        data = _payload_for_table(data, "conflict_id")
        data["conflict_id"] = str(conflict_id)
        data.pop("conflicting_event_id", None)
        data.pop("resolution_status", None)
        data.pop("resolution_notes", None)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ConflictResponse.model_validate(_row_for_model(res.data[0], "conflict_id"))

    def save_item(self, conflict: ConflictResponse) -> ConflictResponse:
        data = _payload_for_table(conflict.model_dump(mode="json"), "conflict_id")
        data.pop("conflicting_event_id", None)
        data.pop("resolution_status", None)
        data.pop("resolution_notes", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ConflictResponse.model_validate(_row_for_model(res.data[0], "conflict_id"))

    def save(self, entity: ConflictResponse) -> ConflictResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ConflictResponse]:
        res = self._client.table(self.table_name).select("*").eq("conflict_id", str(entity_id)).execute()
        return ConflictResponse.model_validate(_row_for_model(res.data[0], "conflict_id")) if res.data else None

    def update(self, conflict_id: UUID, payload: ConflictUpdate) -> ConflictResponse:
        item = self.get_by_id(conflict_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Conflict record '{conflict_id}' not found.")
        now = datetime.utcnow()
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = now.isoformat()
        updates = _payload_for_table(updates, "conflict_id")
        res = self._client.table(self.table_name).update(updates).eq("conflict_id", str(conflict_id)).execute()
        if res.data:
            return ConflictResponse.model_validate(_row_for_model(res.data[0], "conflict_id"))
        updated = item.model_copy(update=payload.model_dump(exclude_unset=True))
        return updated

    def list_all(
        self,
        event_id: Optional[UUID] = None,
        resolution_status: Optional[str] = None,
    ) -> List[ConflictResponse]:
        query = self._client.table(self.table_name).select("*")
        if event_id is not None:
            query = query.or_(f"event_id.eq.{event_id},conflicting_event_id.eq.{event_id}")
        if resolution_status is not None:
            query = query.ilike("resolution_status", resolution_status)
        res = query.execute()
        return [ConflictResponse.model_validate(_row_for_model(r, "conflict_id")) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("conflict_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 11. Actual Progress Supabase Repository
class SupabaseActualProgressRepository(BaseRepository[ProgressEventResponse], IActualProgressRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "actual_progress"

    def create(self, progress: ProgressEventResponse) -> ProgressEventResponse:
        data = progress.model_dump(mode="json")
        data = _payload_for_table(data, "progress_id", {"progress_percentage": "progress_value"})
        data["progress_id"] = data.pop("id", str(uuid4()))
        data.pop("project_id", None)
        data.pop("review_id", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return ProgressEventResponse.model_validate(_row_for_model(res.data[0], "progress_id", {"progress_percentage": "progress_value"}))

    def save(self, entity: ProgressEventResponse) -> ProgressEventResponse:
        return self.create(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("progress_id", str(entity_id)).execute()
        return ProgressEventResponse.model_validate(_row_for_model(res.data[0], "progress_id", {"progress_percentage": "progress_value"})) if res.data else None

    def get_by_review_id(self, review_id: UUID) -> Optional[ProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("review_id", str(review_id)).execute()
        return ProgressEventResponse.model_validate(_row_for_model(res.data[0], "progress_id", {"progress_percentage": "progress_value"})) if res.data else None

    def list_all(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[ProgressStatus] = None,
    ) -> List[ProgressEventResponse]:
        query = self._client.table(self.table_name).select("*")
        if project_id is not None:
            query = query.eq("project_id", str(project_id))
        if status is not None:
            query = query.eq("status", status.value if hasattr(status, "value") else str(status))
        res = query.execute()
        return [ProgressEventResponse.model_validate(_row_for_model(r, "progress_id", {"progress_percentage": "progress_value"})) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("progress_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 12. Audit Logs Supabase Repository
class SupabaseAuditLogRepository(BaseRepository[AuditEventResponse], IAuditLogRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "audit_logs"

    def create(self, event: AuditEventCreate) -> AuditEventResponse:
        audit_id = uuid4()
        now = datetime.utcnow()
        data = event.model_dump(mode="json")
        data = _payload_for_table(data, "audit_id", {"actor_id": "user_id", "event_type": "action", "description": "details"})
        data["audit_id"] = str(audit_id)
        data.pop("project_id", None)
        data.pop("payload", None)
        data["timestamp"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return AuditEventResponse.model_validate(_row_for_model(res.data[0], "audit_id", {"actor_id": "user_id", "event_type": "action", "description": "details"}))

    def save_item(self, log: AuditEventResponse) -> AuditEventResponse:
        data = _payload_for_table(log.model_dump(mode="json"), "audit_id", {"actor_id": "user_id", "event_type": "action", "description": "details"})
        data.pop("project_id", None)
        data.pop("payload", None)
        res = self._client.table(self.table_name).upsert(data).execute()
        return AuditEventResponse.model_validate(_row_for_model(res.data[0], "audit_id", {"actor_id": "user_id", "event_type": "action", "description": "details"}))

    def save(self, entity: AuditEventResponse) -> AuditEventResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[AuditEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("audit_id", str(entity_id)).execute()
        return AuditEventResponse.model_validate(_row_for_model(res.data[0], "audit_id", {"actor_id": "user_id", "event_type": "action", "description": "details"})) if res.data else None

    def list_all(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
    ) -> List[AuditEventResponse]:
        query = self._client.table(self.table_name).select("*")
        if entity_type is not None:
            query = query.ilike("entity_type", entity_type)
        if entity_id is not None:
            query = query.eq("entity_id", str(entity_id))
        res = query.execute()
        return [AuditEventResponse.model_validate(_row_for_model(r, "audit_id", {"actor_id": "user_id", "event_type": "action", "description": "details"})) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("audit_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")


# 13. Users Supabase Repository
class SupabaseUserRepository(BaseRepository[UserResponse], IUserRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "users"

    def create(self, user: UserCreate) -> UserResponse:
        u_id = uuid4()
        now = datetime.utcnow()
        data = user.model_dump(mode="json")
        data = _payload_for_table(data, "user_id", {"username": "name", "full_name": "name"})
        data["user_id"] = str(u_id)
        data.pop("is_active", None)
        if isinstance(data.get("role"), str):
            data["role"] = {"PLANNER": "Planner", "SUPERVISOR": "Supervisor"}.get(data["role"].upper(), data["role"])
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return UserResponse.model_validate(_row_for_model(res.data[0], "user_id", {"username": "name", "full_name": "name"}))

    def save(self, entity: UserResponse) -> UserResponse:
        data = _payload_for_table(entity.model_dump(mode="json"), "user_id", {"username": "name", "full_name": "name"})
        data.pop("is_active", None)
        if isinstance(data.get("role"), str):
            data["role"] = {"PLANNER": "Planner", "SUPERVISOR": "Supervisor"}.get(data["role"].upper(), data["role"])
        res = self._client.table(self.table_name).upsert(data).execute()
        return UserResponse.model_validate(_row_for_model(res.data[0], "user_id", {"username": "name", "full_name": "name"}))

    def get_by_id(self, entity_id: UUID) -> Optional[UserResponse]:
        res = self._client.table(self.table_name).select("*").eq("user_id", str(entity_id)).execute()
        return UserResponse.model_validate(_row_for_model(res.data[0], "user_id", {"username": "name", "full_name": "name"})) if res.data else None

    def get_by_username(self, username: str) -> Optional[UserResponse]:
        res = self._client.table(self.table_name).select("*").ilike("name", username).execute()
        return UserResponse.model_validate(_row_for_model(res.data[0], "user_id", {"username": "name", "full_name": "name"})) if res.data else None

    def list_all(self) -> List[UserResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [UserResponse.model_validate(_row_for_model(r, "user_id", {"username": "name", "full_name": "name"})) for r in res.data]

    def update(self, user_id: UUID, payload: UserUpdate) -> Optional[UserResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        updates = _payload_for_table(updates, "user_id", {"username": "name", "full_name": "name"})
        updates.pop("is_active", None)
        res = self._client.table(self.table_name).update(updates).eq("user_id", str(user_id)).execute()
        return UserResponse.model_validate(_row_for_model(res.data[0], "user_id", {"username": "name", "full_name": "name"})) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("user_id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")
