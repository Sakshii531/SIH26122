from __future__ import annotations

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.schemas.evidence import (
    EvidenceBase,
    EvidenceCreate,
    EvidenceResponse,
)
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.schedule import (
    ScheduleBase,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)
from app.schemas.wbs import (
    WBSBase,
    WBSCreate,
    WBSResponse,
    WBSUpdate,
)
from app.schemas.activity import (
    ActivityBase,
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    # Backward compatibility
    ScheduleActivityBase,
    ScheduleActivityCreate,
    ScheduleActivityResponse,
    ScheduleActivityUpdate,
)
from app.schemas.field_report import (
    EvidenceItem,
    FieldReportBase,
    FieldReportCreate,
    FieldReportResponse,
)
from app.schemas.extracted_progress_event import (
    ExtractedProgressEventBase,
    ExtractedProgressEventCreate,
    ExtractedProgressEventResponse,
)
from app.schemas.activity_match import (
    ActivityMatchBase,
    ActivityMatchCreate,
    ActivityMatchResponse,
)
from app.schemas.planner_review import (
    PlannerReviewBase,
    PlannerReviewCreate,
    PlannerReviewResponse,
    # Backward compatibility
    ReviewBase,
    ReviewCreate,
    ReviewResponse,
)
from app.schemas.conflict import (
    ConflictBase,
    ConflictCreate,
    ConflictResponse,
    ConflictUpdate,
)
from app.schemas.actual_progress import (
    ActualProgressBase,
    ActualProgressCreate,
    ActualProgressResponse,
)
from app.schemas.audit_log import (
    AuditLogBase,
    AuditLogCreate,
    AuditLogResponse,
    # Backward compatibility
    AuditEventBase,
    AuditEventCreate,
    AuditEventResponse,
)

# ── Enums ─────────────────────────────────────────────────────────────────────
from app.schemas.enums import (
    ActivityLevel,
    ActivityStatus,
    AuditEventType,
    FieldReportFormat,
    MatchStatus,
    ProgressStatus,
    ReviewDecision,
    ReviewStatus,
)

# ── Workflow & requests ───────────────────────────────────────────────────────
from app.schemas.progress_event import (
    ProgressEventBase,
    ProgressEventCreate,
    ProgressEventResponse,
)
from app.schemas.progress_request import ProgressFromReviewCreate
from app.schemas.review_workflow import (
    ReviewDecisionRequest,
    ReviewItemCreate,
    ReviewItemResponse,
)

# ── Import & scheduling ───────────────────────────────────────────────────────
from app.schemas.schedule_import import (
    ScheduleImportSummaryResponse,
    ScheduleRowValidationError,
)

# ── AI contract ───────────────────────────────────────────────────────────────
from app.schemas.ai_contract import (
    ActivityMatchingRequest,
    ActivityMatchingResponse,
    AlternativeCandidateMatch,
    CandidateActivity,
    FieldReportExtractionRequest,
    FieldReportExtractionResponse,
)

# ── Dashboard ─────────────────────────────────────────────────────────────────
from app.schemas.dashboard import (
    ActivityReportItem,
    ActivityReportResponse,
    DashboardSummaryResponse,
    ProjectExecutionSummary,
    RecentActivityItem,
    RecentActivityResponse,
)

__all__ = [
    # ── Enums ─────────────────────────────────────────────────────────────────
    "ActivityLevel",
    "ActivityStatus",
    "AuditEventType",
    "FieldReportFormat",
    "MatchStatus",
    "ProgressStatus",
    "ReviewDecision",
    "ReviewStatus",
    # ── Core ER entities ──────────────────────────────────────────────────────
    "UserRole",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "EvidenceBase",
    "EvidenceCreate",
    "EvidenceResponse",
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ScheduleBase",
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "WBSBase",
    "WBSCreate",
    "WBSUpdate",
    "WBSResponse",
    "ActivityBase",
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityResponse",
    "ScheduleActivityBase",  # backward compat
    "ScheduleActivityCreate",  # backward compat
    "ScheduleActivityUpdate",  # backward compat
    "ScheduleActivityResponse",  # backward compat
    "EvidenceItem",
    "FieldReportBase",
    "FieldReportCreate",
    "FieldReportResponse",
    "ExtractedProgressEventBase",
    "ExtractedProgressEventCreate",
    "ExtractedProgressEventResponse",
    "ActivityMatchBase",
    "ActivityMatchCreate",
    "ActivityMatchResponse",
    "PlannerReviewBase",
    "PlannerReviewCreate",
    "PlannerReviewResponse",
    "ReviewBase",  # backward compat
    "ReviewCreate",  # backward compat
    "ReviewResponse",  # backward compat
    "ConflictBase",
    "ConflictCreate",
    "ConflictUpdate",
    "ConflictResponse",
    "ActualProgressBase",
    "ActualProgressCreate",
    "ActualProgressResponse",
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogResponse",
    "AuditEventBase",  # backward compat
    "AuditEventCreate",  # backward compat
    "AuditEventResponse",  # backward compat
    # ── Workflow & requests ───────────────────────────────────────────────────
    "ProgressEventBase",
    "ProgressEventCreate",
    "ProgressEventResponse",
    "ProgressFromReviewCreate",
    "ReviewItemCreate",
    "ReviewDecisionRequest",
    "ReviewItemResponse",
    # ── Import & scheduling ───────────────────────────────────────────────────
    "ScheduleRowValidationError",
    "ScheduleImportSummaryResponse",
    # ── AI contract ───────────────────────────────────────────────────────────
    "FieldReportExtractionRequest",
    "FieldReportExtractionResponse",
    "CandidateActivity",
    "ActivityMatchingRequest",
    "AlternativeCandidateMatch",
    "ActivityMatchingResponse",
    # ── Dashboard ─────────────────────────────────────────────────────────────
    "DashboardSummaryResponse",
    "ProjectExecutionSummary",
    "ActivityReportItem",
    "ActivityReportResponse",
    "RecentActivityItem",
    "RecentActivityResponse",
]


