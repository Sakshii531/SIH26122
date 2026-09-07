"""
End-to-End Multi-Modal AI Pipeline Integration Tests for SIH26122 (Phase 9).

Tests text, OCR image, and ASR audio inputs, heterogeneous batch processing, failure handling,
strict non-mutation policy (human_validation_required=True), source_type provenance, determinism,
and source dataset immutability.
"""

import hashlib
from pathlib import Path
import struct
import unittest
import wave
from PIL import Image, PngImagePlugin

from ai.confidence.confidence_scorer import ConfidenceLevel
from ai.conflict.conflict_detector import ConflictSeverity
from ai.data.schedule_loader import ScheduleLoader
from ai.matching.matcher import MatchStatus
from ai.pipeline.report_pipeline import RecommendedAction, ReportPipeline
from ai.pipeline.suggestion_engine import AISuggestion


class TestMultiModalAIPipeline(unittest.TestCase):
    """Test suite for Phase 9 Multi-Modal ReportPipeline and AISuggestion Engine."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment, synthetic files, and initial dataset hashes."""
        cls.ai_dir = Path(__file__).resolve().parent.parent
        cls.schedule_dir = cls.ai_dir / "data" / "schedule"
        cls.reports_dir = cls.ai_dir / "data" / "reports"

        cls.schedule_dataset = ScheduleLoader.load_from_directory(cls.schedule_dir)

        # 1. Ensure synthetic OCR sample report image exists
        cls.ocr_img_path = cls.reports_dir / "synthetic_sample_report.png"
        img = Image.new("RGB", (400, 100), color=(255, 255, 255))
        info = PngImagePlugin.PngInfo()
        info.add_text(
            "ocr_text",
            "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101. Status: In Progress, progress: 50%.",
        )
        img.save(cls.ocr_img_path, pnginfo=info)

        # 2. Ensure synthetic ASR sample report audio exists
        cls.asr_wav_path = cls.reports_dir / "synthetic_sample_report.wav"
        with wave.open(str(cls.asr_wav_path), "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(44100)
            f.writeframes(struct.pack("<h", 0) * 44100)

        cls.sample_transcript = "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101. Status: In Progress, progress: 50%."

        cls.source_files = [
            cls.schedule_dir / "schedules.csv",
            cls.schedule_dir / "wbs.csv",
            cls.schedule_dir / "activities.csv",
            cls.reports_dir / "field_reports.csv",
        ]

        cls.initial_hashes = {
            f: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in cls.source_files
            if f.exists()
        }

    def test_text_input_to_ai_suggestion(self):
        """Test text report input produces valid AISuggestion with source_type='text'."""
        text_input = "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101. Status: In Progress, progress: 50%."
        sugg = ReportPipeline.process_input(text_input, self.schedule_dataset)

        self.assertIsInstance(sugg, AISuggestion)
        self.assertEqual(sugg.source_type, "text")
        self.assertTrue(sugg.human_validation_required)
        self.assertEqual(sugg.recommended_action, RecommendedAction.AUTO_APPROVE)
        self.assertEqual(sugg.target_activity_code, "CIV-007")

    def test_ocr_image_to_ai_suggestion(self):
        """Test image file input produces valid AISuggestion with source_type='image_ocr'."""
        sugg = ReportPipeline.process_input(self.ocr_img_path, self.schedule_dataset)

        self.assertIsInstance(sugg, AISuggestion)
        self.assertEqual(sugg.source_type, "image_ocr")
        self.assertTrue(sugg.human_validation_required)
        self.assertEqual(sugg.recommended_action, RecommendedAction.AUTO_APPROVE)
        self.assertEqual(sugg.target_activity_code, "CIV-007")

    def test_asr_audio_to_ai_suggestion(self):
        """Test audio file input produces valid AISuggestion with source_type='audio_asr'."""
        sugg = ReportPipeline.process_input(
            self.asr_wav_path,
            self.schedule_dataset,
            mock_asr_transcript=self.sample_transcript,
        )

        self.assertIsInstance(sugg, AISuggestion)
        self.assertEqual(sugg.source_type, "audio_asr")
        self.assertTrue(sugg.human_validation_required)
        self.assertEqual(sugg.recommended_action, RecommendedAction.AUTO_APPROVE)
        self.assertEqual(sugg.target_activity_code, "CIV-007")

    def test_ocr_failure_yields_critical_review(self):
        """Test missing/invalid image file returns AISuggestion with CRITICAL_REVIEW."""
        missing_img = self.reports_dir / "non_existent_ocr_image.png"
        sugg = ReportPipeline.process_input(missing_img, self.schedule_dataset)

        self.assertIsInstance(sugg, AISuggestion)
        self.assertEqual(sugg.source_type, "image_ocr")
        self.assertEqual(sugg.recommended_action, RecommendedAction.CRITICAL_REVIEW)
        self.assertTrue(sugg.human_validation_required)
        self.assertTrue(sugg.has_conflicts)
        self.assertEqual(sugg.highest_conflict_severity, ConflictSeverity.HIGH)

    def test_asr_failure_yields_critical_review(self):
        """Test missing/unreadable audio file returns AISuggestion with CRITICAL_REVIEW."""
        missing_audio = self.reports_dir / "non_existent_voice_audio.wav"
        sugg = ReportPipeline.process_input(missing_audio, self.schedule_dataset)

        self.assertIsInstance(sugg, AISuggestion)
        self.assertEqual(sugg.source_type, "audio_asr")
        self.assertEqual(sugg.recommended_action, RecommendedAction.CRITICAL_REVIEW)
        self.assertTrue(sugg.human_validation_required)
        self.assertTrue(sugg.has_conflicts)

    def test_heterogeneous_batch_processing(self):
        """Test processing a mixed batch of Text, OCR image, and ASR audio inputs."""
        inputs = [
            "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101. Status: In Progress, progress: 50%.",
            self.ocr_img_path,
            self.asr_wav_path,  # Audio without mock -> returns failure suggestion
        ]

        batch_suggestions = ReportPipeline.process_heterogeneous_batch(
            inputs=inputs,
            schedule_target=self.schedule_dataset,
        )

        self.assertEqual(len(batch_suggestions), 3)
        self.assertEqual(batch_suggestions[0].source_type, "text")
        self.assertEqual(batch_suggestions[1].source_type, "image_ocr")
        self.assertEqual(batch_suggestions[2].source_type, "audio_asr")

        # Confirm all items have mandatory human_validation_required = True
        for sugg in batch_suggestions:
            self.assertTrue(sugg.human_validation_required)

    def test_human_validation_required_always_true(self):
        """Verify human_validation_required is True across all action types and source types."""
        sugg_text = ReportPipeline.process_input("CIV-007 Concrete curing 50%.", self.schedule_dataset)
        sugg_ocr = ReportPipeline.process_input(self.ocr_img_path, self.schedule_dataset)
        sugg_fail = ReportPipeline.process_input(self.reports_dir / "missing.png", self.schedule_dataset)

        self.assertTrue(sugg_text.human_validation_required)
        self.assertTrue(sugg_ocr.human_validation_required)
        self.assertTrue(sugg_fail.human_validation_required)

    def test_deterministic_repeated_execution(self):
        """Test repeated execution on identical input yields identical AISuggestion attributes."""
        sugg1 = ReportPipeline.process_input(self.ocr_img_path, self.schedule_dataset)
        sugg2 = ReportPipeline.process_input(self.ocr_img_path, self.schedule_dataset)

        self.assertEqual(sugg1.suggestion_id, sugg2.suggestion_id)
        self.assertEqual(sugg1.source_type, sugg2.source_type)
        self.assertEqual(sugg1.recommended_action, sugg2.recommended_action)
        self.assertEqual(sugg1.target_activity_id, sugg2.target_activity_id)
        self.assertEqual(sugg1.confidence_score, sugg2.confidence_score)

    def test_source_dataset_immutability(self):
        """Verify source CSV files remain 100% byte-identical."""
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
