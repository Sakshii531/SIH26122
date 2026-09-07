"""
Unit tests for Conflict Detector Module (AI/ML Step 7.2).

Tests single-report conflicts (defects, date inversions, progress contradictions, status mismatches),
multi-report stream conflicts (status regression, progress variance), missing information handling,
deterministic repeated execution, and source dataset immutability.
"""

import datetime
import hashlib
from pathlib import Path
import unittest

from ai.conflict.conflict_detector import (
    ConflictDetail,
    ConflictDetector,
    ConflictResult,
    ConflictSeverity,
    ConflictType,
)
from ai.extraction.schemas import ExtractedProgressEvent, ExtractionStatus
from ai.matching.matcher import MatchResult, MatchStatus


class TestConflictDetector(unittest.TestCase):
    """Test suite for ConflictDetector class."""

    def setUp(self):
        """Set up test paths and reference objects."""
        self.ai_dir = Path(__file__).resolve().parent.parent
        self.schedule_dir = self.ai_dir / "data" / "schedule"
        self.reports_dir = self.ai_dir / "data" / "reports"

        self.source_files = [
            self.schedule_dir / "schedules.csv",
            self.schedule_dir / "wbs.csv",
            self.schedule_dir / "activities.csv",
            self.reports_dir / "field_reports.csv",
        ]
        
        # Store initial file hashes to verify immutability
        self.initial_hashes = {
            f: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in self.source_files
            if f.exists()
        }

    def test_no_conflict(self):
        """Test that a valid report with matching status and normal text flags no conflicts."""
        event = ExtractedProgressEvent(
            report_id="REP-101",
            activity_description="Pouring foundation slab concrete",
            status="In Progress",
            progress_value=50.0,
            actual_start=datetime.date(2026, 8, 1),
            actual_finish=datetime.date(2026, 8, 5),
            extracted_text="Work proceeding according to schedule without issues.",
        )
        schedule_act = {
            "activity_id": "ACT-001",
            "activity_code": "CIV-001",
            "status": "In Progress",
        }

        result = ConflictDetector.evaluate_conflicts(event, schedule_activity=schedule_act)

        self.assertFalse(result.has_conflict)
        self.assertIsNone(result.highest_severity)
        self.assertEqual(len(result.conflicts), 0)
        self.assertEqual(result.report_count_evaluated, 1)

    def test_defect_breakdown(self):
        """Test detection of defect, repair, or equipment breakdown keywords."""
        event = ExtractedProgressEvent(
            report_id="REP-102",
            activity_description="Column concreting work",
            status="In Progress",
            progress_value=30.0,
            extracted_text="Severe honeycombing noticed on north face. Work halted for repair.",
        )

        result = ConflictDetector.evaluate_conflicts(event)

        self.assertTrue(result.has_conflict)
        self.assertEqual(result.highest_severity, ConflictSeverity.HIGH)
        self.assertEqual(len(result.conflicts), 1)

        conflict = result.conflicts[0]
        self.assertEqual(conflict.conflict_type, ConflictType.DEFECT_BREAKDOWN)
        self.assertEqual(conflict.severity, ConflictSeverity.HIGH)
        self.assertIn("REP-102", conflict.report_ids)
        self.assertTrue(any("honeycombing" in e for e in conflict.evidence))

    def test_status_contradiction(self):
        """Test extracted status 'Completed' vs baseline schedule status 'Not Started'."""
        event = ExtractedProgressEvent(
            report_id="REP-103",
            activity_description="Structural steel erection",
            status="Completed",
            progress_value=100.0,
            extracted_text="Erection fully complete.",
        )
        schedule_act = {
            "activity_id": "ACT-005",
            "activity_code": "STR-005",
            "status": "Not Started",
        }

        result = ConflictDetector.evaluate_conflicts(event, schedule_activity=schedule_act)

        self.assertTrue(result.has_conflict)
        self.assertEqual(result.highest_severity, ConflictSeverity.MEDIUM)
        
        status_conflicts = [c for c in result.conflicts if c.conflict_type == ConflictType.STATUS_CONTRADICTION]
        self.assertEqual(len(status_conflicts), 1)
        self.assertEqual(status_conflicts[0].severity, ConflictSeverity.MEDIUM)

    def test_date_inconsistency(self):
        """Test detection of inverted dates (actual_start > actual_finish)."""
        # Bypass Pydantic validator using model_construct to simulate invalid date extraction
        event = ExtractedProgressEvent.model_construct(
            report_id="REP-104",
            activity_description="Piping alignment test",
            status="In Progress",
            actual_start=datetime.date(2026, 8, 15),
            actual_finish=datetime.date(2026, 8, 10),
            extracted_text="Dates extracted from site log.",
        )

        result = ConflictDetector.evaluate_conflicts(event)

        self.assertTrue(result.has_conflict)
        self.assertEqual(result.highest_severity, ConflictSeverity.HIGH)

        date_conflicts = [c for c in result.conflicts if c.conflict_type == ConflictType.DATE_INCONSISTENCY]
        self.assertEqual(len(date_conflicts), 1)
        self.assertEqual(date_conflicts[0].severity, ConflictSeverity.HIGH)

    def test_progress_contradiction(self):
        """Test progress 100% claimed alongside text caveats indicating incomplete/halted status."""
        event = ExtractedProgressEvent(
            report_id="REP-105",
            activity_description="Transformer installation",
            status="Completed",
            progress_value=100.0,
            extracted_text="100% completed but work halted due to missing cabling.",
        )

        result = ConflictDetector.evaluate_conflicts(event)

        self.assertTrue(result.has_conflict)
        self.assertEqual(result.highest_severity, ConflictSeverity.HIGH)

        prog_conflicts = [c for c in result.conflicts if c.conflict_type == ConflictType.PROGRESS_CONTRADICTION]
        self.assertEqual(len(prog_conflicts), 1)
        self.assertEqual(prog_conflicts[0].severity, ConflictSeverity.HIGH)

    def test_cross_report_status_contradiction(self):
        """Test cross-report status regression (Completed followed by In Progress)."""
        event1 = ExtractedProgressEvent(
            report_id="REP-201",
            activity_description="Cable tray installation",
            status="Completed",
            progress_value=100.0,
            actual_finish=datetime.date(2026, 8, 1),
            extracted_text="Trays complete.",
        )
        event2 = ExtractedProgressEvent(
            report_id="REP-202",
            activity_description="Cable tray installation",
            status="In Progress",
            progress_value=60.0,
            actual_finish=datetime.date(2026, 8, 5),
            extracted_text="Additional tray sections being installed.",
        )

        result = ConflictDetector.evaluate_conflicts([event1, event2])

        self.assertTrue(result.has_conflict)
        self.assertEqual(result.highest_severity, ConflictSeverity.HIGH)

        cross_conflicts = [c for c in result.conflicts if c.conflict_type == ConflictType.CROSS_REPORT_CONTRADICTION]
        self.assertTrue(len(cross_conflicts) >= 1)
        self.assertIn("REP-201", cross_conflicts[0].report_ids)
        self.assertIn("REP-202", cross_conflicts[0].report_ids)

    def test_cross_report_progress_variance(self):
        """Test cross-report progress variance (100% in earlier report vs 40% in later report)."""
        event1 = ExtractedProgressEvent(
            report_id="REP-301",
            activity_description="Piping hydrotest",
            status="Completed",
            progress_value=100.0,
            actual_finish=datetime.date(2026, 8, 2),
            extracted_text="Hydrotest finished.",
        )
        event2 = ExtractedProgressEvent(
            report_id="REP-302",
            activity_description="Piping hydrotest",
            status="In Progress",
            progress_value=40.0,
            actual_finish=datetime.date(2026, 8, 6),
            extracted_text="Hydrotest ongoing.",
        )

        result = ConflictDetector.evaluate_conflicts([event1, event2])

        self.assertTrue(result.has_conflict)
        self.assertEqual(result.highest_severity, ConflictSeverity.HIGH)

    def test_missing_partial_information(self):
        """Test that missing optional fields (None) do NOT trigger false conflict flags."""
        event = ExtractedProgressEvent(
            report_id="REP-401",
            activity_description="Site survey",
            extraction_status=ExtractionStatus.PARTIAL,
            status=None,
            progress_value=None,
            actual_start=None,
            actual_finish=None,
            location=None,
            extracted_text=None,
        )

        result = ConflictDetector.evaluate_conflicts(event)

        self.assertFalse(result.has_conflict)
        self.assertIsNone(result.highest_severity)
        self.assertEqual(len(result.conflicts), 0)

    def test_deterministic_repeated_execution(self):
        """Test that repeated runs on identical inputs yield byte-identical results."""
        event = ExtractedProgressEvent(
            report_id="REP-501",
            activity_description="Excavation work",
            status="Completed",
            progress_value=100.0,
            extracted_text="Excavation completed, but repair needed on retaining wall.",
        )

        res1 = ConflictDetector.evaluate_conflicts(event)
        res2 = ConflictDetector.evaluate_conflicts(event)

        self.assertEqual(res1.has_conflict, res2.has_conflict)
        self.assertEqual(res1.highest_severity, res2.highest_severity)
        self.assertEqual(len(res1.conflicts), len(res2.conflicts))
        self.assertEqual(res1.summary, res2.summary)

        for c1, c2 in zip(res1.conflicts, res2.conflicts):
            self.assertEqual(c1.conflict_id, c2.conflict_id)
            self.assertEqual(c1.conflict_type, c2.conflict_type)
            self.assertEqual(c1.severity, c2.severity)
            self.assertEqual(c1.evidence, c2.evidence)

    def test_source_datasets_unmodified(self):
        """Verify source schedule and report CSV files remain byte-identical."""
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
