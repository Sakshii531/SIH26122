"""
Unit tests for Step 5.1 Synthetic Field Report Preparation module.
"""

import csv
import hashlib
import unittest
from pathlib import Path

from ai.data.schedule_loader import ScheduleLoader

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_DIR = WORKSPACE_DIR / "data" / "schedule"
REPORTS_DIR = WORKSPACE_DIR / "data" / "reports"
FIELD_REPORTS_CSV = REPORTS_DIR / "field_reports.csv"

EXPECTED_REPORT_HEADERS = [
    "report_id",
    "report_date",
    "source_type",
    "raw_text",
    "referenced_activity_id",
    "referenced_activity_code",
    "expected_case",
]

VALID_CATEGORIES = {
    "clear_exact_match",
    "paraphrased_match",
    "short_log",
    "detailed_report",
    "missing_details",
    "ambiguous_match",
    "conflicting_info",
}


class TestFieldReports(unittest.TestCase):

    def setUp(self):
        # Load valid activities from synthetic schedule
        self.schedule_dataset = ScheduleLoader.load_from_directory(SCHEDULE_DIR)
        self.valid_activity_ids = set(self.schedule_dataset.activities.keys())
        self.valid_activity_codes = {
            act.activity_code for act in self.schedule_dataset.activities.values()
        }

    def test_file_existence_and_schema(self):
        """Test field_reports.csv exists and matches expected column headers."""
        self.assertTrue(FIELD_REPORTS_CSV.exists(), f"Missing file: {FIELD_REPORTS_CSV}")

        with open(FIELD_REPORTS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            self.assertIsNotNone(headers, "field_reports.csv is empty")
            self.assertEqual(headers, EXPECTED_REPORT_HEADERS, "Header schema mismatch")

    def test_unique_report_ids_and_non_empty_text(self):
        """Test report_id values are unique and raw_text is non-empty."""
        report_ids = set()
        with open(FIELD_REPORTS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 0, "No field report rows found")

            for i, row in enumerate(rows, start=2):
                rid = row.get("report_id", "").strip()
                text = row.get("raw_text", "").strip()

                self.assertTrue(rid, f"Line {i}: Empty report_id")
                self.assertNotIn(rid, report_ids, f"Line {i}: Duplicate report_id '{rid}'")
                report_ids.add(rid)

                self.assertTrue(text, f"Line {i} ({rid}): Empty raw_text")

    def test_referenced_activity_validity(self):
        """Test referenced_activity_id and referenced_activity_code exist in activities.csv when present."""
        with open(FIELD_REPORTS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                rid = row.get("report_id", "").strip()
                ref_act_id = row.get("referenced_activity_id", "").strip()
                ref_act_code = row.get("referenced_activity_code", "").strip()

                if ref_act_id:
                    self.assertIn(
                        ref_act_id,
                        self.valid_activity_ids,
                        f"Line {i} ({rid}): Referenced activity_id '{ref_act_id}' not found in activities.csv",
                    )

                if ref_act_code:
                    self.assertIn(
                        ref_act_code,
                        self.valid_activity_codes,
                        f"Line {i} ({rid}): Referenced activity_code '{ref_act_code}' not found in activities.csv",
                    )

    def test_expected_case_category_validity(self):
        """Test expected_case values belong to the defined valid category set."""
        with open(FIELD_REPORTS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                rid = row.get("report_id", "").strip()
                category = row.get("expected_case", "").strip()

                self.assertIn(
                    category,
                    VALID_CATEGORIES,
                    f"Line {i} ({rid}): Invalid category '{category}'. Allowed: {VALID_CATEGORIES}",
                )

    def test_source_schedule_csv_unmodified(self):
        """Test processing field reports does not alter source schedule CSV files."""
        files = ["schedules.csv", "wbs.csv", "activities.csv"]
        hashes_before = {}

        for f_name in files:
            p = SCHEDULE_DIR / f_name
            with open(p, "rb") as f:
                hashes_before[f_name] = hashlib.sha256(f.read()).hexdigest()

        # Re-read field reports
        with open(FIELD_REPORTS_CSV, mode="r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 0)

        for f_name in files:
            p = SCHEDULE_DIR / f_name
            with open(p, "rb") as f:
                hash_after = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                hashes_before[f_name],
                hash_after,
                f"Source schedule CSV file {f_name} was modified!",
            )


if __name__ == "__main__":
    unittest.main()
