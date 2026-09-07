"""
Unit tests for Step 6.1 L5/L6 Candidate Retrieval module.
"""

import hashlib
import unittest
from pathlib import Path

from ai.data.schedule_loader import ScheduleLoader
from ai.extraction.extractor import ProgressEventExtractor
from ai.matching.candidate_retriever import CandidateRetriever, RetrievedCandidate

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_DIR = WORKSPACE_DIR / "data" / "schedule"
REPORTS_DIR = WORKSPACE_DIR / "data" / "reports"
FIELD_REPORTS_CSV = REPORTS_DIR / "field_reports.csv"


class TestCandidateRetriever(unittest.TestCase):

    def setUp(self):
        self.schedule_dataset = ScheduleLoader.load_from_directory(SCHEDULE_DIR)

    def test_clear_candidate_retrieval(self):
        """Test retrieving candidates for a clear exact match report."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
            report_date="2026-08-05",
        )

        candidates = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset, top_k=5)

        self.assertGreater(len(candidates), 0)
        top_cand = candidates[0]
        self.assertEqual(top_cand.activity_code, "CIV-001")
        self.assertEqual(top_cand.activity_id, "ACT-001")
        self.assertIn(top_cand.level, ("L5", "L6"))
        self.assertGreater(top_cand.retrieval_score, 0.50)

    def test_discipline_filtering(self):
        """Test discipline filtering prioritizes matching discipline and penalizes mismatched discipline."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-011",
            raw_text="Electrical crew torqued busbar joints and checked insulation resistance for 33kV switchgear panels inside Substation 1.",
            report_date="2026-09-04",
        )

        candidates = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset, top_k=5)

        self.assertGreater(len(candidates), 0)
        for cand in candidates:
            self.assertEqual(cand.discipline, "Electrical")
            self.assertIn("discipline_match:Electrical", cand.retrieval_reasons)

    def test_l5_l6_only_filtering(self):
        """Test candidate retrieval strictly filters activities to L5 and L6 level only."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-004",
            raw_text="Piping team completed erection of Process Overhead Line Piping Spool 24-CDU-001 on PR-101 (PIP-081).",
            report_date="2026-09-08",
        )

        candidates = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset, top_k=20)

        self.assertGreater(len(candidates), 0)
        for cand in candidates:
            self.assertIn(cand.level, ("L5", "L6"), f"Candidate {cand.activity_id} has invalid level '{cand.level}'")

    def test_activity_code_retrieval(self):
        """Test explicit activity code in report text retrieves exact candidate at rank #1."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-004",
            raw_text="Piping team completed erection of Process Overhead Line Piping Spool 24-CDU-001 on PR-101 (PIP-081).",
            report_date="2026-09-08",
        )

        candidates = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset, top_k=5)

        self.assertGreater(len(candidates), 0)
        top_cand = candidates[0]
        self.assertEqual(top_cand.activity_code, "PIP-081")
        self.assertTrue(any("explicit_code_match" in r for r in top_cand.retrieval_reasons))

    def test_no_suitable_candidates(self):
        """Test nonsense or completely unrelated text returns zero candidates above threshold."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-999",
            raw_text="Quantum physics particles entanglement subatomic spin orbital trajectory.",
        )

        candidates = CandidateRetriever.retrieve_candidates(
            event, self.schedule_dataset, top_k=5, min_score_threshold=0.10
        )

        self.assertEqual(len(candidates), 0)

    def test_deterministic_results(self):
        """Test candidate retrieval is 100% deterministic across multiple executions."""
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-007",
            raw_text="Civil gang finished rebar cage tying and steel shuttering for the C-101 main pedestal foundation.",
            report_date="2026-08-18",
        )

        run_1 = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset, top_k=5)
        run_2 = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset, top_k=5)
        run_3 = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset, top_k=5)

        self.assertEqual(len(run_1), len(run_2))
        self.assertEqual(len(run_2), len(run_3))

        for c1, c2, c3 in zip(run_1, run_2, run_3):
            self.assertEqual(c1.activity_id, c2.activity_id)
            self.assertEqual(c2.activity_id, c3.activity_id)
            self.assertEqual(c1.retrieval_score, c2.retrieval_score)
            self.assertEqual(c2.retrieval_score, c3.retrieval_score)

    def test_source_datasets_unmodified(self):
        """Test candidate retrieval leaves source schedule and field report CSV files 100% byte-identical."""
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

        # Run retrieval on a sample event
        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-001",
            raw_text="Completed excavation and subgrade preparation for Crude Column C-101 foundation today as per activity CIV-001.",
        )
        candidates = CandidateRetriever.retrieve_candidates(event, self.schedule_dataset)
        self.assertGreater(len(candidates), 0)

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
