"""
Unit tests for Step 6.3 Semantic Similarity Enhancement module.
"""

import csv
import hashlib
import unittest
from pathlib import Path

from ai.data.schedule_loader import ScheduleLoader
from ai.extraction.extractor import ProgressEventExtractor
from ai.matching.matcher import ActivityMatcher, MatchStatus
from ai.matching.semantic_similarity import SemanticSimilarityCalculator

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_DIR = WORKSPACE_DIR / "data" / "schedule"
REPORTS_DIR = WORKSPACE_DIR / "data" / "reports"
ACTIVITIES_CSV = SCHEDULE_DIR / "activities.csv"


class TestSemanticSimilarity(unittest.TestCase):

    def setUp(self):
        self.schedule_dataset = ScheduleLoader.load_from_directory(SCHEDULE_DIR)

    def test_identical_descriptions(self):
        """Test identical text inputs return similarity score of 1.0."""
        text1 = "Excavation and subgrade preparation for Crude Column C-101 foundation"
        text2 = "Excavation and subgrade preparation for Crude Column C-101 foundation"

        sim = SemanticSimilarityCalculator.calculate_similarity(text1, text2)
        self.assertEqual(sim, 1.0)

    def test_paraphrased_descriptions(self):
        """Test paraphrased/naturally worded descriptions receive high similarity score."""
        text1 = "RMC transit mixers poured 140 m3 of grade M35 concrete for the C-101 main column foundation slab F-101."
        text2 = "Heavy concrete pouring for Column C-101 foundation slab F-101"

        sim = SemanticSimilarityCalculator.calculate_similarity(text1, text2)
        self.assertGreaterEqual(sim, 0.50)
        self.assertLessEqual(sim, 1.0)

    def test_unrelated_descriptions(self):
        """Test completely unrelated text inputs receive low similarity score."""
        text1 = "Substation 33kV switchgear panel positioning inside switchgear room"
        text2 = "Excavation pit for pump foundation pit elevation"

        sim = SemanticSimilarityCalculator.calculate_similarity(text1, text2)
        self.assertLessEqual(sim, 0.25)
        self.assertGreaterEqual(sim, 0.0)

    def test_empty_missing_text(self):
        """Test empty string or None inputs return 0.0 without throwing exceptions."""
        self.assertEqual(SemanticSimilarityCalculator.calculate_similarity("", "valid text"), 0.0)
        self.assertEqual(SemanticSimilarityCalculator.calculate_similarity("valid text", None), 0.0)
        self.assertEqual(SemanticSimilarityCalculator.calculate_similarity(None, None), 0.0)

    def test_bounded_similarity_score(self):
        """Test similarity score is strictly bounded in [0.0, 1.0]."""
        test_pairs = [
            ("Pipe rack column erection Grid A1 to A5", "Erectors assembled steel columns PR-101"),
            ("High pressure steam piping spool fit-up", "Unrelated quantum physics particle spin"),
            ("Transformer oil filtration dielectric test", "Transformer oil filtration dielectric test"),
        ]

        for s1, s2 in test_pairs:
            sim = SemanticSimilarityCalculator.calculate_similarity(s1, s2)
            self.assertGreaterEqual(sim, 0.0)
            self.assertLessEqual(sim, 1.0)

    def test_deterministic_repeated_results(self):
        """Test multiple runs on identical input strings return byte-identical float results."""
        text1 = "Civil gang finished rebar cage tying and steel shuttering for C-101 main pedestal foundation."
        text2 = "Reinforcement steel rebar cage assembly for Column C-101 pedestal"

        sim1 = SemanticSimilarityCalculator.calculate_similarity(text1, text2)
        sim2 = SemanticSimilarityCalculator.calculate_similarity(text1, text2)
        sim3 = SemanticSimilarityCalculator.calculate_similarity(text1, text2)

        self.assertEqual(sim1, sim2)
        self.assertEqual(sim2, sim3)

    def test_existing_matcher_behavior_remains_valid(self):
        """Test ActivityMatcher integrates semantic similarity while maintaining correct match decisions."""
        # Clear exact match
        event1 = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
        )
        res1 = ActivityMatcher.match_event(event1, self.schedule_dataset)
        self.assertEqual(res1.match_status, MatchStatus.MATCHED)
        self.assertEqual(res1.matched_activity_id, "ACT-001")

        # Paraphrased match
        event2 = ProgressEventExtractor.extract_from_report(
            report_id="REP-010",
            raw_text="Piping crew performed fit-up and completed root pass TIG welding on the 24-inch crude overhead line spool 24-CDU-002.",
        )
        res2 = ActivityMatcher.match_event(event2, self.schedule_dataset)
        self.assertEqual(res2.match_status, MatchStatus.MATCHED)
        self.assertEqual(res2.matched_activity_id, "ACT-082")

        # Unrelated no match
        event3 = ProgressEventExtractor.extract_from_report(
            report_id="REP-NO-MATCH",
            raw_text="Quantum orbital trajectory Subatomic spin",
        )
        res3 = ActivityMatcher.match_event(event3, self.schedule_dataset)
        self.assertEqual(res3.match_status, MatchStatus.NO_MATCH)

    def test_source_datasets_and_schema_unmodified(self):
        """Test source CSV files remain 100% byte-identical and location is not added to activities.csv."""
        files = [
            SCHEDULE_DIR / "schedules.csv",
            SCHEDULE_DIR / "wbs.csv",
            ACTIVITIES_CSV,
            REPORTS_DIR / "field_reports.csv",
        ]
        hashes_before = {}

        for p in files:
            with open(p, "rb") as f:
                hashes_before[p.name] = hashlib.sha256(f.read()).hexdigest()

        # Run semantic calculation
        sim = SemanticSimilarityCalculator.calculate_similarity(
            "Concrete pouring for foundation", "Concrete pouring for pedestal"
        )
        self.assertGreater(sim, 0.0)

        for p in files:
            with open(p, "rb") as f:
                hash_after = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                hashes_before[p.name],
                hash_after,
                f"Source file {p.name} was modified!",
            )

        # Verify activities.csv headers do NOT contain 'location'
        with open(ACTIVITIES_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.assertNotIn("location", reader.fieldnames, "Forbidden column 'location' found in activities.csv!")


if __name__ == "__main__":
    unittest.main()
