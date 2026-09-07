"""
Conflict Detection Engine Module for SIH26122.

Defines deterministic, offline conflict detection logic for progress events extracted
from field reports, evaluating single events and multi-report activity streams for 
defects, progress contradictions, date inversions, status mismatches, and cross-report regression.
"""

from dataclasses import dataclass, field
import datetime
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Set, Union

from ai.extraction.schemas import ExtractedProgressEvent, EventStatus
from ai.matching.matcher import MatchResult


class ConflictType(str, Enum):
    """Categories of detected conflicts."""
    STATUS_CONTRADICTION = "status_contradiction"
    DATE_INCONSISTENCY = "date_inconsistency"
    PROGRESS_CONTRADICTION = "progress_contradiction"
    DEFECT_BREAKDOWN = "defect_breakdown"
    CROSS_REPORT_CONTRADICTION = "cross_report_contradiction"


class ConflictSeverity(str, Enum):
    """Severity ratings for detected conflicts."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ConflictDetail:
    """
    Structured detail of an individual flagged conflict.
    """
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    report_ids: List[str]
    activity_id: Optional[str]
    activity_code: Optional[str]
    description: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class ConflictResult:
    """
    Aggregated result of conflict detection for one or more evaluated field reports.
    """
    has_conflict: bool
    highest_severity: Optional[ConflictSeverity]
    conflicts: List[ConflictDetail]
    report_count_evaluated: int
    activity_id: Optional[str]
    summary: str


class ConflictDetector:
    """
    Offline, deterministic conflict detector for site field reports and schedule activities.
    Flags contradictions without altering underlying schedule or event data.
    """

    DEFECT_KEYWORDS: List[str] = [
        "honeycombing",
        "breakdown",
        "flagged",
        "repair",
        "rework",
        "halted",
        "crack",
        "failed inspection",
        "defect",
        "faulty",
        "damage",
    ]

    INCOMPLETE_KEYWORDS: List[str] = [
        "halted",
        "incomplete",
        "pending repair",
        "partially done",
        "rework needed",
        "issue",
        "delay",
        "stopped",
        "failed",
    ]

    @classmethod
    def detect_single_report_conflicts(
        cls,
        event: ExtractedProgressEvent,
        match_result: Optional[MatchResult] = None,
        schedule_activity: Optional[Dict[str, Any]] = None,
    ) -> List[ConflictDetail]:
        """
        Detect conflicts within a single extracted progress event and its matched schedule activity.
        
        Args:
            event: ExtractedProgressEvent object.
            match_result: Optional MatchResult object from ActivityMatcher.
            schedule_activity: Optional dictionary representing schedule activity.
            
        Returns:
            List of ConflictDetail objects.
        """
        conflicts: List[ConflictDetail] = []
        
        # Resolve activity ID and code references
        act_id = None
        act_code = None
        if match_result and match_result.matched_activity_id:
            act_id = match_result.matched_activity_id
            act_code = match_result.matched_activity_code
        elif schedule_activity:
            act_id = schedule_activity.get("activity_id")
            act_code = schedule_activity.get("activity_code")

        full_text = f"{event.activity_description or ''} {event.extracted_text or ''}".lower()

        # Rule 1: Defect / Breakdown Detection
        for kw in cls.DEFECT_KEYWORDS:
            if kw in full_text:
                conflicts.append(
                    ConflictDetail(
                        conflict_id=f"CONF-DEFECT-{event.report_id}-{kw.upper()}",
                        conflict_type=ConflictType.DEFECT_BREAKDOWN,
                        severity=ConflictSeverity.HIGH,
                        report_ids=[event.report_id],
                        activity_id=act_id,
                        activity_code=act_code,
                        description=f"Site report indicates defect, repair, or equipment breakdown ('{kw}')",
                        evidence=[
                            f"Matched keyword '{kw}' in report text: '{event.extracted_text or event.activity_description}'"
                        ],
                    )
                )
                break  # Flag highest priority defect keyword per report

        # Rule 2: Progress vs Text Contradiction
        if event.progress_value is not None and event.progress_value >= 100.0:
            for kw in cls.INCOMPLETE_KEYWORDS:
                if kw in full_text:
                    conflicts.append(
                        ConflictDetail(
                            conflict_id=f"CONF-PROG-{event.report_id}",
                            conflict_type=ConflictType.PROGRESS_CONTRADICTION,
                            severity=ConflictSeverity.HIGH,
                            report_ids=[event.report_id],
                            activity_id=act_id,
                            activity_code=act_code,
                            description=f"Progress value claimed 100.0% but report text indicates incomplete status ('{kw}')",
                            evidence=[
                                f"Extracted progress 100.0% conflicts with caveat text containing '{kw}': '{event.extracted_text or event.activity_description}'"
                            ],
                        )
                    )
                    break

        # Rule 3: Inverted Date Logic
        if event.actual_start and event.actual_finish:
            if event.actual_start > event.actual_finish:
                conflicts.append(
                    ConflictDetail(
                        conflict_id=f"CONF-DATE-{event.report_id}",
                        conflict_type=ConflictType.DATE_INCONSISTENCY,
                        severity=ConflictSeverity.HIGH,
                        report_ids=[event.report_id],
                        activity_id=act_id,
                        activity_code=act_code,
                        description=f"Extracted actual_start ({event.actual_start}) is after actual_finish ({event.actual_finish})",
                        evidence=[
                            f"actual_start: {event.actual_start.isoformat()} > actual_finish: {event.actual_finish.isoformat()}"
                        ],
                    )
                )

        # Rule 4: Extracted Status vs Schedule Baseline Status
        baseline_status = None
        if match_result and match_result.matched_context:
            baseline_status = match_result.matched_context.status
        elif schedule_activity:
            baseline_status = schedule_activity.get("status")

        if baseline_status and event.status:
            b_norm = str(baseline_status).strip().lower()
            e_norm = str(event.status).strip().lower()
            if b_norm != e_norm:
                # Contradiction when baseline is Not Started but event is Completed, or baseline is Completed but event is Not Started / In Progress
                if (b_norm == "not started" and e_norm == "completed") or (b_norm == "completed" and e_norm in ["not started", "in progress"]):
                    conflicts.append(
                        ConflictDetail(
                            conflict_id=f"CONF-STATUS-{event.report_id}",
                            conflict_type=ConflictType.STATUS_CONTRADICTION,
                            severity=ConflictSeverity.MEDIUM,
                            report_ids=[event.report_id],
                            activity_id=act_id,
                            activity_code=act_code,
                            description=f"Extracted status '{event.status}' conflicts with schedule baseline status '{baseline_status}'",
                            evidence=[
                                f"Extracted status: '{event.status}' vs Schedule baseline status: '{baseline_status}'"
                            ],
                        )
                    )

        return conflicts

    @classmethod
    def detect_multi_report_conflicts(
        cls,
        events: List[ExtractedProgressEvent],
        activity_id: Optional[str] = None,
    ) -> List[ConflictDetail]:
        """
        Detect cross-report contradictions across multiple field reports referencing the same activity.
        
        Args:
            events: List of ExtractedProgressEvent objects.
            activity_id: Optional activity ID associated with the report stream.
            
        Returns:
            List of ConflictDetail objects.
        """
        if len(events) < 2:
            return []

        conflicts: List[ConflictDetail] = []

        # Sort events deterministically by date if available, then by report_id
        def sort_key(e: ExtractedProgressEvent):
            d = e.actual_finish or e.actual_start or datetime.date.min
            return (d, e.report_id)

        sorted_events = sorted(events, key=sort_key)

        for i in range(len(sorted_events) - 1):
            e1 = sorted_events[i]
            e2 = sorted_events[i + 1]

            # Rule 2.1: Cross-report status regression (Completed -> In Progress / Not Started)
            if e1.status and e2.status:
                s1 = e1.status.strip().lower()
                s2 = e2.status.strip().lower()
                if s1 == "completed" and s2 in ["in progress", "not started"]:
                    conflicts.append(
                        ConflictDetail(
                            conflict_id=f"CONF-CROSS-STATUS-{e1.report_id}-{e2.report_id}",
                            conflict_type=ConflictType.CROSS_REPORT_CONTRADICTION,
                            severity=ConflictSeverity.HIGH,
                            report_ids=[e1.report_id, e2.report_id],
                            activity_id=activity_id,
                            activity_code=None,
                            description=f"Status regression across reports: '{e1.status}' in {e1.report_id} followed by '{e2.status}' in {e2.report_id}",
                            evidence=[
                                f"Report {e1.report_id} claimed status '{e1.status}', but subsequent report {e2.report_id} claimed status '{e2.status}'"
                            ],
                        )
                    )

            # Rule 2.2: Cross-report progress variance (e.g. 100% -> 40%)
            if e1.progress_value is not None and e2.progress_value is not None:
                p1 = e1.progress_value
                p2 = e2.progress_value
                if p1 >= 90.0 and p2 <= 50.0:
                    conflicts.append(
                        ConflictDetail(
                            conflict_id=f"CONF-CROSS-PROG-{e1.report_id}-{e2.report_id}",
                            conflict_type=ConflictType.CROSS_REPORT_CONTRADICTION,
                            severity=ConflictSeverity.HIGH,
                            report_ids=[e1.report_id, e2.report_id],
                            activity_id=activity_id,
                            activity_code=None,
                            description=f"Significant progress contradiction across reports: {p1}% in {e1.report_id} vs {p2}% in {e2.report_id}",
                            evidence=[
                                f"Report {e1.report_id} claimed progress {p1}%, but report {e2.report_id} claimed progress {p2}%"
                            ],
                        )
                    )

        return conflicts

    @classmethod
    def evaluate_conflicts(
        cls,
        events: Union[ExtractedProgressEvent, List[ExtractedProgressEvent]],
        match_result: Optional[MatchResult] = None,
        schedule_activity: Optional[Dict[str, Any]] = None,
    ) -> ConflictResult:
        """
        Evaluate single or multiple extracted field reports for conflicts.
        
        Args:
            events: Single ExtractedProgressEvent or list of ExtractedProgressEvent objects.
            match_result: Optional MatchResult object.
            schedule_activity: Optional dictionary representing schedule activity.
            
        Returns:
            Structured ConflictResult object.
        """
        if isinstance(events, ExtractedProgressEvent):
            event_list = [events]
        else:
            event_list = events

        conflicts: List[ConflictDetail] = []
        for ev in event_list:
            single_conflicts = cls.detect_single_report_conflicts(
                event=ev,
                match_result=match_result,
                schedule_activity=schedule_activity,
            )
            conflicts.extend(single_conflicts)

        act_id = None
        if match_result and match_result.matched_activity_id:
            act_id = match_result.matched_activity_id
        elif schedule_activity:
            act_id = schedule_activity.get("activity_id")

        if len(event_list) > 1:
            multi_conflicts = cls.detect_multi_report_conflicts(
                events=event_list,
                activity_id=act_id,
            )
            conflicts.extend(multi_conflicts)

        highest_severity: Optional[ConflictSeverity] = None
        if conflicts:
            severities = {c.severity for c in conflicts}
            if ConflictSeverity.HIGH in severities:
                highest_severity = ConflictSeverity.HIGH
            elif ConflictSeverity.MEDIUM in severities:
                highest_severity = ConflictSeverity.MEDIUM
            elif ConflictSeverity.LOW in severities:
                highest_severity = ConflictSeverity.LOW

        summary = f"Evaluated {len(event_list)} report(s). Flagged {len(conflicts)} conflict(s)."
        if highest_severity:
            summary += f" Highest severity: {highest_severity.value}."

        return ConflictResult(
            has_conflict=len(conflicts) > 0,
            highest_severity=highest_severity,
            conflicts=conflicts,
            report_count_evaluated=len(event_list),
            activity_id=act_id,
            summary=summary,
        )
