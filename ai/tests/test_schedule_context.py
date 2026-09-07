"""
Unit tests for Step 4.4 Schedule Context Preparation module.
"""

import datetime
import hashlib
import unittest
from pathlib import Path

from ai.data.schedule_context import ActivityContext, ScheduleContextBuilder
from ai.data.schedule_loader import Activity, ScheduleDataset, ScheduleLoader, WBSNode

WORKSPACE_SCHEDULE_DIR = Path(__file__).resolve().parent.parent / "data" / "schedule"


class TestScheduleContext(unittest.TestCase):

    def setUp(self):
        self.dataset = ScheduleLoader.load_from_directory(WORKSPACE_SCHEDULE_DIR)

    def test_context_generation(self):
        """Test building contexts for all 160 activities in synthetic dataset."""
        contexts = ScheduleContextBuilder.build_schedule_context(self.dataset)

        self.assertEqual(len(contexts), 160)
        self.assertIsInstance(contexts[0], ActivityContext)

        context_index = ScheduleContextBuilder.build_context_index(self.dataset)
        self.assertEqual(len(context_index), 160)
        self.assertIn("ACT-001", context_index)

    def test_preservation_of_activity_fields(self):
        """Test all original activity fields are preserved in ActivityContext."""
        act_001 = self.dataset.get_activity("ACT-001")
        self.assertIsNotNone(act_001)

        ctx_001 = ScheduleContextBuilder.build_activity_context(act_001)

        self.assertEqual(ctx_001.activity_id, act_001.activity_id)
        self.assertEqual(ctx_001.activity_code, act_001.activity_code)
        self.assertEqual(ctx_001.name, act_001.name)
        self.assertEqual(ctx_001.level, act_001.level)
        self.assertEqual(ctx_001.discipline, act_001.discipline)
        self.assertEqual(ctx_001.planned_start, act_001.planned_start)
        self.assertEqual(ctx_001.planned_finish, act_001.planned_finish)
        self.assertEqual(ctx_001.duration, act_001.duration)
        self.assertEqual(ctx_001.status, act_001.status)
        self.assertIs(ctx_001.raw_activity, act_001)

        # Confirm location is NOT present on ActivityContext
        self.assertFalse(hasattr(ctx_001, "location"))

    def test_wbs_hierarchy_breadcrumbs(self):
        """Test complete L1 to L6 WBS hierarchy path construction."""
        # ACT-001 belongs to WBS-311-1-1 (L6 node)
        act_001 = self.dataset.get_activity("ACT-001")
        ctx_001 = ScheduleContextBuilder.build_activity_context(act_001)

        self.assertEqual(ctx_001.wbs_id, "WBS-311-1-1")
        self.assertEqual(ctx_001.wbs_level, "L6")
        self.assertEqual(ctx_001.wbs_code, "1.3.1.1.1.1")

        # Verify ancestor path depth (L1 -> L2 -> L3 -> L4 -> L5 -> L6) = 6 levels
        self.assertEqual(len(ctx_001.wbs_path), 6)
        self.assertEqual(len(ctx_001.wbs_code_path), 6)

        # Check path string contains L1 root and L6 leaf names
        self.assertIn("[L1]", ctx_001.wbs_path_str)
        self.assertIn("Greenfield Refinery Infrastructure Project", ctx_001.wbs_path_str)
        self.assertIn("[L6]", ctx_001.wbs_path_str)
        self.assertIn("Column C-101 Excavation", ctx_001.wbs_path_str)

        # Check code path string
        self.assertEqual(ctx_001.wbs_code_path_str, "1 > 1.3 > 1.3.1 > 1.3.1.1 > 1.3.1.1.1 > 1.3.1.1.1.1")

    def test_deterministic_output(self):
        """Test context_text generation is 100% deterministic."""
        act_055 = self.dataset.get_activity("ACT-055")
        self.assertIsNotNone(act_055)

        ctx_run_1 = ScheduleContextBuilder.build_activity_context(act_055)
        ctx_run_2 = ScheduleContextBuilder.build_activity_context(act_055)
        ctx_run_3 = ScheduleContextBuilder.build_activity_context(act_055)

        self.assertEqual(ctx_run_1.context_text, ctx_run_2.context_text)
        self.assertEqual(ctx_run_2.context_text, ctx_run_3.context_text)

        # Verify text format contains key searchable tokens
        text = ctx_run_1.context_text
        self.assertIn(f"Activity Code: {act_055.activity_code}", text)
        self.assertIn(f"Activity Name: {act_055.name}", text)
        self.assertIn(f"Discipline: {act_055.discipline}", text)
        self.assertIn("WBS Hierarchy:", text)

    def test_missing_optional_hierarchy(self):
        """Test handling of an activity attached to a root WBS node (no parent hierarchy)."""
        root_wbs = WBSNode(
            wbs_id="WBS-ROOT-ONLY",
            schedule_id="SCH-001",
            parent_wbs_id=None,
            code="1",
            name="Root Only Node",
            level="L1",
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )

        root_activity = Activity(
            activity_id="ACT-ROOT-01",
            wbs_id="WBS-ROOT-ONLY",
            activity_code="ROOT-001",
            name="Activity On Root WBS",
            level="L5",
            discipline="Civil",
            planned_start=datetime.date(2026, 8, 1),
            planned_finish=datetime.date(2026, 8, 5),
            duration=5,
            status="Not Started",
            created_at=datetime.datetime.now(datetime.timezone.utc),
            wbs_node=root_wbs,
        )

        ctx = ScheduleContextBuilder.build_activity_context(root_activity)

        self.assertEqual(ctx.activity_id, "ACT-ROOT-01")
        self.assertEqual(ctx.wbs_id, "WBS-ROOT-ONLY")
        self.assertEqual(len(ctx.wbs_path), 1)
        self.assertEqual(ctx.wbs_path[0], "[L1] Root Only Node")
        self.assertEqual(ctx.wbs_path_str, "[L1] Root Only Node")
        self.assertEqual(ctx.wbs_code_path_str, "1")
        self.assertIn("Activity Name: Activity On Root WBS", ctx.context_text)

    def test_source_csv_unmodified(self):
        """Test schedule context generation does not alter original CSV files."""
        files = ["schedules.csv", "wbs.csv", "activities.csv"]
        hashes_before = {}

        for f_name in files:
            p = WORKSPACE_SCHEDULE_DIR / f_name
            with open(p, "rb") as f:
                hashes_before[f_name] = hashlib.sha256(f.read()).hexdigest()

        # Build context from dataset
        contexts = ScheduleContextBuilder.build_schedule_context(self.dataset)
        self.assertGreater(len(contexts), 0)

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
