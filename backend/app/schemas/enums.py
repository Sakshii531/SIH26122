from __future__ import annotations

from enum import Enum


class ActivityLevel(str, Enum):
    """Level of Schedule Activity in Primavera / MS Project (L5/L6)."""

    L5 = "L5"
    L6 = "L6"


class ActivityStatus(str, Enum):
    """Execution status of a Schedule Activity."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"
    SUSPENDED = "SUSPENDED"


class FieldReportFormat(str, Enum):
    """Input format of the field report."""

    TEXT = "TEXT"
    VOICE = "VOICE"
    DPR = "DPR"
    EXCEL = "EXCEL"
    PHOTO = "PHOTO"


class MatchStatus(str, Enum):
    """AI activity matching status."""

    AUTO_MATCHED = "AUTO_MATCHED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    MANUALLY_MATCHED = "MANUALLY_MATCHED"
    REJECTED = "REJECTED"
    UNMATCHED = "UNMATCHED"


class ReviewDecision(str, Enum):
    """Human planner review decision."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    CORRECTED = "CORRECTED"
    OVERRIDDEN = "OVERRIDDEN"


class ReviewStatus(str, Enum):
    """Status of a human review item."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"



class ProgressStatus(str, Enum):
    """Validated progress status."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"


class AuditEventType(str, Enum):
    """Category of audit trail event."""

    REPORT_SUBMITTED = "REPORT_SUBMITTED"
    AI_MATCH_GENERATED = "AI_MATCH_GENERATED"
    REVIEW_SUBMITTED = "REVIEW_SUBMITTED"
    PROGRESS_UPDATED = "PROGRESS_UPDATED"
    OVERRIDE_RECORDED = "OVERRIDE_RECORDED"
