"""
Unit tests for Step 5.3 Progress Event Extractor module.
"""

import datetime
import hashlib
import unittest
from pathlib import Path

from ai.extraction.extractor import ProgressEventExtractor
from ai.extraction.schemas import (
    EventDiscipline,
    EventStatus,
    ExtractedProgressEvent,
    ExtractionStatus,
)

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_DIR = WORKSPACE_DIR / "data" / "schedule"
REPORTS_DIR = WORKSPACE_DIR / "data" / "reports"
FIELD_REPORTS_CSV = REPORTS_DIR / "field_reports.csv"


class TestProgressEventExtractor(unittest.TestCase):

    def test_extract_clear_reports(self):
        """Test extraction from clear_exact_match report entries."""
        raw_text = "Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001."
        report_date = "2026-08-05"

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text=raw_text,
            report_date=report_date,
            expected_case="clear_exact_match",
        )

        self.assertEqual(event.report_id, "REP-001")
        self.assertEqual(event.discipline, EventDiscipline.CIVIL.value)
        self.assertEqual(event.status, EventStatus.COMPLETED.value)
        self.assertEqual(event.progress_value, 100.0)
        self.assertEqual(event.actual_finish, datetime.date(2026, 8, 5))
        self.assertEqual(event.extraction_status, ExtractionStatus.COMPLETE)
        self.assertIn("C-101", event.location)

    def test_extract_paraphrased_reports(self):
        """Test extraction from paraphrased_match report entries."""
        raw_text = "Civil gang finished rebar cage tying and steel shuttering for the C-101 main pedestal foundation."
        report_date = "2026-08-18"

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-007",
            raw_text=raw_text,
            report_date=report_date,
            expected_case="paraphrased_match",
        )

        self.assertEqual(event.discipline, EventDiscipline.CIVIL.value)
        self.assertEqual(event.status, EventStatus.COMPLETED.value)
        self.assertEqual(event.progress_value, 100.0)
        self.assertEqual(event.extraction_status, ExtractionStatus.COMPLETE)
        self.assertIn("C-101", event.location)

    def test_extract_short_reports(self):
        """Test extraction from short_log report entries (ExtractionStatus.PARTIAL)."""
        raw_text = "Anchor bolts aligned for C-101."

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-013",
            raw_text=raw_text,
            expected_case="short_log",
        )

        self.assertEqual(event.report_id, "REP-013")
        self.assertEqual(event.extraction_status, ExtractionStatus.PARTIAL)
        self.assertIn("C-101", event.location)

    def test_extract_detailed_reports(self):
        """Test extraction from detailed_report multi-sentence shift entries."""
        raw_text = (
            "Shift Report - Civil & Foundations:\n"
            "Civil contractor deployed 18 workers and 1 backhoe. Excavation pit for Crude Charge Pump P-101 "
            "foundation was completed to target elevation -2.5m. Subgrade was compacted and tested with plate "
            "load bearing test. Blind PCC pouring scheduled for tomorrow morning."
        )
        report_date = "2026-08-28"

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-018",
            raw_text=raw_text,
            report_date=report_date,
            expected_case="detailed_report",
        )

        self.assertEqual(event.discipline, EventDiscipline.CIVIL.value)
        self.assertEqual(event.status, EventStatus.COMPLETED.value)
        self.assertEqual(event.actual_finish, datetime.date(2026, 8, 28))
        self.assertEqual(event.extraction_status, ExtractionStatus.COMPLETE)
        self.assertIn("P-101", event.location)

    def test_extract_missing_information(self):
        """Test extraction from missing_details entries preserves unknown fields as None."""
        raw_text = "Rebar work ongoing for pump foundation."

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-022",
            raw_text=raw_text,
            report_date="",  # Missing report date
            expected_case="missing_details",
        )

        self.assertEqual(event.discipline, EventDiscipline.CIVIL.value)
        self.assertEqual(event.status, EventStatus.IN_PROGRESS.value)
        self.assertIsNone(event.actual_start)
        self.assertIsNone(event.actual_finish)
        self.assertEqual(event.extraction_status, ExtractionStatus.PARTIAL)

    def test_extract_ambiguous_reports(self):
        """Test extraction sets ExtractionStatus.AMBIGUOUS for vague entries."""
        raw_text = "Concrete pouring completed for pump foundation."

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-026",
            raw_text=raw_text,
            expected_case="ambiguous_match",
        )

        self.assertEqual(event.extraction_status, ExtractionStatus.AMBIGUOUS)

    def test_extract_conflicting_info(self):
        """Test extraction sets ExtractionStatus.NEEDS_REVIEW for reports with defects/contradictions."""
        raw_text = (
            "Site supervisor reported 100% completion of concrete pouring for Column C-101 foundation F-101 (CIV-006), "
            "but QC inspector flagged honeycombing on north face requiring repair."
        )

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-031",
            raw_text=raw_text,
            expected_case="conflicting_info",
        )

        self.assertEqual(event.extraction_status, ExtractionStatus.NEEDS_REVIEW)

    def test_invalid_empty_input(self):
        """Test extractor raises ValueError for empty or whitespace-only inputs."""
        with self.assertRaises(ValueError):
            ProgressEventExtractor.extract_from_report(report_id="", raw_text="Valid text")

        with self.assertRaises(ValueError):
            ProgressEventExtractor.extract_from_report(report_id="REP-999", raw_text="   ")

    def test_extract_from_full_dataset(self):
        """Test batch extraction on field_reports.csv dataset."""
        events = ProgressEventExtractor.extract_from_dataset(FIELD_REPORTS_CSV)
        self.assertEqual(len(events), 36)
        self.assertTrue(all(isinstance(e, ExtractedProgressEvent) for e in events))

    def test_source_datasets_and_schema_unmodified(self):
        """Test extraction execution leaves source datasets and schemas 100% byte-identical."""
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

        # Run batch extraction
        events = ProgressEventExtractor.extract_from_dataset(FIELD_REPORTS_CSV)
        self.assertEqual(len(events), 36)

        for p in files:
            with open(p, "rb") as f:
                hash_after = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                hashes_before[p.name],
                hash_after,
                f"Source dataset file {p.name} was modified!",
            )


if __name__ == "__main__":
    unittest.main()
