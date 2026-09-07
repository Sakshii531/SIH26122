from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

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


# 1. Projects In-Memory Repository
class InMemoryProjectRepository(BaseRepository[ProjectResponse], IProjectRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ProjectResponse] = {}

    def create(self, project: ProjectCreate) -> ProjectResponse:
        project_id = uuid4()
        now = datetime.utcnow()
        resp = ProjectResponse(
            id=project_id,
            name=project.name,
            code=project.code,
            description=project.description,
            created_at=now,
            updated_at=now,
        )
        self._store[project_id] = resp
        return resp

    def save(self, entity: ProjectResponse) -> ProjectResponse:
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, entity_id: UUID) -> Optional[ProjectResponse]:
        return self._store.get(entity_id)

    def list_all(self) -> List[ProjectResponse]:
        return list(self._store.values())

    def update(self, project_id: UUID, payload: ProjectUpdate) -> Optional[ProjectResponse]:
        item = self.get_by_id(project_id)
        if not item:
            return None
        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.utcnow()
        updated = item.model_copy(update=updates)
        self._store[project_id] = updated
        return updated

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 2. Schedules In-Memory Repository
class InMemoryScheduleRepository(BaseRepository[ScheduleResponse], IScheduleRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ScheduleResponse] = {}

    def create(self, schedule: ScheduleCreate) -> ScheduleResponse:
        schedule_id = uuid4()
        now = datetime.utcnow()
        resp = ScheduleResponse(
            id=schedule_id,
            project_id=schedule.project_id,
            name=schedule.name,
            version=schedule.version or "v1.0",
            created_at=now,
            updated_at=now,
        )
        self._store[schedule_id] = resp
        return resp

    def save(self, entity: ScheduleResponse) -> ScheduleResponse:
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, entity_id: UUID) -> Optional[ScheduleResponse]:
        return self._store.get(entity_id)

    def list_by_project(self, project_id: UUID) -> List[ScheduleResponse]:
        return [s for s in self._store.values() if s.project_id == project_id]

    def list_all(self) -> List[ScheduleResponse]:
        return list(self._store.values())

    def update(self, schedule_id: UUID, payload: ScheduleUpdate) -> Optional[ScheduleResponse]:
        item = self.get_by_id(schedule_id)
        if not item:
            return None
        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.utcnow()
        updated = item.model_copy(update=updates)
        self._store[schedule_id] = updated
        return updated

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 3. WBS In-Memory Repository
class InMemoryWBSRepository(BaseRepository[WBSResponse], IWBSRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, WBSResponse] = {}

    def create(self, wbs: WBSCreate) -> WBSResponse:
        wbs_id = uuid4()
        now = datetime.utcnow()
        resp = WBSResponse(
            id=wbs_id,
            schedule_id=wbs.schedule_id,
            parent_wbs_id=wbs.parent_wbs_id,
            wbs_code=wbs.wbs_code,
            wbs_name=wbs.wbs_name,
            level=wbs.level,
            path=wbs.path,
            created_at=now,
            updated_at=now,
        )
        self._store[wbs_id] = resp
        return resp

    def save(self, entity: WBSResponse) -> WBSResponse:
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, entity_id: UUID) -> Optional[WBSResponse]:
        return self._store.get(entity_id)

    def list_by_schedule(self, schedule_id: UUID) -> List[WBSResponse]:
        return [w for w in self._store.values() if w.schedule_id == schedule_id]

    def list_all(self) -> List[WBSResponse]:
        return list(self._store.values())

    def update(self, wbs_id: UUID, payload: WBSUpdate) -> Optional[WBSResponse]:
        item = self.get_by_id(wbs_id)
        if not item:
            return None
        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.utcnow()
        updated = item.model_copy(update=updates)
        self._store[wbs_id] = updated
        return updated

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 4. Activities In-Memory Repository
class InMemoryActivityRepository(BaseRepository[ScheduleActivityResponse], IActivityRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ScheduleActivityResponse] = {}

    def create(self, activity: ScheduleActivityCreate) -> ScheduleActivityResponse:
        act_id = uuid4()
        now = datetime.utcnow()
        resp = ScheduleActivityResponse(
            id=act_id,
            project_id=activity.project_id,
            schedule_id=activity.schedule_id,
            wbs_id=activity.wbs_id,
            activity_code=activity.activity_code,
            name=activity.name,
            wbs_code=getattr(activity, "wbs_code", None),
            wbs_path=getattr(activity, "wbs_path", None),
            level=activity.level,
            discipline=activity.discipline,
            location=activity.location,
            planned_start_date=activity.planned_start_date,
            planned_finish_date=activity.planned_finish_date,
            status=activity.status,
            progress_percentage=activity.progress_percentage,
            created_at=now,
            updated_at=now,
        )
        self._store[act_id] = resp
        return resp

    def save_item(self, activity: ScheduleActivityResponse) -> ScheduleActivityResponse:
        self._store[activity.id] = activity
        return activity

    def save(self, entity: ScheduleActivityResponse) -> ScheduleActivityResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ScheduleActivityResponse]:
        return self._store.get(entity_id)

    def get_by_code(self, activity_code: str) -> Optional[ScheduleActivityResponse]:
        for act in self._store.values():
            if act.activity_code.lower() == activity_code.lower():
                return act
        return None

    def list_by_project(self, project_id: UUID) -> List[ScheduleActivityResponse]:
        return [a for a in self._store.values() if a.project_id == project_id]

    def list_all(self) -> List[ScheduleActivityResponse]:
        return list(self._store.values())

    def update(self, activity_id: UUID, payload: ScheduleActivityUpdate) -> Optional[ScheduleActivityResponse]:
        item = self.get_by_id(activity_id)
        if not item:
            return None
        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.utcnow()
        updated = item.model_copy(update=updates)
        self._store[activity_id] = updated
        return updated

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 5. Field Reports In-Memory Repository
class InMemoryFieldReportRepository(BaseRepository[FieldReportResponse], IFieldReportRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, FieldReportResponse] = {}

    def create(self, report: FieldReportCreate) -> FieldReportResponse:
        rep_id = uuid4()
        now = datetime.utcnow()
        resp = FieldReportResponse(
            id=rep_id,
            project_id=report.project_id or uuid4(),
            source_format=report.source_format,
            reporter_id=report.reporter_id,
            raw_content=report.raw_content,
            discipline=report.discipline,
            location=report.location,
            evidence=report.evidence or [],
            created_at=now,
        )
        self._store[rep_id] = resp
        return resp

    def save_item(self, report: FieldReportResponse) -> FieldReportResponse:
        self._store[report.id] = report
        return report

    def save(self, entity: FieldReportResponse) -> FieldReportResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[FieldReportResponse]:
        return self._store.get(entity_id)

    def list_by_project(self, project_id: UUID) -> List[FieldReportResponse]:
        return [r for r in self._store.values() if r.project_id == project_id]

    def list_all(self) -> List[FieldReportResponse]:
        return list(self._store.values())

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 6. Evidence In-Memory Repository
class InMemoryEvidenceRepository(BaseRepository[EvidenceResponse], IEvidenceRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, EvidenceResponse] = {}

    def create(self, evidence: EvidenceCreate) -> EvidenceResponse:
        ev_id = uuid4()
        now = datetime.utcnow()
        resp = EvidenceResponse(
            id=ev_id,
            report_id=evidence.report_id,
            file_name=evidence.file_name,
            file_url=evidence.file_url,
            mime_type=evidence.mime_type,
            description=evidence.description,
            created_at=now,
        )
        self._store[ev_id] = resp
        return resp

    def save_item(self, evidence: EvidenceResponse) -> EvidenceResponse:
        self._store[evidence.id] = evidence
        return evidence

    def save(self, entity: EvidenceResponse) -> EvidenceResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[EvidenceResponse]:
        return self._store.get(entity_id)

    def list_by_report(self, report_id: UUID) -> List[EvidenceResponse]:
        return [e for e in self._store.values() if e.report_id == report_id]

    def list_all(self) -> List[EvidenceResponse]:
        return list(self._store.values())

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 7. Extracted Progress Events In-Memory Repository
class InMemoryExtractedProgressEventRepository(
    BaseRepository[ExtractedProgressEventResponse], IExtractedProgressEventRepository
):
    def __init__(self) -> None:
        self._store: Dict[UUID, ExtractedProgressEventResponse] = {}

    def create(self, event: ExtractedProgressEventCreate) -> ExtractedProgressEventResponse:
        ev_id = uuid4()
        now = datetime.utcnow()
        resp = ExtractedProgressEventResponse(
            id=ev_id,
            report_id=event.report_id,
            extracted_activity_name=event.extracted_activity_name,
            extracted_progress_percentage=event.extracted_progress_percentage,
            extracted_status=event.extracted_status,
            extracted_start_date=event.extracted_start_date,
            extracted_finish_date=event.extracted_finish_date,
            extracted_quantity=event.extracted_quantity,
            extracted_unit=event.extracted_unit,
            extraction_confidence=event.extraction_confidence,
            discipline=event.discipline,
            location=event.location,
            created_at=now,
        )
        self._store[ev_id] = resp
        return resp

    def save_item(self, event: ExtractedProgressEventResponse) -> ExtractedProgressEventResponse:
        self._store[event.id] = event
        return event

    def save(self, entity: ExtractedProgressEventResponse) -> ExtractedProgressEventResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ExtractedProgressEventResponse]:
        return self._store.get(entity_id)

    def list_by_report(self, report_id: UUID) -> List[ExtractedProgressEventResponse]:
        return [e for e in self._store.values() if e.report_id == report_id]

    def list_all(self) -> List[ExtractedProgressEventResponse]:
        return list(self._store.values())

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 8. Activity Matches In-Memory Repository
class InMemoryActivityMatchRepository(BaseRepository[ActivityMatchResponse], IActivityMatchRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ActivityMatchResponse] = {}

    def create(self, match: ActivityMatchCreate) -> ActivityMatchResponse:
        m_id = uuid4()
        now = datetime.utcnow()
        resp = ActivityMatchResponse(
            id=m_id,
            event_id=match.event_id,
            report_id=match.report_id,
            field_report_id=match.field_report_id or match.report_id,
            activity_id=match.activity_id,
            schedule_activity_id=match.schedule_activity_id or match.activity_id,
            confidence_score=match.confidence_score,
            match_status=match.match_status,
            rationale=match.rationale,
            suggested_activity_code=match.suggested_activity_code,
            created_at=now,
        )
        self._store[m_id] = resp
        return resp

    def save_item(self, match: ActivityMatchResponse) -> ActivityMatchResponse:
        self._store[match.id] = match
        return match

    def save(self, entity: ActivityMatchResponse) -> ActivityMatchResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ActivityMatchResponse]:
        return self._store.get(entity_id)

    def list_by_event(self, event_id: UUID) -> List[ActivityMatchResponse]:
        return [m for m in self._store.values() if m.event_id == event_id]

    def list_all(self) -> List[ActivityMatchResponse]:
        return list(self._store.values())

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 9. Planner Reviews In-Memory Repository
class InMemoryPlannerReviewRepository(BaseRepository[ReviewItemResponse], IPlannerReviewRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ReviewItemResponse] = {}

    def create(self, payload: ReviewItemCreate) -> ReviewItemResponse:
        review_id = uuid4()
        now = datetime.utcnow()
        item = ReviewItemResponse(
            id=review_id,
            report_id=payload.report_id,
            schedule_activity_id=payload.schedule_activity_id,
            matched_activity_code=payload.matched_activity_code,
            confidence_score=payload.confidence_score,
            status=ReviewStatus.PENDING,
            extracted_progress_percentage=payload.extracted_progress_percentage,
            extracted_status=payload.extracted_status,
            discipline=payload.discipline,
            location=payload.location,
            evidence=payload.evidence,
            metadata=payload.metadata,
            created_at=now,
        )
        self._store[review_id] = item
        return item

    def save_item(self, review: ReviewItemResponse) -> ReviewItemResponse:
        self._store[review.id] = review
        return review

    def save(self, entity: ReviewItemResponse) -> ReviewItemResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ReviewItemResponse]:
        return self._store.get(entity_id)

    def list_all(self, status: Optional[ReviewStatus] = None) -> List[ReviewItemResponse]:
        items = list(self._store.values())
        if status is not None:
            items = [item for item in items if item.status == status]
        return items

    def update(self, review_id: UUID, review: ReviewItemResponse) -> ReviewItemResponse:
        self._store[review_id] = review
        return review

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 10. Conflicts In-Memory Repository
class InMemoryConflictRepository(BaseRepository[ConflictResponse], IConflictRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ConflictResponse] = {}

    def create(self, payload: ConflictCreate) -> ConflictResponse:
        conflict_id = uuid4()
        now = datetime.utcnow()
        conflict = ConflictResponse(
            id=conflict_id,
            event_id=payload.event_id,
            conflicting_event_id=payload.conflicting_event_id,
            conflict_type=payload.conflict_type,
            severity=payload.severity,
            description=payload.description,
            resolution_status=payload.resolution_status,
            resolved_by=payload.resolved_by,
            resolution_notes=payload.resolution_notes,
            metadata=payload.metadata,
            created_at=now,
            updated_at=now,
        )
        self._store[conflict_id] = conflict
        return conflict

    def save_item(self, conflict: ConflictResponse) -> ConflictResponse:
        self._store[conflict.id] = conflict
        return conflict

    def save(self, entity: ConflictResponse) -> ConflictResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ConflictResponse]:
        return self._store.get(entity_id)

    def update(self, conflict_id: UUID, payload: ConflictUpdate) -> ConflictResponse:
        item = self.get_by_id(conflict_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Conflict record '{conflict_id}' not found.")
        now = datetime.utcnow()
        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = now
        updated = item.model_copy(update=updates)
        self._store[conflict_id] = updated
        return updated

    def list_all(
        self,
        event_id: Optional[UUID] = None,
        resolution_status: Optional[str] = None,
    ) -> List[ConflictResponse]:
        items = list(self._store.values())
        if event_id is not None:
            items = [
                item for item in items if item.event_id == event_id or item.conflicting_event_id == event_id
            ]
        if resolution_status is not None:
            items = [item for item in items if item.resolution_status.upper() == resolution_status.upper()]
        return items

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 11. Actual Progress In-Memory Repository
class InMemoryActualProgressRepository(BaseRepository[ProgressEventResponse], IActualProgressRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, ProgressEventResponse] = {}
        self._review_progress_map: Dict[UUID, UUID] = {}

    def create(self, progress: ProgressEventResponse) -> ProgressEventResponse:
        self._store[progress.id] = progress
        if progress.review_id:
            self._review_progress_map[progress.review_id] = progress.id
        return progress

    def save(self, entity: ProgressEventResponse) -> ProgressEventResponse:
        return self.create(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[ProgressEventResponse]:
        return self._store.get(entity_id)

    def get_by_review_id(self, review_id: UUID) -> Optional[ProgressEventResponse]:
        prog_id = self._review_progress_map.get(review_id)
        if prog_id:
            return self._store.get(prog_id)
        return None

    def list_all(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[ProgressStatus] = None,
    ) -> List[ProgressEventResponse]:
        items = list(self._store.values())
        if project_id is not None:
            items = [item for item in items if item.project_id == project_id]
        if status is not None:
            items = [item for item in items if item.status == status]
        return items

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            prog = self._store[entity_id]
            if prog.review_id in self._review_progress_map:
                del self._review_progress_map[prog.review_id]
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()
        self._review_progress_map.clear()


# 12. Audit Logs In-Memory Repository
class InMemoryAuditLogRepository(BaseRepository[AuditEventResponse], IAuditLogRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, AuditEventResponse] = {}

    def create(self, event: AuditEventCreate) -> AuditEventResponse:
        audit_id = uuid4()
        now = datetime.utcnow()
        resp = AuditEventResponse(
            id=audit_id,
            project_id=event.project_id,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            actor_id=event.actor_id,
            actor_role=event.actor_role,
            description=event.description,
            payload=event.payload,
            timestamp=now,
        )
        self._store[audit_id] = resp
        return resp

    def save_item(self, log: AuditEventResponse) -> AuditEventResponse:
        self._store[log.id] = log
        return log

    def save(self, entity: AuditEventResponse) -> AuditEventResponse:
        return self.save_item(entity)

    def get_by_id(self, entity_id: UUID) -> Optional[AuditEventResponse]:
        return self._store.get(entity_id)

    def list_all(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
    ) -> List[AuditEventResponse]:
        items = list(self._store.values())
        if entity_type is not None:
            items = [item for item in items if item.entity_type.lower() == entity_type.lower()]
        if entity_id is not None:
            items = [item for item in items if item.entity_id == entity_id]
        return items

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


# 13. Users In-Memory Repository
class InMemoryUserRepository(BaseRepository[UserResponse], IUserRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, UserResponse] = {}

    def create(self, user: UserCreate) -> UserResponse:
        u_id = uuid4()
        now = datetime.utcnow()
        resp = UserResponse(
            id=u_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=now,
            updated_at=now,
        )
        self._store[u_id] = resp
        return resp

    def save(self, entity: UserResponse) -> UserResponse:
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, entity_id: UUID) -> Optional[UserResponse]:
        return self._store.get(entity_id)

    def get_by_username(self, username: str) -> Optional[UserResponse]:
        for u in self._store.values():
            if u.username.lower() == username.lower():
                return u
        return None

    def list_all(self) -> List[UserResponse]:
        return list(self._store.values())

    def update(self, user_id: UUID, payload: UserUpdate) -> Optional[UserResponse]:
        item = self.get_by_id(user_id)
        if not item:
            return None
        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.utcnow()
        updated = item.model_copy(update=updates)
        self._store[user_id] = updated
        return updated

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()
