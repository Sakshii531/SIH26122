from __future__ import annotations

from app.schemas.activity_match import (
    ActivityMatchBase,
    ActivityMatchCreate,
    ActivityMatchResponse,
)
from app.schemas.audit_event import (
    AuditEventBase,
    AuditEventCreate,
    AuditEventResponse,
)
from app.schemas.enums import (
    ActivityLevel,
    ActivityStatus,
    AuditEventType,
    FieldReportFormat,
    MatchStatus,
    ProgressStatus,
    ReviewDecision,
)
from app.schemas.field_report import (
    EvidenceItem,
    FieldReportBase,
    FieldReportCreate,
    FieldReportResponse,
)
from app.schemas.progress_event import (
    ProgressEventBase,
    ProgressEventCreate,
    ProgressEventResponse,
)
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.review import (
    ReviewBase,
    ReviewCreate,
    ReviewResponse,
)
from app.schemas.schedule_activity import (
    ScheduleActivityBase,
    ScheduleActivityCreate,
    ScheduleActivityResponse,
    ScheduleActivityUpdate,
)
from app.schemas.schedule_import import (
    ScheduleImportSummaryResponse,
    ScheduleRowValidationError,
)

from app.schemas.ai_contract import (
    ActivityMatchingRequest,
    ActivityMatchingResponse,
    AlternativeCandidateMatch,
    CandidateActivity,
    FieldReportExtractionRequest,
    FieldReportExtractionResponse,
)

__all__ = [
    # Enums
    "ActivityLevel",
    "ActivityStatus",
    "FieldReportFormat",
    "MatchStatus",
    "ReviewDecision",
    "ReviewStatus",
    "ProgressStatus",
    "AuditEventType",
    # Review Workflow
    "ReviewItemCreate",
    "ReviewDecisionRequest",
    "ReviewItemResponse",
    # Project
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    # Schedule Activity
    "ScheduleActivityBase",
    "ScheduleActivityCreate",
    "ScheduleActivityUpdate",
    "ScheduleActivityResponse",
    # Schedule Import
    "ScheduleRowValidationError",
    "ScheduleImportSummaryResponse",
    # Field Report
    "EvidenceItem",
    "FieldReportBase",
    "FieldReportCreate",
    "FieldReportResponse",
    # AI Contract
    "FieldReportExtractionRequest",
    "FieldReportExtractionResponse",
    "CandidateActivity",
    "ActivityMatchingRequest",
    "AlternativeCandidateMatch",
    "ActivityMatchingResponse",
    # Activity Match
    "ActivityMatchBase",
    "ActivityMatchCreate",
    "ActivityMatchResponse",
    # Review
    "ReviewBase",
    "ReviewCreate",
    "ReviewResponse",
    # Progress Event
    "ProgressEventBase",
    "ProgressEventCreate",
    "ProgressEventResponse",
    # Audit Event
    "AuditEventBase",
    "AuditEventCreate",
    "AuditEventResponse",
]


