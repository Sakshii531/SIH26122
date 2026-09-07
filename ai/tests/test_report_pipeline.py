"""
Unit tests for End-to-End Report Pipeline Orchestrator (AI/ML Step 7.3).

Tests single-report processing, batch processing, decision recommendation classification 
(AUTO_APPROVE, HUMAN_REVIEW, CRITICAL_REVIEW), decision priority hierarchy, mandatory human validation,
deterministic execution, and source dataset immutability.
"""

import datetime
import hashlib
from pathlib import Path
import unittest

from ai.data.schedule_loader import ScheduleLoader
from ai.extraction.schemas import ExtractedProgressEvent, ExtractionStatus
from ai.matching.matcher import MatchResult, MatchStatus
from ai.confidence.confidence_scorer import ConfidenceLevel, ConfidenceScorer
from ai.conflict.conflict_detector import ConflictDetector, ConflictSeverity, ConflictType
from ai.pipeline.report_pipeline import PipelineResult, RecommendedAction, ReportPipeline


class TestReportPipeline(unittest.TestCase):
    """Test suite for ReportPipeline class."""

    @classmethod
    def setUpClass(cls):
        """Load schedule dataset context once for pipeline tests."""
        cls.ai_dir = Path(__file__).resolve().parent.parent
        cls.schedule_dir = cls.ai_dir / "data" / "schedule"
        cls.reports_dir = cls.ai_dir / "data" / "reports"

        cls.schedule_dataset = ScheduleLoader.load_from_directory(cls.schedule_dir)
        cls.source_files = [
            cls.schedule_dir / "schedules.csv",
            cls.schedule_dir / "wbs.csv",
            cls.schedule_dir / "activities.csv",
            cls.reports_dir / "field_reports.csv",
        ]

        cls.initial_hashes = {
            f: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in cls.source_files
            if f.exists()
        }

    def test_auto_approve_flow(self):
        """Test strong, clear field report recommendation (AUTO_APPROVE)."""
        raw_text = (
            "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101. "
            "Status: In Progress, 50% completed."
        )
        report_input = {
            "report_id": "REP-801",
            "raw_text": raw_text,
            "report_date": "2026-08-25",
        }

        result = ReportPipeline.process_report(
            report_input=report_input,
            schedule_target=self.schedule_dataset,
        )

        self.assertEqual(result.report_id, "REP-801")
        self.assertEqual(result.recommended_action, RecommendedAction.AUTO_APPROVE)
        self.assertTrue(result.human_validation_required)  # MANDATORY
        self.assertFalse(result.conflict_result.has_conflict)
        self.assertEqual(result.match_result.match_status, MatchStatus.MATCHED)
        self.assertEqual(result.confidence_result.confidence_level, ConfidenceLevel.HIGH)

    def test_ambiguous_match_flow(self):
        """Test ambiguous candidate match routes to HUMAN_REVIEW."""
        event = ExtractedProgressEvent(
            report_id="REP-802",
            activity_description="Structural steel work",
            status="In Progress",
            progress_value=50.0,
            extraction_status=ExtractionStatus.COMPLETE,
        )

        # Mock an ambiguous MatchResult
        match_res = MatchResult(
            matched_activity_id=None,
            matched_activity_code=None,
            matched_activity_name=None,
            matched_level=None,
            matched_discipline=None,
            match_score=0.65,
            match_status=MatchStatus.AMBIGUOUS,
            ranked_candidates=[],
            match_reasons=["top_two_candidates_too_close"],
        )
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)
        conflict_res = ConflictDetector.evaluate_conflicts(event, match_result=match_res)

        action, reasons = ReportPipeline._evaluate_decision_recommendation(
            event=event,
            match_result=match_res,
            confidence_result=conf_res,
            conflict_result=conflict_res,
        )

        self.assertEqual(action, RecommendedAction.HUMAN_REVIEW)
        self.assertTrue(any("ambiguous" in r for r in reasons))

    def test_partial_extraction_flow(self):
        """Test report with partial extraction status routes to HUMAN_REVIEW."""
        event = ExtractedProgressEvent(
            report_id="REP-803",
            activity_description="CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101",
            extraction_status=ExtractionStatus.PARTIAL,
            status=None,
            progress_value=None,
        )

        result = ReportPipeline.process_report(
            report_input=event,
            schedule_target=self.schedule_dataset,
        )

        self.assertEqual(result.recommended_action, RecommendedAction.HUMAN_REVIEW)
        self.assertTrue(result.human_validation_required)

    def test_high_severity_conflict_flow(self):
        """Test high-severity defect conflict routes to CRITICAL_REVIEW overriding high confidence."""
        event = ExtractedProgressEvent(
            report_id="REP-804",
            activity_description="CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101",
            status="In Progress",
            progress_value=50.0,
            extracted_text="Foundation concrete curing in progress, but severe honeycombing observed on east footing. Work halted for repair.",
        )

        result = ReportPipeline.process_report(
            report_input=event,
            schedule_target=self.schedule_dataset,
        )

        self.assertEqual(result.recommended_action, RecommendedAction.CRITICAL_REVIEW)
        self.assertTrue(result.human_validation_required)
        self.assertEqual(result.conflict_result.highest_severity, ConflictSeverity.HIGH)
        self.assertTrue(any("CRITICAL_REVIEW" in r for r in result.decision_reasons))

    def test_no_match_flow(self):
        """Test unrelated report text producing NO_MATCH routes to CRITICAL_REVIEW."""
        event = ExtractedProgressEvent(
            report_id="REP-805",
            activity_description="Catering services and cafeteria inventory setup",
            status="Completed",
            progress_value=100.0,
        )

        result = ReportPipeline.process_report(
            report_input=event,
            schedule_target=self.schedule_dataset,
        )

        self.assertEqual(result.recommended_action, RecommendedAction.CRITICAL_REVIEW)
        self.assertEqual(result.match_result.match_status, MatchStatus.NO_MATCH)
        self.assertEqual(result.confidence_result.confidence_level, ConfidenceLevel.LOW)
        self.assertTrue(result.human_validation_required)

    def test_non_critical_conflict_flow(self):
        """Test status contradiction with baseline (MEDIUM severity) routes to HUMAN_REVIEW."""
        event = ExtractedProgressEvent(
            report_id="REP-806",
            activity_description="STR-027 Primary Pipe Rack PR-101 baseplate levelling",
            status="Not Started",
            progress_value=0.0,
            extracted_text="Pipe rack levelling not started yet.",
        )
        schedule_act = {
            "activity_id": "ACT-027",
            "activity_code": "STR-027",
            "status": "Completed",  # Mismatch: baseline Completed vs event Not Started
        }

        match_res = MatchResult(
            matched_activity_id="ACT-027",
            matched_activity_code="STR-027",
            matched_activity_name="Primary Pipe Rack PR-101 baseplate levelling",
            matched_level="L5",
            matched_discipline="Structural",
            match_score=0.85,
            match_status=MatchStatus.MATCHED,
            ranked_candidates=[],
        )
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)
        conflict_res = ConflictDetector.evaluate_conflicts(event, schedule_activity=schedule_act)

        action, reasons = ReportPipeline._evaluate_decision_recommendation(
            event=event,
            match_result=match_res,
            confidence_result=conf_res,
            conflict_result=conflict_res,
        )

        self.assertEqual(action, RecommendedAction.HUMAN_REVIEW)
        self.assertEqual(conflict_res.highest_severity, ConflictSeverity.MEDIUM)

    def test_decision_priority_precedence(self):
        """Verify strict priority order: CRITICAL_REVIEW > HUMAN_REVIEW > AUTO_APPROVE."""
        event = ExtractedProgressEvent(
            report_id="REP-807",
            activity_description="CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101",
            status="Completed",
            progress_value=100.0,
            extracted_text="Completed, but major crack and honeycombing detected.",
        )

        result = ReportPipeline.process_report(
            report_input=event,
            schedule_target=self.schedule_dataset,
        )

        # High match score (CIV-007) and high raw confidence, BUT defect conflict MUST force CRITICAL_REVIEW
        self.assertEqual(result.recommended_action, RecommendedAction.CRITICAL_REVIEW)

    def test_human_validation_required_always_true(self):
        """Verify human_validation_required is True for AUTO_APPROVE, HUMAN_REVIEW, and CRITICAL_REVIEW."""
        event_clear = ExtractedProgressEvent(
            report_id="REP-808A",
            activity_description="CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101",
            status="In Progress",
            progress_value=50.0,
            extracted_text="Work on schedule.",
        )
        res_auto = ReportPipeline.process_report(event_clear, self.schedule_dataset)

        event_partial = ExtractedProgressEvent(
            report_id="REP-808B",
            activity_description="CIV-007 Concrete curing and wet matting",
            extraction_status=ExtractionStatus.PARTIAL,
        )
        res_human = ReportPipeline.process_report(event_partial, self.schedule_dataset)

        event_defect = ExtractedProgressEvent(
            report_id="REP-808C",
            activity_description="CIV-007 Concrete curing and wet matting",
            extracted_text="Severe breakdown of equipment.",
        )
        res_critical = ReportPipeline.process_report(event_defect, self.schedule_dataset)

        self.assertTrue(res_auto.human_validation_required)
        self.assertTrue(res_human.human_validation_required)
        self.assertTrue(res_critical.human_validation_required)

    def test_batch_report_processing(self):
        """Test batch processing of multiple reports and stream conflict resolution."""
        reports = [
            {
                "report_id": "REP-901",
                "raw_text": "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101 - Completed 100%.",
                "report_date": "2026-08-25",
            },
            {
                "report_id": "REP-902",
                "raw_text": "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101 - In Progress 40% only.",
                "report_date": "2026-08-28",
            },
        ]

        batch_results = ReportPipeline.process_batch(
            report_inputs=reports,
            schedule_target=self.schedule_dataset,
        )

        self.assertEqual(len(batch_results), 2)
        # Cross-report status regression (Completed -> In Progress) must trigger CRITICAL_REVIEW
        for res in batch_results:
            self.assertTrue(res.conflict_result.has_conflict)
            self.assertEqual(res.recommended_action, RecommendedAction.CRITICAL_REVIEW)

    def test_deterministic_repeated_execution(self):
        """Test repeated execution on identical input returns structurally identical results."""
        report = {
            "report_id": "REP-999",
            "raw_text": "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101 - In Progress 50%.",
            "report_date": "2026-08-25",
        }

        res1 = ReportPipeline.process_report(report, self.schedule_dataset)
        res2 = ReportPipeline.process_report(report, self.schedule_dataset)

        self.assertEqual(res1.report_id, res2.report_id)
        self.assertEqual(res1.recommended_action, res2.recommended_action)
        self.assertEqual(res1.human_validation_required, res2.human_validation_required)
        self.assertEqual(res1.decision_reasons, res2.decision_reasons)
        self.assertEqual(res1.confidence_result.confidence_score, res2.confidence_result.confidence_score)

    def test_source_dataset_immutability(self):
        """Verify source schedule and field report CSV files remain 100% byte-identical."""
        for f in self.source_files:
            if f.exists():
                current_hash = hashlib.sha256(f.read_bytes()).hexdigest()
                self.assertEqual(
                    current_hash,
                    self.initial_hashes[f],
                    f"Source file {f.name} was unexpectedly modified!",
                )


if __name__ == "__main__":
    unittest.main()
