"""
Unit tests for Step 5.2 Progress Event Extraction Schema module.
"""

import datetime
import hashlib
import unittest
from pathlib import Path
from pydantic import ValidationError

from ai.extraction.schemas import (
    EventDiscipline,
    EventStatus,
    ExtractedProgressEvent,
    ExtractionStatus,
)

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_DIR = WORKSPACE_DIR / "data" / "schedule"
REPORTS_DIR = WORKSPACE_DIR / "data" / "reports"


class TestExtractionSchemas(unittest.TestCase):

    def test_valid_complete_event(self):
        """Test creating a valid complete ExtractedProgressEvent."""
        event = ExtractedProgressEvent(
            report_id="REP-001",
            activity_description="Excavation and subgrade prep for C-101 foundation",
            extraction_status=ExtractionStatus.COMPLETE,
            discipline=EventDiscipline.CIVIL,
            status=EventStatus.COMPLETED,
            actual_start=datetime.date(2026, 8, 1),
            actual_finish=datetime.date(2026, 8, 5),
            location="Process Unit 100, Grid A-B",
            progress_value=100.0,
            extracted_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today",
            metadata={"source": "daily_log", "inspector": "QA-John"},
        )

        self.assertEqual(event.report_id, "REP-001")
        self.assertEqual(event.activity_description, "Excavation and subgrade prep for C-101 foundation")
        self.assertEqual(event.extraction_status, ExtractionStatus.COMPLETE)
        self.assertEqual(event.discipline, "Civil")
        self.assertEqual(event.status, "Completed")
        self.assertEqual(event.actual_start, datetime.date(2026, 8, 1))
        self.assertEqual(event.actual_finish, datetime.date(2026, 8, 5))
        self.assertEqual(event.location, "Process Unit 100, Grid A-B")
        self.assertEqual(event.progress_value, 100.0)
        self.assertEqual(event.metadata["inspector"], "QA-John")

    def test_missing_optional_fields(self):
        """Test creating an event with only required fields leaves optional fields as None."""
        event = ExtractedProgressEvent(
            report_id="REP-022",
            activity_description="Rebar work ongoing for pump foundation",
        )

        self.assertEqual(event.report_id, "REP-022")
        self.assertEqual(event.activity_description, "Rebar work ongoing for pump foundation")
        self.assertEqual(event.extraction_status, ExtractionStatus.COMPLETE)  # Default
        self.assertIsNone(event.discipline)
        self.assertIsNone(event.status)
        self.assertIsNone(event.actual_start)
        self.assertIsNone(event.actual_finish)
        self.assertIsNone(event.location)
        self.assertIsNone(event.progress_value)
        self.assertIsNone(event.extracted_text)

    def test_invalid_progress_value(self):
        """Test progress_value validation raises ValidationError for values outside 0..100."""
        # Negative progress value
        with self.assertRaises(ValidationError) as ctx:
            ExtractedProgressEvent(
                report_id="REP-001",
                activity_description="Test",
                progress_value=-10.0,
            )
        self.assertIn("progress_value must be between 0.0 and 100.0", str(ctx.exception))

        # Progress value > 100%
        with self.assertRaises(ValidationError) as ctx:
            ExtractedProgressEvent(
                report_id="REP-001",
                activity_description="Test",
                progress_value=120.0,
            )
        self.assertIn("progress_value must be between 0.0 and 100.0", str(ctx.exception))

    def test_date_validation(self):
        """Test date validation raises ValidationError when actual_start > actual_finish."""
        with self.assertRaises(ValidationError) as ctx:
            ExtractedProgressEvent(
                report_id="REP-001",
                activity_description="Test dates",
                actual_start=datetime.date(2026, 8, 10),
                actual_finish=datetime.date(2026, 8, 5),
            )
        self.assertIn("actual_start", str(ctx.exception))
        self.assertIn("cannot be after actual_finish", str(ctx.exception))

    def test_extraction_statuses(self):
        """Test all valid extraction status enum values."""
        statuses = [
            ExtractionStatus.COMPLETE,
            ExtractionStatus.PARTIAL,
            ExtractionStatus.AMBIGUOUS,
            ExtractionStatus.NEEDS_REVIEW,
        ]

        for st in statuses:
            event = ExtractedProgressEvent(
                report_id="REP-026",
                activity_description="Ambiguous log entry",
                extraction_status=st,
            )
            self.assertEqual(event.extraction_status, st)

    def test_location_field_in_event(self):
        """Test location field is explicitly present and preserved in ExtractedProgressEvent."""
        event = ExtractedProgressEvent(
            report_id="REP-003",
            activity_description="Pipe rack column erection",
            location="Pipe Rack PR-101 Tier 1 Grid A1 to A5",
        )
        self.assertTrue(hasattr(event, "location"))
        self.assertEqual(event.location, "Pipe Rack PR-101 Tier 1 Grid A1 to A5")

    def test_source_datasets_unmodified(self):
        """Test schema validation execution leaves source datasets 100% byte-identical."""
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

        # Instantiate a model
        event = ExtractedProgressEvent(
            report_id="REP-001",
            activity_description="Test",
            progress_value=50.0,
        )
        self.assertIsNotNone(event)

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
