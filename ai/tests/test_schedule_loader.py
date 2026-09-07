"""
Unit tests for Step 4.3 Schedule Data Loader & Normalization module.
"""

import csv
import datetime
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from ai.data.schedule_loader import (
    Activity,
    Schedule,
    ScheduleDataset,
    ScheduleLoader,
    ScheduleValidationError,
    WBSNode,
)

# Workspace schedule data directory
WORKSPACE_SCHEDULE_DIR = Path(__file__).resolve().parent.parent / "data" / "schedule"


class TestScheduleLoader(unittest.TestCase):

    def test_successful_loading(self):
        """Test loading full synthetic dataset from ai/data/schedule/."""
        dataset = ScheduleLoader.load_from_directory(WORKSPACE_SCHEDULE_DIR)

        self.assertIsInstance(dataset, ScheduleDataset)
        self.assertEqual(len(dataset.schedules), 1)
        self.assertIn("SCH-001", dataset.schedules)

        schedule = dataset.get_schedule("SCH-001")
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule.project_id, "PROJ-001")
        self.assertEqual(schedule.baseline_date, datetime.date(2026, 8, 1))

        # Check WBS counts and roots
        self.assertEqual(len(dataset.wbs_nodes), 65)
        self.assertEqual(len(dataset.root_wbs_nodes), 1)
        root_wbs = dataset.root_wbs_nodes[0]
        self.assertEqual(root_wbs.wbs_id, "WBS-001")
        self.assertEqual(root_wbs.level, "L1")

        # Check activities count
        self.assertEqual(len(dataset.activities), 160)

        # Check sample activity
        act = dataset.get_activity("ACT-001")
        self.assertIsNotNone(act)
        self.assertEqual(act.activity_code, "CIV-001")
        self.assertEqual(act.discipline, "Civil")
        self.assertEqual(act.level, "L6")
        self.assertEqual(act.status, "Completed")
        self.assertEqual(act.planned_start, datetime.date(2026, 8, 1))
        self.assertEqual(act.planned_finish, datetime.date(2026, 8, 5))
        self.assertEqual(act.duration, 5)
        self.assertIsNotNone(act.wbs_node)
        self.assertEqual(act.wbs_node.wbs_id, "WBS-311-1-1")

    def test_required_column_validation(self):
        """Test validation fails if required columns are missing in CSV headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            s_file = tmp_path / "schedules.csv"
            w_file = tmp_path / "wbs.csv"
            a_file = tmp_path / "activities.csv"

            # Create bad schedules.csv with missing baseline_date
            with open(s_file, "w", newline="", encoding="utf-8") as f:
                f.write("schedule_id,project_id,name,source_type,created_at\n")
                f.write("SCH-001,PROJ-001,Test,synthetic_sample,2026-08-01T08:00:00Z\n")

            with open(w_file, "w", newline="", encoding="utf-8") as f:
                f.write("wbs_id,schedule_id,parent_wbs_id,code,name,level,created_at\n")

            with open(a_file, "w", newline="", encoding="utf-8") as f:
                f.write("activity_id,wbs_id,activity_code,name,level,discipline,planned_start,planned_finish,duration,status,created_at\n")

            with self.assertRaises(ScheduleValidationError) as ctx:
                ScheduleLoader.load_from_directory(tmp_path)
            self.assertIn("Schema header mismatch", str(ctx.exception))

    def test_date_parsing_and_validation(self):
        """Test ISO date parsing and planned_start <= planned_finish / duration checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            s_file = tmp_path / "schedules.csv"
            w_file = tmp_path / "wbs.csv"
            a_file = tmp_path / "activities.csv"

            # Valid schedule and WBS
            with open(s_file, "w", newline="", encoding="utf-8") as f:
                f.write("schedule_id,project_id,name,source_type,baseline_date,created_at\n")
                f.write("SCH-001,PROJ-001,Test,synthetic_sample,2026-08-01,2026-08-01T08:00:00Z\n")

            with open(w_file, "w", newline="", encoding="utf-8") as f:
                f.write("wbs_id,schedule_id,parent_wbs_id,code,name,level,created_at\n")
                f.write("WBS-001,SCH-001,,1,Root,L1,2026-08-01T08:00:00Z\n")

            # Invalid activity where planned_start > planned_finish
            with open(a_file, "w", newline="", encoding="utf-8") as f:
                f.write("activity_id,wbs_id,activity_code,name,level,discipline,planned_start,planned_finish,duration,status,created_at\n")
                f.write("ACT-999,WBS-001,CIV-999,Bad Dates,L5,Civil,2026-08-10,2026-08-05,5,Not Started,2026-08-01T08:00:00Z\n")

            with self.assertRaises(ScheduleValidationError) as ctx:
                ScheduleLoader.load_from_directory(tmp_path)
            self.assertIn("planned_start", str(ctx.exception))

    def test_wbs_activity_relationships(self):
        """Test parent-child WBS tree traversal and activity linking."""
        dataset = ScheduleLoader.load_from_directory(WORKSPACE_SCHEDULE_DIR)

        # Test L4 node WBS-311
        wbs_l4 = dataset.get_wbs("WBS-311")
        self.assertIsNotNone(wbs_l4)

        # Non-recursive activities for WBS-311 (L4 has no direct activities, only L5/L6 have)
        direct_acts = dataset.get_activities_for_wbs("WBS-311", recursive=False)
        self.assertEqual(len(direct_acts), 0)

        # Recursive activities for WBS-311 sub-tree
        sub_tree_acts = dataset.get_activities_for_wbs("WBS-311", recursive=True)
        self.assertGreater(len(sub_tree_acts), 0)

        # Test filtering by discipline
        civil_acts = dataset.get_activities_by_discipline("Civil")
        self.assertGreater(len(civil_acts), 20)

        # Test filtering by status
        completed_acts = dataset.get_activities_by_status("Completed")
        self.assertGreater(len(completed_acts), 0)

    def test_invalid_data_handling(self):
        """Test invalid foreign keys, non-existent files, and invalid discipline values."""
        # Non-existent directory
        with self.assertRaises(ScheduleValidationError):
            ScheduleLoader.load_from_directory("/non/existent/path/to/data")

        # Invalid foreign key in activities
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            s_file = tmp_path / "schedules.csv"
            w_file = tmp_path / "wbs.csv"
            a_file = tmp_path / "activities.csv"

            with open(s_file, "w", newline="", encoding="utf-8") as f:
                f.write("schedule_id,project_id,name,source_type,baseline_date,created_at\n")
                f.write("SCH-001,PROJ-001,Test,synthetic_sample,2026-08-01,2026-08-01T08:00:00Z\n")

            with open(w_file, "w", newline="", encoding="utf-8") as f:
                f.write("wbs_id,schedule_id,parent_wbs_id,code,name,level,created_at\n")
                f.write("WBS-001,SCH-001,,1,Root,L1,2026-08-01T08:00:00Z\n")

            with open(a_file, "w", newline="", encoding="utf-8") as f:
                f.write("activity_id,wbs_id,activity_code,name,level,discipline,planned_start,planned_finish,duration,status,created_at\n")
                f.write("ACT-001,INVALID-WBS-ID,CIV-001,Test,L5,Civil,2026-08-01,2026-08-05,5,Not Started,2026-08-01T08:00:00Z\n")

            with self.assertRaises(ScheduleValidationError) as ctx:
                ScheduleLoader.load_from_directory(tmp_path)
            self.assertIn("Foreign key error", str(ctx.exception))

    def test_source_csv_unmodified(self):
        """Test loading dataset does not alter source CSV files."""
        files = ["schedules.csv", "wbs.csv", "activities.csv"]
        hashes_before = {}

        for f_name in files:
            p = WORKSPACE_SCHEDULE_DIR / f_name
            with open(p, "rb") as f:
                hashes_before[f_name] = hashlib.sha256(f.read()).hexdigest()

        # Load dataset
        dataset = ScheduleLoader.load_from_directory(WORKSPACE_SCHEDULE_DIR)
        self.assertIsNotNone(dataset)

        for f_name in files:
            p = WORKSPACE_SCHEDULE_DIR / f_name
            with open(p, "rb") as f:
                hash_after = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                hashes_before[f_name],
                hash_after,
                f"Source CSV file {f_name} was modified!"
            )


if __name__ == "__main__":
    unittest.main()
