from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

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


# 1. Projects
class IProjectRepository(ABC):
    """Repository interface for Projects entity."""

    @abstractmethod
    def create(self, project: ProjectCreate) -> ProjectResponse:
        pass

    @abstractmethod
    def get_by_id(self, project_id: UUID) -> Optional[ProjectResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[ProjectResponse]:
        pass

    @abstractmethod
    def update(self, project_id: UUID, payload: ProjectUpdate) -> Optional[ProjectResponse]:
        pass

    @abstractmethod
    def delete(self, project_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 2. Schedules
class IScheduleRepository(ABC):
    """Repository interface for Schedules entity."""

    @abstractmethod
    def create(self, schedule: ScheduleCreate) -> ScheduleResponse:
        pass

    @abstractmethod
    def get_by_id(self, schedule_id: UUID) -> Optional[ScheduleResponse]:
        pass

    @abstractmethod
    def list_by_project(self, project_id: UUID) -> List[ScheduleResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[ScheduleResponse]:
        pass

    @abstractmethod
    def update(self, schedule_id: UUID, payload: ScheduleUpdate) -> Optional[ScheduleResponse]:
        pass

    @abstractmethod
    def delete(self, schedule_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 3. WBS
class IWBSRepository(ABC):
    """Repository interface for WBS entity."""

    @abstractmethod
    def create(self, wbs: WBSCreate) -> WBSResponse:
        pass

    @abstractmethod
    def get_by_id(self, wbs_id: UUID) -> Optional[WBSResponse]:
        pass

    @abstractmethod
    def list_by_schedule(self, schedule_id: UUID) -> List[WBSResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[WBSResponse]:
        pass

    @abstractmethod
    def update(self, wbs_id: UUID, payload: WBSUpdate) -> Optional[WBSResponse]:
        pass

    @abstractmethod
    def delete(self, wbs_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 4. Activities
class IActivityRepository(ABC):
    """Repository interface for Activities entity."""

    @abstractmethod
    def create(self, activity: ScheduleActivityCreate) -> ScheduleActivityResponse:
        pass

    @abstractmethod
    def save_item(self, activity: ScheduleActivityResponse) -> ScheduleActivityResponse:
        pass

    @abstractmethod
    def get_by_id(self, activity_id: UUID) -> Optional[ScheduleActivityResponse]:
        pass

    @abstractmethod
    def get_by_code(self, activity_code: str) -> Optional[ScheduleActivityResponse]:
        pass

    @abstractmethod
    def list_by_project(self, project_id: UUID) -> List[ScheduleActivityResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[ScheduleActivityResponse]:
        pass

    @abstractmethod
    def update(self, activity_id: UUID, payload: ScheduleActivityUpdate) -> Optional[ScheduleActivityResponse]:
        pass

    @abstractmethod
    def delete(self, activity_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 5. Field Reports
class IFieldReportRepository(ABC):
    """Repository interface for Field Reports entity."""

    @abstractmethod
    def create(self, report: FieldReportCreate) -> FieldReportResponse:
        pass

    @abstractmethod
    def save_item(self, report: FieldReportResponse) -> FieldReportResponse:
        pass

    @abstractmethod
    def get_by_id(self, report_id: UUID) -> Optional[FieldReportResponse]:
        pass

    @abstractmethod
    def list_by_project(self, project_id: UUID) -> List[FieldReportResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[FieldReportResponse]:
        pass

    @abstractmethod
    def delete(self, report_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 6. Evidence
class IEvidenceRepository(ABC):
    """Repository interface for Evidence entity."""

    @abstractmethod
    def create(self, evidence: EvidenceCreate) -> EvidenceResponse:
        pass

    @abstractmethod
    def save_item(self, evidence: EvidenceResponse) -> EvidenceResponse:
        pass

    @abstractmethod
    def get_by_id(self, evidence_id: UUID) -> Optional[EvidenceResponse]:
        pass

    @abstractmethod
    def list_by_report(self, report_id: UUID) -> List[EvidenceResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[EvidenceResponse]:
        pass

    @abstractmethod
    def delete(self, evidence_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 7. Extracted Progress Events
class IExtractedProgressEventRepository(ABC):
    """Repository interface for Extracted Progress Events entity."""

    @abstractmethod
    def create(self, event: ExtractedProgressEventCreate) -> ExtractedProgressEventResponse:
        pass

    @abstractmethod
    def save_item(self, event: ExtractedProgressEventResponse) -> ExtractedProgressEventResponse:
        pass

    @abstractmethod
    def get_by_id(self, event_id: UUID) -> Optional[ExtractedProgressEventResponse]:
        pass

    @abstractmethod
    def list_by_report(self, report_id: UUID) -> List[ExtractedProgressEventResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[ExtractedProgressEventResponse]:
        pass

    @abstractmethod
    def delete(self, event_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 8. Activity Matches
class IActivityMatchRepository(ABC):
    """Repository interface for Activity Matches entity."""

    @abstractmethod
    def create(self, match: ActivityMatchCreate) -> ActivityMatchResponse:
        pass

    @abstractmethod
    def save_item(self, match: ActivityMatchResponse) -> ActivityMatchResponse:
        pass

    @abstractmethod
    def get_by_id(self, match_id: UUID) -> Optional[ActivityMatchResponse]:
        pass

    @abstractmethod
    def list_by_event(self, event_id: UUID) -> List[ActivityMatchResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[ActivityMatchResponse]:
        pass

    @abstractmethod
    def delete(self, match_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 9. Planner Reviews
class IPlannerReviewRepository(ABC):
    """Repository interface for Planner Reviews entity."""

    @abstractmethod
    def create(self, payload: ReviewItemCreate) -> ReviewItemResponse:
        pass

    @abstractmethod
    def save_item(self, review: ReviewItemResponse) -> ReviewItemResponse:
        pass

    @abstractmethod
    def get_by_id(self, review_id: UUID) -> Optional[ReviewItemResponse]:
        pass

    @abstractmethod
    def list_all(self, status: Optional[ReviewStatus] = None) -> List[ReviewItemResponse]:
        pass

    @abstractmethod
    def update(self, review_id: UUID, review: ReviewItemResponse) -> ReviewItemResponse:
        pass

    @abstractmethod
    def delete(self, review_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 10. Conflicts
class IConflictRepository(ABC):
    """Repository interface for Conflicts entity."""

    @abstractmethod
    def create(self, payload: ConflictCreate) -> ConflictResponse:
        pass

    @abstractmethod
    def save_item(self, conflict: ConflictResponse) -> ConflictResponse:
        pass

    @abstractmethod
    def get_by_id(self, conflict_id: UUID) -> Optional[ConflictResponse]:
        pass

    @abstractmethod
    def update(self, conflict_id: UUID, payload: ConflictUpdate) -> ConflictResponse:
        pass

    @abstractmethod
    def list_all(
        self,
        event_id: Optional[UUID] = None,
        resolution_status: Optional[str] = None,
    ) -> List[ConflictResponse]:
        pass

    @abstractmethod
    def delete(self, conflict_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 11. Actual Progress
class IActualProgressRepository(ABC):
    """Repository interface for Actual Progress entity."""

    @abstractmethod
    def create(self, progress: ProgressEventResponse) -> ProgressEventResponse:
        pass

    @abstractmethod
    def get_by_id(self, progress_id: UUID) -> Optional[ProgressEventResponse]:
        pass

    @abstractmethod
    def get_by_review_id(self, review_id: UUID) -> Optional[ProgressEventResponse]:
        pass

    @abstractmethod
    def list_all(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[ProgressStatus] = None,
    ) -> List[ProgressEventResponse]:
        pass

    @abstractmethod
    def delete(self, progress_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 12. Audit Logs
class IAuditLogRepository(ABC):
    """Repository interface for Audit Logs entity."""

    @abstractmethod
    def create(self, event: AuditEventCreate) -> AuditEventResponse:
        pass

    @abstractmethod
    def save_item(self, log: AuditEventResponse) -> AuditEventResponse:
        pass

    @abstractmethod
    def get_by_id(self, audit_id: UUID) -> Optional[AuditEventResponse]:
        pass

    @abstractmethod
    def list_all(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
    ) -> List[AuditEventResponse]:
        pass

    @abstractmethod
    def delete(self, audit_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


# 13. Users
class IUserRepository(ABC):
    """Repository interface for Users entity."""

    @abstractmethod
    def create(self, user: UserCreate) -> UserResponse:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[UserResponse]:
        pass

    @abstractmethod
    def update(self, user_id: UUID, payload: UserUpdate) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
