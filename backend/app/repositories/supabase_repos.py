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


# 1. Projects Supabase Repository
class SupabaseProjectRepository(BaseRepository[ProjectResponse], IProjectRepository):
    def __init__(self, client=None) -> None:
        self._client = client or get_supabase_client()
        self.table_name = "projects"

    def create(self, project: ProjectCreate) -> ProjectResponse:
        project_id = uuid4()
        now = datetime.utcnow()
        data = project.model_dump(mode="json")
        data["id"] = str(project_id)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ProjectResponse.model_validate(res.data[0])

    def save(self, entity: ProjectResponse) -> ProjectResponse:
        data = entity.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ProjectResponse.model_validate(res.data[0])

    def get_by_id(self, entity_id: UUID) -> Optional[ProjectResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ProjectResponse.model_validate(res.data[0]) if res.data else None

    def list_all(self) -> List[ProjectResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ProjectResponse.model_validate(r) for r in res.data]

    def update(self, project_id: UUID, payload: ProjectUpdate) -> Optional[ProjectResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        res = self._client.table(self.table_name).update(updates).eq("id", str(project_id)).execute()
        return ProjectResponse.model_validate(res.data[0]) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(schedule_id)
        if not data.get("version"):
            data["version"] = "v1.0"
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ScheduleResponse.model_validate(res.data[0])

    def save(self, entity: ScheduleResponse) -> ScheduleResponse:
        data = entity.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ScheduleResponse.model_validate(res.data[0])

    def get_by_id(self, entity_id: UUID) -> Optional[ScheduleResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ScheduleResponse.model_validate(res.data[0]) if res.data else None

    def list_by_project(self, project_id: UUID) -> List[ScheduleResponse]:
        res = self._client.table(self.table_name).select("*").eq("project_id", str(project_id)).execute()
        return [ScheduleResponse.model_validate(r) for r in res.data]

    def list_all(self) -> List[ScheduleResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ScheduleResponse.model_validate(r) for r in res.data]

    def update(self, schedule_id: UUID, payload: ScheduleUpdate) -> Optional[ScheduleResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        res = self._client.table(self.table_name).update(updates).eq("id", str(schedule_id)).execute()
        return ScheduleResponse.model_validate(res.data[0]) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(wbs_id)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return WBSResponse.model_validate(res.data[0])

    def save(self, entity: WBSResponse) -> WBSResponse:
        data = entity.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return WBSResponse.model_validate(res.data[0])

    def get_by_id(self, entity_id: UUID) -> Optional[WBSResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return WBSResponse.model_validate(res.data[0]) if res.data else None

    def list_by_schedule(self, schedule_id: UUID) -> List[WBSResponse]:
        res = self._client.table(self.table_name).select("*").eq("schedule_id", str(schedule_id)).execute()
        return [WBSResponse.model_validate(r) for r in res.data]

    def list_all(self) -> List[WBSResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [WBSResponse.model_validate(r) for r in res.data]

    def update(self, wbs_id: UUID, payload: WBSUpdate) -> Optional[WBSResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        res = self._client.table(self.table_name).update(updates).eq("id", str(wbs_id)).execute()
        return WBSResponse.model_validate(res.data[0]) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(act_id)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ScheduleActivityResponse.model_validate(res.data[0])

    def save_item(self, activity: ScheduleActivityResponse) -> ScheduleActivityResponse:
        data = activity.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ScheduleActivityResponse.model_validate(res.data[0])

    def save(self, entity: ScheduleActivityResponse) -> ScheduleActivityResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ScheduleActivityResponse.model_validate(res.data[0]) if res.data else None

    def get_by_code(self, activity_code: str) -> Optional[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").ilike("activity_code", activity_code).execute()
        return ScheduleActivityResponse.model_validate(res.data[0]) if res.data else None

    def list_by_project(self, project_id: UUID) -> List[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").eq("project_id", str(project_id)).execute()
        return [ScheduleActivityResponse.model_validate(r) for r in res.data]

    def list_all(self) -> List[ScheduleActivityResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ScheduleActivityResponse.model_validate(r) for r in res.data]

    def update(self, activity_id: UUID, payload: ScheduleActivityUpdate) -> Optional[ScheduleActivityResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        res = self._client.table(self.table_name).update(updates).eq("id", str(activity_id)).execute()
        return ScheduleActivityResponse.model_validate(res.data[0]) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(rep_id)
        if not data.get("project_id"):
            data["project_id"] = str(uuid4())
        if "evidence" not in data or data["evidence"] is None:
            data["evidence"] = []
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return FieldReportResponse.model_validate(res.data[0])

    def save_item(self, report: FieldReportResponse) -> FieldReportResponse:
        data = report.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return FieldReportResponse.model_validate(res.data[0])

    def save(self, entity: FieldReportResponse) -> FieldReportResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[FieldReportResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return FieldReportResponse.model_validate(res.data[0]) if res.data else None

    def list_by_project(self, project_id: UUID) -> List[FieldReportResponse]:
        res = self._client.table(self.table_name).select("*").eq("project_id", str(project_id)).execute()
        return [FieldReportResponse.model_validate(r) for r in res.data]

    def list_all(self) -> List[FieldReportResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [FieldReportResponse.model_validate(r) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(ev_id)
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return EvidenceResponse.model_validate(res.data[0])

    def save_item(self, evidence: EvidenceResponse) -> EvidenceResponse:
        data = evidence.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return EvidenceResponse.model_validate(res.data[0])

    def save(self, entity: EvidenceResponse) -> EvidenceResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[EvidenceResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return EvidenceResponse.model_validate(res.data[0]) if res.data else None

    def list_by_report(self, report_id: UUID) -> List[EvidenceResponse]:
        res = self._client.table(self.table_name).select("*").eq("report_id", str(report_id)).execute()
        return [EvidenceResponse.model_validate(r) for r in res.data]

    def list_all(self) -> List[EvidenceResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [EvidenceResponse.model_validate(r) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(ev_id)
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ExtractedProgressEventResponse.model_validate(res.data[0])

    def save_item(self, event: ExtractedProgressEventResponse) -> ExtractedProgressEventResponse:
        data = event.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ExtractedProgressEventResponse.model_validate(res.data[0])

    def save(self, entity: ExtractedProgressEventResponse) -> ExtractedProgressEventResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ExtractedProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ExtractedProgressEventResponse.model_validate(res.data[0]) if res.data else None

    def list_by_report(self, report_id: UUID) -> List[ExtractedProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("report_id", str(report_id)).execute()
        return [ExtractedProgressEventResponse.model_validate(r) for r in res.data]

    def list_all(self) -> List[ExtractedProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ExtractedProgressEventResponse.model_validate(r) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(m_id)
        if not data.get("field_report_id"):
            data["field_report_id"] = data.get("report_id")
        if not data.get("schedule_activity_id"):
            data["schedule_activity_id"] = data.get("activity_id")
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ActivityMatchResponse.model_validate(res.data[0])

    def save_item(self, match: ActivityMatchResponse) -> ActivityMatchResponse:
        data = match.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ActivityMatchResponse.model_validate(res.data[0])

    def save(self, entity: ActivityMatchResponse) -> ActivityMatchResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ActivityMatchResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ActivityMatchResponse.model_validate(res.data[0]) if res.data else None

    def list_by_event(self, event_id: UUID) -> List[ActivityMatchResponse]:
        res = self._client.table(self.table_name).select("*").eq("event_id", str(event_id)).execute()
        return [ActivityMatchResponse.model_validate(r) for r in res.data]

    def list_all(self) -> List[ActivityMatchResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [ActivityMatchResponse.model_validate(r) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(review_id)
        data["status"] = ReviewStatus.PENDING.value
        data["created_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ReviewItemResponse.model_validate(res.data[0])

    def save_item(self, review: ReviewItemResponse) -> ReviewItemResponse:
        data = review.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ReviewItemResponse.model_validate(res.data[0])

    def save(self, entity: ReviewItemResponse) -> ReviewItemResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ReviewItemResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ReviewItemResponse.model_validate(res.data[0]) if res.data else None

    def list_all(self, status: Optional[ReviewStatus] = None) -> List[ReviewItemResponse]:
        query = self._client.table(self.table_name).select("*")
        if status is not None:
            query = query.eq("status", status.value if hasattr(status, "value") else str(status))
        res = query.execute()
        return [ReviewItemResponse.model_validate(r) for r in res.data]

    def update(self, review_id: UUID, review: ReviewItemResponse) -> ReviewItemResponse:
        data = review.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ReviewItemResponse.model_validate(res.data[0]) if res.data else review

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(conflict_id)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return ConflictResponse.model_validate(res.data[0])

    def save_item(self, conflict: ConflictResponse) -> ConflictResponse:
        data = conflict.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return ConflictResponse.model_validate(res.data[0])

    def save(self, entity: ConflictResponse) -> ConflictResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ConflictResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ConflictResponse.model_validate(res.data[0]) if res.data else None

    def update(self, conflict_id: UUID, payload: ConflictUpdate) -> ConflictResponse:
        item = self.get_by_id(conflict_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Conflict record '{conflict_id}' not found.")
        now = datetime.utcnow()
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).update(updates).eq("id", str(conflict_id)).execute()
        if res.data:
            return ConflictResponse.model_validate(res.data[0])
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
        return [ConflictResponse.model_validate(r) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        res = self._client.table(self.table_name).upsert(data).execute()
        return ProgressEventResponse.model_validate(res.data[0])

    def save(self, entity: ProgressEventResponse) -> ProgressEventResponse:
        return self.create(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return ProgressEventResponse.model_validate(res.data[0]) if res.data else None

    def get_by_review_id(self, review_id: UUID) -> Optional[ProgressEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("review_id", str(review_id)).execute()
        return ProgressEventResponse.model_validate(res.data[0]) if res.data else None

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
        return [ProgressEventResponse.model_validate(r) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(audit_id)
        data["timestamp"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return AuditEventResponse.model_validate(res.data[0])

    def save_item(self, log: AuditEventResponse) -> AuditEventResponse:
        data = log.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return AuditEventResponse.model_validate(res.data[0])

    def save(self, entity: AuditEventResponse) -> AuditEventResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[AuditEventResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return AuditEventResponse.model_validate(res.data[0]) if res.data else None

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
        return [AuditEventResponse.model_validate(r) for r in res.data]

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
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
        data["id"] = str(u_id)
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        res = self._client.table(self.table_name).insert(data).execute()
        return UserResponse.model_validate(res.data[0])

    def save(self, entity: UserResponse) -> UserResponse:
        data = entity.model_dump(mode="json")
        res = self._client.table(self.table_name).upsert(data).execute()
        return UserResponse.model_validate(res.data[0])

    def get_by_id(self, entity_id: UUID) -> Optional[UserResponse]:
        res = self._client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
        return UserResponse.model_validate(res.data[0]) if res.data else None

    def get_by_username(self, username: str) -> Optional[UserResponse]:
        res = self._client.table(self.table_name).select("*").ilike("username", username).execute()
        return UserResponse.model_validate(res.data[0]) if res.data else None

    def list_all(self) -> List[UserResponse]:
        res = self._client.table(self.table_name).select("*").execute()
        return [UserResponse.model_validate(r) for r in res.data]

    def update(self, user_id: UUID, payload: UserUpdate) -> Optional[UserResponse]:
        updates = payload.model_dump(exclude_unset=True, mode="json")
        updates["updated_at"] = datetime.utcnow().isoformat()
        res = self._client.table(self.table_name).update(updates).eq("id", str(user_id)).execute()
        return UserResponse.model_validate(res.data[0]) if res.data else None

    def delete(self, entity_id: UUID) -> bool:
        res = self._client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
        return len(res.data) > 0 if res.data is not None else False

    def clear(self) -> None:
        raise NotImplementedError("Clear operation is not supported for Supabase repository to prevent accidental data loss.")
