"""
Report Pipeline Orchestrator & Decision Recommendation Module for SIH26122.

Executes the end-to-end AI processing workflow:
  1. Extraction (Step 5.3)
  2. Activity Matching (Step 6.2)
  3. Confidence Scoring (Step 7.1)
  4. Conflict Detection (Step 7.2)
  5. Decision Recommendation Engine (Step 7.3)

Enforces strict decision priority (CRITICAL_REVIEW > HUMAN_REVIEW > AUTO_APPROVE).
All AI outputs recommend actions only; human validation is mandatory (human_validation_required=True).
"""

from dataclasses import dataclass, field
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ai.data.schedule_context import ActivityContext
from ai.data.schedule_loader import ScheduleDataset
from ai.extraction.extractor import ProgressEventExtractor
from ai.extraction.schemas import ExtractedProgressEvent, ExtractionStatus
from ai.matching.matcher import ActivityMatcher, MatchResult, MatchStatus
from ai.confidence.confidence_scorer import ConfidenceLevel, ConfidenceResult, ConfidenceScorer
from ai.conflict.conflict_detector import ConflictDetector, ConflictResult, ConflictSeverity


class RecommendedAction(str, Enum):
    """
    Categorical decision recommendation produced by the AI pipeline engine.
    NOTE: AUTO_APPROVE represents an AI recommendation only; human validation remains mandatory.
    """
    AUTO_APPROVE = "auto_approve"
    HUMAN_REVIEW = "human_review"
    CRITICAL_REVIEW = "critical_review"


@dataclass
class PipelineResult:
    """
    Comprehensive, explainable output encapsulating all stage results and decision recommendation.
    """
    report_id: str
    recommended_action: RecommendedAction
    human_validation_required: bool  # MANDATORY: Always True
    decision_reasons: List[str]
    event: ExtractedProgressEvent
    match_result: MatchResult
    confidence_result: ConfidenceResult
    conflict_result: ConflictResult
    processed_at: str


