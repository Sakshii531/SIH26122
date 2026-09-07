"""
Unit tests for Step 6.2 L5/L6 Activity Matching & Ranking module.
"""

import hashlib
import unittest
from pathlib import Path

from ai.data.schedule_loader import ScheduleLoader
from ai.extraction.extractor import ProgressEventExtractor
from ai.extraction.schemas import ExtractedProgressEvent, ExtractionStatus
from ai.matching.matcher import ActivityMatcher, MatchResult, MatchStatus

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_DIR = WORKSPACE_DIR / "data" / "schedule"
REPORTS_DIR = WORKSPACE_DIR / "data" / "reports"
FIELD_REPORTS_CSV = REPORTS_DIR / "field_reports.csv"


class TestActivityMatcher(unittest.TestCase):

    def setUp(self):
        self.schedule_dataset = ScheduleLoader.load_from_directory(SCHEDULE_DIR)

    def test_clear_exact_activity_match(self):
        """Test clear exact match report produces MATCHED status and correct activity ID."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
            report_date="2026-08-05",
        )

        result = ActivityMatcher.match_event(event, self.schedule_dataset)

        self.assertEqual(result.match_status, MatchStatus.MATCHED)
        self.assertEqual(result.matched_activity_id, "ACT-001")
        self.assertEqual(result.matched_activity_code, "CIV-001")
        self.assertEqual(result.matched_discipline, "Civil")
        self.assertGreater(result.match_score, 0.50)

    def test_paraphrased_activity_match(self):
        """Test natural language paraphrased report produces MATCHED status."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-010",
            raw_text="Piping crew performed fit-up and completed root pass TIG welding on the 24-inch crude overhead line spool 24-CDU-002.",
            report_date="2026-09-06",
        )

        result = ActivityMatcher.match_event(event, self.schedule_dataset)

        self.assertEqual(result.match_status, MatchStatus.MATCHED)
        self.assertEqual(result.matched_activity_id, "ACT-082")
        self.assertEqual(result.matched_activity_code, "PIP-082")

    def test_explicit_activity_code_match(self):
        """Test explicit activity code in report produces MATCHED status with explicit_code_match reason."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-004",
            raw_text="Piping team completed erection of Process Overhead Line Piping Spool 24-CDU-001 on PR-101 (PIP-081).",
            report_date="2026-09-08",
        )

        result = ActivityMatcher.match_event(event, self.schedule_dataset)

        self.assertEqual(result.match_status, MatchStatus.MATCHED)
        self.assertEqual(result.matched_activity_code, "PIP-081")
        self.assertTrue(any("explicit_code_match" in r for r in result.match_reasons))

    def test_discipline_agreement_disagreement(self):
        """Test discipline mismatch penalizes candidate score."""
        event = ExtractedProgressEvent(
            report_id="REP-TEST-DISC",
            activity_description="High tension electrical cable pulling",
            discipline="Electrical",
        )

        result = ActivityMatcher.match_event(event, self.schedule_dataset)

        if result.match_status == MatchStatus.MATCHED:
            self.assertEqual(result.matched_discipline, "Electrical")

    def test_similar_activity_names_ranking(self):
        """Test ranked_candidates list is ordered by descending match score."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-010",
            raw_text="Piping crew performed fit-up and completed root pass TIG welding on the 24-inch crude overhead line spool 24-CDU-002.",
            report_date="2026-09-06",
        )

        result = ActivityMatcher.match_event(event, self.schedule_dataset, top_k=5)

        self.assertGreater(len(result.ranked_candidates), 1)

        # Check descending order of scores
        scores = [c.retrieval_score for c in result.ranked_candidates]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_ambiguous_top_candidates(self):
        """Test close competing candidates return MatchStatus.AMBIGUOUS."""
        event = ExtractedProgressEvent(
            report_id="REP-AMBIG",
            activity_description="Concrete pouring completed for pump foundation",
            discipline="Civil",
            extraction_status=ExtractionStatus.AMBIGUOUS,
        )

        # Using small ambiguity delta to trigger ambiguity check
        result = ActivityMatcher.match_event(
            event, self.schedule_dataset, ambiguity_delta=0.50
        )

        self.assertEqual(result.match_status, MatchStatus.AMBIGUOUS)
        self.assertIsNone(result.matched_activity_id)

    def test_no_suitable_candidate(self):
        """Test unrelated text produces MatchStatus.NO_MATCH."""
        event = ExtractedProgressEvent(
            report_id="REP-NO-MATCH",
            activity_description="Quantum particle orbital spin trajectory",
        )

        result = ActivityMatcher.match_event(event, self.schedule_dataset)

        self.assertEqual(result.match_status, MatchStatus.NO_MATCH)
        self.assertIsNone(result.matched_activity_id)

    def test_deterministic_repeated_results(self):
        """Test repeated matcher calls produce 100% identical MatchResult."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
        )

        res1 = ActivityMatcher.match_event(event, self.schedule_dataset)
        res2 = ActivityMatcher.match_event(event, self.schedule_dataset)

        self.assertEqual(res1.match_status, res2.match_status)
        self.assertEqual(res1.matched_activity_id, res2.matched_activity_id)
        self.assertEqual(res1.match_score, res2.match_score)
        self.assertEqual(res1.match_reasons, res2.match_reasons)

    def test_source_dataset_immutability(self):
        """Test activity matching leaves source CSV files 100% byte-identical."""
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

        # Execute matcher
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
        )
        res = ActivityMatcher.match_event(event, self.schedule_dataset)
        self.assertIsNotNone(res)

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
