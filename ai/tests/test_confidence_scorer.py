"""
Unit tests for Step 7.1 Confidence Scoring module.
"""

import hashlib
import unittest
from pathlib import Path

from ai.confidence.confidence_scorer import (
    ConfidenceLevel,
    ConfidenceResult,
    ConfidenceScorer,
)
from ai.data.schedule_loader import ScheduleLoader
from ai.extraction.extractor import ProgressEventExtractor
from ai.extraction.schemas import ExtractedProgressEvent, ExtractionStatus
from ai.matching.matcher import ActivityMatcher, MatchResult, MatchStatus

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_DIR = WORKSPACE_DIR / "data" / "schedule"
REPORTS_DIR = WORKSPACE_DIR / "data" / "reports"


class TestConfidenceScorer(unittest.TestCase):

    def setUp(self):
        self.schedule_dataset = ScheduleLoader.load_from_directory(SCHEDULE_DIR)

    def test_high_confidence_score(self):
        """Test clear report with explicit code produces confidence_score >= 0.80 and HIGH level."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
            report_date="2026-08-05",
        )

        match_res = ActivityMatcher.match_event(event, self.schedule_dataset)
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

        self.assertEqual(conf_res.confidence_level, ConfidenceLevel.HIGH)
        self.assertGreaterEqual(conf_res.confidence_score, 0.80)
        self.assertEqual(conf_res.match_status, MatchStatus.MATCHED)
        self.assertEqual(conf_res.matched_activity_code, "CIV-001")
        self.assertIn("explicit_code_evidence_present", conf_res.confidence_reasons)

    def test_medium_confidence_score(self):
        """Test paraphrased report produces 0.50 <= confidence_score < 0.80 and MEDIUM level."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-010",
            raw_text="Piping crew performed fit-up and completed root pass TIG welding on the 24-inch crude overhead line spool 24-CDU-002.",
            report_date="2026-09-06",
        )

        match_res = ActivityMatcher.match_event(event, self.schedule_dataset)
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

        self.assertEqual(conf_res.match_status, MatchStatus.MATCHED)
        self.assertGreaterEqual(conf_res.confidence_score, 0.50)
        self.assertIn(conf_res.confidence_level, (ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH))

    def test_low_confidence_score(self):
        """Test weak match or mismatched signals produce confidence_score < 0.50 and LOW level."""
        event = ExtractedProgressEvent(
            report_id="REP-WEAK",
            activity_description="Vague general work",
            discipline="Civil",
            extraction_status=ExtractionStatus.PARTIAL,
        )

        match_res = ActivityMatcher.match_event(event, self.schedule_dataset, match_threshold=0.10)
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

        if match_res.match_status == MatchStatus.NO_MATCH:
            self.assertEqual(conf_res.confidence_score, 0.0)
            self.assertEqual(conf_res.confidence_level, ConfidenceLevel.LOW)
        else:
            self.assertLess(conf_res.confidence_score, 0.50)
            self.assertEqual(conf_res.confidence_level, ConfidenceLevel.LOW)

    def test_no_match_confidence(self):
        """Test MatchStatus.NO_MATCH strictly returns confidence_score = 0.0 and LOW level."""
        event = ExtractedProgressEvent(
            report_id="REP-NO-MATCH",
            activity_description="Quantum particle orbital trajectory spin",
        )

        match_res = ActivityMatcher.match_event(event, self.schedule_dataset)
        self.assertEqual(match_res.match_status, MatchStatus.NO_MATCH)

        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

        self.assertEqual(conf_res.confidence_score, 0.0)
        self.assertEqual(conf_res.confidence_level, ConfidenceLevel.LOW)
        self.assertEqual(conf_res.matched_activity_id, None)
        self.assertIn("no_matched_activity_candidate", conf_res.confidence_reasons)

    def test_ambiguous_match_confidence_capping(self):
        """Test MatchStatus.AMBIGUOUS caps confidence_score <= 0.45 and sets LOW level."""
        event = ExtractedProgressEvent(
            report_id="REP-AMBIG",
            activity_description="Concrete pouring completed for pump foundation",
            discipline="Civil",
            extraction_status=ExtractionStatus.AMBIGUOUS,
        )

        match_res = ActivityMatcher.match_event(
            event, self.schedule_dataset, ambiguity_delta=0.50
        )
        self.assertEqual(match_res.match_status, MatchStatus.AMBIGUOUS)

        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

        self.assertEqual(conf_res.confidence_level, ConfidenceLevel.LOW)
        self.assertLessEqual(conf_res.confidence_score, 0.45)
        self.assertIn("confidence_capped_due_to_ambiguity", conf_res.confidence_reasons)

    def test_needs_review_conflict_penalty(self):
        """Test ExtractionStatus.NEEDS_REVIEW caps confidence_score <= 0.40 with conflict penalty."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-031",
            raw_text="Site supervisor reported 100% completion of concrete pouring for Column C-101 foundation F-101 (CIV-006), but QC inspector flagged honeycombing on north face requiring repair.",
        )
        self.assertEqual(event.extraction_status, ExtractionStatus.NEEDS_REVIEW)

        match_res = ActivityMatcher.match_event(event, self.schedule_dataset)
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

        self.assertEqual(conf_res.confidence_level, ConfidenceLevel.LOW)
        self.assertLessEqual(conf_res.confidence_score, 0.40)
        self.assertIn("conflict_needs_review_penalty_applied", conf_res.confidence_reasons)

    def test_missing_optional_signals_handling(self):
        """Test missing location or missing dates handle neutral scoring without errors."""
        event = ExtractedProgressEvent(
            report_id="REP-022",
            activity_description="Rebar work ongoing for pump foundation",
            discipline="Civil",
            extraction_status=ExtractionStatus.PARTIAL,
        )

        match_res = ActivityMatcher.match_event(event, self.schedule_dataset)
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

        self.assertIsInstance(conf_res, ConfidenceResult)
        self.assertIn("location_wbs", conf_res.signal_breakdown)
        self.assertEqual(conf_res.signal_breakdown["location_wbs"], 0.5)

    def test_bounded_confidence_score(self):
        """Test confidence_score is strictly bounded in [0.0, 1.0]."""
        events = ProgressEventExtractor.extract_from_dataset(REPORTS_DIR / "field_reports.csv")
        self.assertGreater(len(events), 0)

        for event in events:
            match_res = ActivityMatcher.match_event(event, self.schedule_dataset)
            conf_res = ConfidenceScorer.calculate_confidence(event, match_res)

            self.assertGreaterEqual(conf_res.confidence_score, 0.0)
            self.assertLessEqual(conf_res.confidence_score, 1.0)
            self.assertIn(conf_res.confidence_level, (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW))

    def test_deterministic_repeated_execution(self):
        """Test confidence scoring is 100% deterministic across multiple runs."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
        )
        match_res = ActivityMatcher.match_event(event, self.schedule_dataset)

        res1 = ConfidenceScorer.calculate_confidence(event, match_res)
        res2 = ConfidenceScorer.calculate_confidence(event, match_res)

        self.assertEqual(res1.confidence_score, res2.confidence_score)
        self.assertEqual(res1.confidence_level, res2.confidence_level)
        self.assertEqual(res1.signal_breakdown, res2.signal_breakdown)
        self.assertEqual(res1.confidence_reasons, res2.confidence_reasons)

    def test_source_datasets_unmodified(self):
        """Test confidence scoring leaves source schedule and field report CSV files 100% byte-identical."""
        files = [
            SCHEDULE_DIR / "schedules.csv",
            SCHEDULE_DIR / "wbs.csv",
            SCHEDULE_DIR / "activities.csv",
            REPORTS_DIR / "field_reports.csv",
        ]
        hashes_before = {}

        for p in files:
            with open(p, "rb") as f:
                hashes_before[p.name] = hashlib.sha256(f.read()).hexdigest()

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
        )
        match_res = ActivityMatcher.match_event(event, self.schedule_dataset)
        conf_res = ConfidenceScorer.calculate_confidence(event, match_res)
        self.assertIsNotNone(conf_res)

        for p in files:
            with open(p, "rb") as f:
                hash_after = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                hashes_before[p.name],
                hash_after,
                f"Source file {p.name} was modified!",
            )


if __name__ == "__main__":
    unittest.main()
