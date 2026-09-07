"""
Report Pipeline Orchestrator & Decision Recommendation Module for SIH26122.

Executes the end-to-end multi-modal AI processing workflow:
  1. Input Processing / OCR / ASR (Step 7.4 / Phase 8)
  2. Text Progress Extraction (Step 5.3)
  3. L5/L6 Activity Matching (Step 6.2)
  4. Confidence Scoring (Step 7.1)
  5. Conflict Detection (Step 7.2)
  6. Decision Recommendation Engine (Step 7.3)
  7. Multi-Modal AISuggestion Formatting (Phase 9)

Enforces strict decision priority (CRITICAL_REVIEW > HUMAN_REVIEW > AUTO_APPROVE).
All AI outputs recommend actions only; human validation is mandatory (human_validation_required=True).
"""

from dataclasses import dataclass, field
import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ai.asr.asr_processor import ASRProcessor
from ai.confidence.confidence_scorer import ConfidenceLevel, ConfidenceResult, ConfidenceScorer
from ai.conflict.conflict_detector import ConflictDetail, ConflictDetector, ConflictResult, ConflictSeverity, ConflictType
from ai.data.schedule_context import ActivityContext
from ai.data.schedule_loader import ScheduleDataset
from ai.extraction.extractor import ProgressEventExtractor
from ai.extraction.schemas import EventStatus, ExtractedProgressEvent, ExtractionStatus
from ai.matching.matcher import ActivityMatcher, MatchResult, MatchStatus
from ai.ocr.ocr_processor import OCRProcessor


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
    Synthesizes extraction, activity matching, confidence scoring, conflict detection, and multi-modal suggestions.
    """

    IMAGE_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]
    AUDIO_EXTENSIONS: List[str] = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".wma"]

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
    def process_input(
        cls,
        input_data: Union[ExtractedProgressEvent, Dict[str, Any], str, Path],
        schedule_target: Union[ScheduleDataset, List[ActivityContext], Dict[str, ActivityContext]],
        top_k: int = 5,
        mock_asr_transcript: Optional[str] = None,
    ) -> Any:
        """
        Process any multi-modal input (text, OCR image path, or ASR audio path) and return an AISuggestion.
        Import inside method to avoid circular imports.
        """
        from ai.pipeline.suggestion_engine import AISuggestion, build_ai_suggestion

        if isinstance(input_data, AISuggestion):
            return input_data

        all_known_extensions = cls.IMAGE_EXTENSIONS + cls.AUDIO_EXTENSIONS + [".txt"]
        is_path_input = False

        if isinstance(input_data, Path):
            is_path_input = True
        elif isinstance(input_data, str):
            # Check if input string is a valid path or ends with a known media extension
            s_lower = input_data.lower()
            if any(s_lower.endswith(ext) for ext in all_known_extensions) or Path(input_data).exists():
                is_path_input = True

        if is_path_input:
            path_candidate = Path(input_data)
            ext = path_candidate.suffix.lower()
            report_id = f"REP-{path_candidate.stem.upper()}"

            # Case A: Image file -> OCR Processing
            if ext in cls.IMAGE_EXTENSIONS:
                source_type = "image_ocr"
                ocr_res = OCRProcessor.process_image(path_candidate)
                if not ocr_res.success:
                    return cls._create_failed_processing_suggestion(
                        report_id=report_id,
                        source_type=source_type,
                        error_message=ocr_res.error or "OCR processing failed.",
                        path_name=path_candidate.name,
                    )
                extracted_text = ocr_res.extracted_text
                event = ProgressEventExtractor.extract_from_report(
                    report_id=report_id,
                    raw_text=extracted_text,
                )
                pipeline_res = cls.process_report(event, schedule_target, top_k=top_k)
                return build_ai_suggestion(pipeline_res, source_type=source_type)

            # Case B: Audio file -> ASR Processing
            elif ext in cls.AUDIO_EXTENSIONS:
                source_type = "audio_asr"
                asr_res = ASRProcessor.process_audio(
                    path_candidate,
                    mock_transcription=mock_asr_transcript,
                )
                if not asr_res.success:
                    return cls._create_failed_processing_suggestion(
                        report_id=report_id,
                        source_type=source_type,
                        error_message=asr_res.error or "ASR processing failed.",
                        path_name=path_candidate.name,
                    )
                extracted_text = asr_res.transcribed_text
                event = ProgressEventExtractor.extract_from_report(
                    report_id=report_id,
                    raw_text=extracted_text,
                )
                pipeline_res = cls.process_report(event, schedule_target, top_k=top_k)
                return build_ai_suggestion(pipeline_res, source_type=source_type)

            # Case C: Plain text file (.txt)
            elif ext == ".txt":
                source_type = "text"
                if path_candidate.exists():
                    extracted_text = path_candidate.read_text(encoding="utf-8").strip()
                    event = ProgressEventExtractor.extract_from_report(
                        report_id=report_id,
                        raw_text=extracted_text,
                    )
                    pipeline_res = cls.process_report(event, schedule_target, top_k=top_k)
                    return build_ai_suggestion(pipeline_res, source_type=source_type)
                else:
                    return cls._create_failed_processing_suggestion(
                        report_id=report_id,
                        source_type=source_type,
                        error_message=f"Text file not found: '{path_candidate}'",
                        path_name=path_candidate.name,
                    )

        # Standard text report (str/dict/ExtractedProgressEvent)
        pipeline_res = cls.process_report(input_data, schedule_target, top_k=top_k)
        return build_ai_suggestion(pipeline_res, source_type="text")

    @classmethod
    def process_heterogeneous_batch(
        cls,
        inputs: List[Union[ExtractedProgressEvent, Dict[str, Any], str, Path]],
        schedule_target: Union[ScheduleDataset, List[ActivityContext], Dict[str, ActivityContext]],
        top_k: int = 5,
    ) -> List[Any]:
        """
        Process a mixed batch of heterogeneous inputs (text, OCR image paths, ASR audio paths).
        Individual failures do not block processing of remaining batch items.
        """
        suggestions: List[Any] = []
        for inp in inputs:
            try:
                sugg = cls.process_input(inp, schedule_target, top_k=top_k)
                suggestions.append(sugg)
            except Exception as ex:
                rep_id = "REP-BATCH-ERR"
                if isinstance(inp, dict):
                    rep_id = str(inp.get("report_id", rep_id))
                elif isinstance(inp, (str, Path)):
                    p = Path(inp)
                    if p.suffix:
                        rep_id = f"REP-{p.stem.upper()}"
                suggestions.append(
                    cls._create_failed_processing_suggestion(
                        report_id=rep_id,
                        source_type="text",
                        error_message=f"Batch processing error: {str(ex)}",
                        path_name=str(inp),
                    )
                )
        return suggestions

    @classmethod
    def _create_failed_processing_suggestion(
        cls,
        report_id: str,
        source_type: str,
        error_message: str,
        path_name: str,
    ) -> Any:
        """Helper to format a structured AISuggestion with CRITICAL_REVIEW when OCR or ASR fails."""
        from ai.pipeline.suggestion_engine import AISuggestion

        event = ExtractedProgressEvent(
            report_id=report_id,
            activity_description=f"Input Processing Failure ({source_type}): {path_name}",
            extraction_status=ExtractionStatus.NEEDS_REVIEW,
        )

        match_res = MatchResult(
            matched_activity_id=None,
            matched_activity_code=None,
            matched_activity_name=None,
            matched_level=None,
            matched_discipline=None,
            match_score=0.0,
            match_status=MatchStatus.NO_MATCH,
            ranked_candidates=[],
            match_reasons=[f"{source_type}_processing_failed"],
        )

        conf_res = ConfidenceResult(
            confidence_score=0.0,
            confidence_level=ConfidenceLevel.LOW,
            match_status=MatchStatus.NO_MATCH,
            matched_activity_id=None,
            matched_activity_code=None,
            signal_breakdown={},
            confidence_reasons=[f"{source_type}_failure"],
        )

        conflict_detail = ConflictDetail(
            conflict_id=f"CONF-{source_type.upper()}-FAIL-{report_id}",
            conflict_type=ConflictType.DEFECT_BREAKDOWN,
            severity=ConflictSeverity.HIGH,
            report_ids=[report_id],
            activity_id=None,
            activity_code=None,
            description=error_message,
            evidence=[error_message],
        )

        conflict_res = ConflictResult(
            has_conflict=True,
            highest_severity=ConflictSeverity.HIGH,
            conflicts=[conflict_detail],
            report_count_evaluated=1,
            activity_id=None,
            summary=f"Input processing failed for {source_type}: {error_message}",
        )

        pipeline_res = PipelineResult(
            report_id=report_id,
            recommended_action=RecommendedAction.CRITICAL_REVIEW,
            human_validation_required=True,
            decision_reasons=[
                f"decision:CRITICAL_REVIEW:{source_type}_input_processing_failed",
                error_message,
            ],
            event=event,
            match_result=match_res,
            confidence_result=conf_res,
            conflict_result=conflict_res,
            processed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        sugg_id = f"SUGG-{report_id}-{source_type.upper()}"
        return AISuggestion(
            suggestion_id=sugg_id,
            report_id=report_id,
            source_type=source_type,
            recommended_action=RecommendedAction.CRITICAL_REVIEW,
            human_validation_required=True,  # Mandatory
            target_activity_id=None,
            target_activity_code=None,
            target_activity_name=None,
            suggested_status=None,
            suggested_progress_value=None,
            suggested_start_date=None,
            suggested_finish_date=None,
            confidence_score=0.0,
            confidence_level=ConfidenceLevel.LOW,
            has_conflicts=True,
            highest_conflict_severity=ConflictSeverity.HIGH,
            conflict_count=1,
            decision_reasons=pipeline_res.decision_reasons,
            pipeline_result=pipeline_res,
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

        if match_result.match_reasons:
            reasons.extend([f"match:{r}" for r in match_result.match_reasons[:3]])

        if confidence_result.confidence_reasons:
            reasons.extend([f"confidence:{r}" for r in confidence_result.confidence_reasons[:3]])

        if conflict_result.conflicts:
            for c in conflict_result.conflicts:
                reasons.append(f"conflict:{c.conflict_type.value}:{c.severity.value}:{c.description}")

        # Rule 1: CRITICAL_REVIEW (Highest Precedence)
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
        reasons.insert(0, "decision:AUTO_APPROVE:unambiguous_match_high_confidence_zero_conflicts")
        return RecommendedAction.AUTO_APPROVE, reasons