class ReportPipeline:
    """
    Offline, deterministic end-to-end pipeline orchestrator for field reports.
    Synthesizes extraction, activity matching, confidence scoring, and conflict detection outputs.
    """

    @classmethod
    def process_report(
        cls,
        report_input: Union[ExtractedProgressEvent, Dict[str, Any], str],
        schedule_target: Union[ScheduleDataset, List[ActivityContext], Dict[str, ActivityContext]],
        top_k: int = 5,
    ) -> PipelineResult:
        """
        Process a single field report through all AI pipeline stages and determine decision recommendation.
        
        Args:
            report_input: ExtractedProgressEvent, dict containing report fields, or raw report string.
            schedule_target: ScheduleDataset, list of ActivityContexts, or dict of ActivityContexts.
            top_k: Candidate retrieval pool size.
            
        Returns:
            Structured PipelineResult object.
        """
        # Step 1: Extraction Stage
        if isinstance(report_input, ExtractedProgressEvent):
            event = report_input
        elif isinstance(report_input, dict):
            report_id = str(report_input.get("report_id", "REP-UNK"))
            raw_text = str(report_input.get("raw_text", ""))
            report_date = report_input.get("report_date")
            event = ProgressEventExtractor.extract_from_report(
                report_id=report_id,
                raw_text=raw_text,
                report_date=report_date,
            )
        elif isinstance(report_input, str):
            event = ProgressEventExtractor.extract_from_report(
                report_id="REP-RAW",
                raw_text=report_input,
            )
        else:
            raise ValueError(f"Unsupported report_input type: {type(report_input)}")

        # Step 2: Activity Matching Stage
        match_result = ActivityMatcher.match_event(
            event=event,
            schedule_target=schedule_target,
            top_k=top_k,
        )

        # Step 3: Confidence Scoring Stage
        confidence_result = ConfidenceScorer.calculate_confidence(
            event=event,
            match_result=match_result,
        )

        # Step 4: Conflict Detection Stage
        conflict_result = ConflictDetector.evaluate_conflicts(
            events=event,
            match_result=match_result,
        )

        # Step 5: Decision Recommendation Engine
        action, decision_reasons = cls._evaluate_decision_recommendation(
            event=event,
            match_result=match_result,
            confidence_result=confidence_result,
            conflict_result=conflict_result,
        )

        processed_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return PipelineResult(
            report_id=event.report_id,
            recommended_action=action,
            human_validation_required=True,  # Mandatory: AI never auto-applies schedule changes directly
            decision_reasons=decision_reasons,
            event=event,
            match_result=match_result,
            confidence_result=confidence_result,
            conflict_result=conflict_result,
            processed_at=processed_timestamp,
        )

    @classmethod
    def process_batch(
        cls,
        report_inputs: List[Union[ExtractedProgressEvent, Dict[str, Any], str]],
        schedule_target: Union[ScheduleDataset, List[ActivityContext], Dict[str, ActivityContext]],
        top_k: int = 5,
    ) -> List[PipelineResult]:
        """
        Process a list of field reports deterministically and evaluate cross-report stream conflicts.
        
        Args:
            report_inputs: List of report inputs.
            schedule_target: Schedule dataset or activity contexts.
            top_k: Candidate retrieval pool size.
            
        Returns:
            List of PipelineResult objects.
        """
        single_results: List[PipelineResult] = [
            cls.process_report(inp, schedule_target, top_k=top_k)
            for inp in report_inputs
        ]

        if len(single_results) < 2:
            return single_results

        # Group events by matched activity_id to detect stream conflicts across reports
        activity_events_map: Dict[str, List[ExtractedProgressEvent]] = {}
        for res in single_results:
            act_id = res.match_result.matched_activity_id
            if act_id:
                activity_events_map.setdefault(act_id, []).append(res.event)

        multi_conflicts_map: Dict[str, ConflictResult] = {}
        for act_id, ev_list in activity_events_map.items():
            if len(ev_list) > 1:
                stream_res = ConflictDetector.evaluate_conflicts(events=ev_list)
                if stream_res.has_conflict:
                    multi_conflicts_map[act_id] = stream_res

        # Re-evaluate decision for reports affected by multi-report stream conflicts
        final_results: List[PipelineResult] = []
        for res in single_results:
            act_id = res.match_result.matched_activity_id
            if act_id and act_id in multi_conflicts_map:
                stream_conflict = multi_conflicts_map[act_id]
                # Merge multi-report conflicts into existing conflict result
                combined_conflicts = list(res.conflict_result.conflicts)
                for sc in stream_conflict.conflicts:
                    if sc.conflict_id not in {c.conflict_id for c in combined_conflicts}:
                        combined_conflicts.append(sc)

                highest_sev = res.conflict_result.highest_severity
                if stream_conflict.highest_severity:
                    if stream_conflict.highest_severity == ConflictSeverity.HIGH or highest_sev is None:
                        highest_sev = stream_conflict.highest_severity

                updated_conflict_result = ConflictResult(
                    has_conflict=len(combined_conflicts) > 0,
                    highest_severity=highest_sev,
                    conflicts=combined_conflicts,
                    report_count_evaluated=res.conflict_result.report_count_evaluated,
                    activity_id=act_id,
                    summary=f"Evaluated report stream for activity {act_id}. Flagged {len(combined_conflicts)} conflict(s).",
                )

                # Re-evaluate decision with updated stream conflicts
                new_action, new_reasons = cls._evaluate_decision_recommendation(
                    event=res.event,
                    match_result=res.match_result,
                    confidence_result=res.confidence_result,
                    conflict_result=updated_conflict_result,
                )

                final_results.append(
                    PipelineResult(
                        report_id=res.report_id,
                        recommended_action=new_action,
                        human_validation_required=True,
                        decision_reasons=new_reasons,
                        event=res.event,
                        match_result=res.match_result,
                        confidence_result=res.confidence_result,
                        conflict_result=updated_conflict_result,
                        processed_at=res.processed_at,
                    )
                )
            else:
                final_results.append(res)

        return final_results

    @classmethod
    def _evaluate_decision_recommendation(
        cls,
        event: ExtractedProgressEvent,
        match_result: MatchResult,
        confidence_result: ConfidenceResult,
        conflict_result: ConflictResult,
    ) -> Tuple[RecommendedAction, List[str]]:
        """
        Evaluate intermediate stage outputs against strict decision priority rules.
        Precedence Order: CRITICAL_REVIEW > HUMAN_REVIEW > AUTO_APPROVE.
        
        Returns:
            Tuple of (RecommendedAction, List of explainable decision reasons).
        """
        reasons: List[str] = []

        # Gather explainable reasons from previous stages
        if match_result.match_reasons:
            reasons.extend([f"match:{r}" for r in match_result.match_reasons[:3]])

        if confidence_result.confidence_reasons:
            reasons.extend([f"confidence:{r}" for r in confidence_result.confidence_reasons[:3]])

        if conflict_result.conflicts:
            for c in conflict_result.conflicts:
                reasons.append(f"conflict:{c.conflict_type.value}:{c.severity.value}:{c.description}")

        # Rule 1: CRITICAL_REVIEW (Highest Precedence)
        # Triggered by high-severity conflict or NO_MATCH status
        is_high_severity_conflict = (
            conflict_result.has_conflict and conflict_result.highest_severity == ConflictSeverity.HIGH
        )
        is_no_match = match_result.match_status == MatchStatus.NO_MATCH

        if is_high_severity_conflict or is_no_match:
            if is_high_severity_conflict:
                reasons.insert(0, "decision:CRITICAL_REVIEW:high_severity_conflict_flagged")
            else:
                reasons.insert(0, "decision:CRITICAL_REVIEW:no_matching_activity_candidate_found")

            return RecommendedAction.CRITICAL_REVIEW, reasons

        # Rule 2: HUMAN_REVIEW (Medium Precedence)
        # Triggered by AMBIGUOUS match, partial extraction, medium/capped confidence, or non-critical conflicts
        is_ambiguous_match = match_result.match_status == MatchStatus.AMBIGUOUS
        is_partial_extraction = event.extraction_status != ExtractionStatus.COMPLETE
        is_medium_or_low_confidence = confidence_result.confidence_level in [ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        is_non_critical_conflict = conflict_result.has_conflict and conflict_result.highest_severity != ConflictSeverity.HIGH

        if is_ambiguous_match or is_non_critical_conflict or is_partial_extraction or is_medium_or_low_confidence:
            if is_ambiguous_match:
                reasons.insert(0, "decision:HUMAN_REVIEW:ambiguous_candidate_match")
            elif is_non_critical_conflict:
                reasons.insert(0, f"decision:HUMAN_REVIEW:non_critical_conflict_{conflict_result.highest_severity.value if conflict_result.highest_severity else 'flagged'}")
            elif is_partial_extraction:
                reasons.insert(0, f"decision:HUMAN_REVIEW:partial_extraction_status_{event.extraction_status.value}")
            else:
                reasons.insert(0, f"decision:HUMAN_REVIEW:confidence_level_{confidence_result.confidence_level.value}")

            return RecommendedAction.HUMAN_REVIEW, reasons

        # Rule 3: AUTO_APPROVE (Lowest Precedence - AI Recommendation Only)
        # Triggered ONLY when extraction is complete, match is unambiguous, confidence is high, and zero conflicts exist
        reasons.insert(0, "decision:AUTO_APPROVE:unambiguous_match_high_confidence_zero_conflicts")
        return RecommendedAction.AUTO_APPROVE, reasons
