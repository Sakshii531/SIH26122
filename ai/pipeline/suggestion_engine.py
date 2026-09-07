"""
AI Suggestion Data Model & Helper Module for SIH26122 (Phase 9).

Defines the formal AISuggestion model representing the multi-modal AI pipeline output.
All AI suggestions represent recommendations for human validation and never directly mutate project schedule data.
"""

from dataclasses import dataclass, field
import datetime
from typing import List, Optional

from ai.confidence.confidence_scorer import ConfidenceLevel
from ai.conflict.conflict_detector import ConflictSeverity
from ai.pipeline.report_pipeline import PipelineResult, RecommendedAction


@dataclass
class AISuggestion:
    """
    Structured, human-validatable AI Suggestion object produced by the multi-modal pipeline.
    """
    suggestion_id: str
    report_id: str
    source_type: str  # "text", "image_ocr", "audio_asr"
    recommended_action: RecommendedAction
    human_validation_required: bool  # MANDATORY: Always True
    target_activity_id: Optional[str]
    target_activity_code: Optional[str]
    target_activity_name: Optional[str]
    suggested_status: Optional[str]
    suggested_progress_value: Optional[float]
    suggested_start_date: Optional[datetime.date]
    suggested_finish_date: Optional[datetime.date]
    confidence_score: float
    confidence_level: ConfidenceLevel
    has_conflicts: bool
    highest_conflict_severity: Optional[ConflictSeverity]
    conflict_count: int
    decision_reasons: List[str]
    pipeline_result: PipelineResult


def build_ai_suggestion(pipeline_result: PipelineResult, source_type: str = "text") -> AISuggestion:
    """
    Build a formal AISuggestion instance from a PipelineResult object.
    
    Args:
        pipeline_result: Evaluated PipelineResult object.
        source_type: Input provenance ("text", "image_ocr", "audio_asr").
        
    Returns:
        Structured AISuggestion instance.
    """
    event = pipeline_result.event
    match = pipeline_result.match_result
    conf = pipeline_result.confidence_result
    conflict = pipeline_result.conflict_result

    target_act_id = match.matched_activity_id
    target_act_code = match.matched_activity_code
    target_act_name = match.matched_activity_name

    sugg_id = f"SUGG-{event.report_id}-{source_type.upper()}"

    return AISuggestion(
        suggestion_id=sugg_id,
        report_id=event.report_id,
        source_type=source_type,
        recommended_action=pipeline_result.recommended_action,
        human_validation_required=True,  # Mandatory: AI output is an unverified suggestion
        target_activity_id=target_act_id,
        target_activity_code=target_act_code,
        target_activity_name=target_act_name,
        suggested_status=event.status,
        suggested_progress_value=event.progress_value,
        suggested_start_date=event.actual_start,
        suggested_finish_date=event.actual_finish,
        confidence_score=conf.confidence_score,
        confidence_level=conf.confidence_level,
        has_conflicts=conflict.has_conflict,
        highest_conflict_severity=conflict.highest_severity,
        conflict_count=len(conflict.conflicts),
        decision_reasons=pipeline_result.decision_reasons,
        pipeline_result=pipeline_result,
    )
