"""
Unit tests for ASR Processing Module (Phase 8).

Tests valid audio transcription interface, whitespace text normalization, missing file handling,
unsupported extension handling, corrupt audio handling, structured failure handling, strict non-fallback behavior for companion .txt files, integration with ProgressEventExtractor, deterministic execution, and source dataset immutability.
"""

import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import wave

from ai.asr.asr_processor import ASRProcessor, ASRResult
from ai.extraction.extractor import ProgressEventExtractor


class TestASRProcessor(unittest.TestCase):
    """Test suite for ASRProcessor class."""

    @classmethod
    def setUpClass(cls):
        """Set up test directories, synthetic WAV file, and initial dataset hashes."""
        cls.ai_dir = Path(__file__).resolve().parent.parent
        cls.schedule_dir = cls.ai_dir / "data" / "schedule"
        cls.reports_dir = cls.ai_dir / "data" / "reports"

        cls.synthetic_wav_path = cls.reports_dir / "synthetic_sample_report.wav"
        
        # Ensure synthetic sample report WAV exists
        if not cls.synthetic_wav_path.exists():
            with wave.open(str(cls.synthetic_wav_path), "w") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(44100)
                f.writeframes(struct.pack("<h", 0) * 44100)

        # Create companion text transcript file for test fixture usage
        cls.companion_txt_path = cls.synthetic_wav_path.with_suffix(".txt")
        cls.sample_text = "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101. Status: In Progress, progress: 50%."
        cls.companion_txt_path.write_text(cls.sample_text, encoding="utf-8")

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

    def test_companion_txt_not_used_as_runtime_fallback(self):
        """Verify process_audio() does NOT automatically read companion .txt as a runtime fallback."""
        # Calling process_audio without mock_transcription parameter
        result = ASRProcessor.process_audio(self.synthetic_wav_path)

        # Since synthetic_wav_path is silent audio and no offline Sphinx engine is configured,
        # it must return success=False and NOT read sample_text from companion .txt
        self.assertFalse(result.success)
        self.assertEqual(result.transcribed_text, "")
        self.assertIsNotNone(result.error)

    def test_companion_transcript_usable_explicitly_by_test(self):
        """Verify test fixture can explicitly pass companion transcript as mock_transcription."""
        fixture_text = self.companion_txt_path.read_text(encoding="utf-8")
        result = ASRProcessor.process_audio(
            self.synthetic_wav_path,
            mock_transcription=fixture_text,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.transcribed_text, ASRProcessor.normalize_text(fixture_text))
        self.assertIsNone(result.error)

    def test_successful_asr_from_mock_or_engine(self):
        """Test processing audio with explicit transcript input yields successful ASRResult."""
        result = ASRProcessor.process_audio(
            self.synthetic_wav_path,
            mock_transcription=self.sample_text,
        )

        self.assertIsInstance(result, ASRResult)
        self.assertTrue(result.success)
        self.assertIsNone(result.error)
        self.assertEqual(result.source_path, str(self.synthetic_wav_path))
        self.assertIn("CIV-007", result.transcribed_text)
        self.assertIn("Column C-101", result.transcribed_text)

    def test_transcription_normalization(self):
        """Test whitespace normalization compresses excessive padding, newlines, and tabs."""
        raw_input = "  CIV-001  Foundation   Slab \n\n Concreting  \t 50%   completed.  "
        normalized = ASRProcessor.normalize_text(raw_input)

        self.assertEqual(
            normalized,
            "CIV-001 Foundation Slab Concreting 50% completed.",
        )

    def test_missing_file(self):
        """Test missing file path returns success=False without crashing."""
        missing_path = self.reports_dir / "non_existent_voice_report_9999.wav"
        result = ASRProcessor.process_audio(missing_path)

        self.assertFalse(result.success)
        self.assertEqual(result.transcribed_text, "")
        self.assertIsNotNone(result.error)
        self.assertIn("Audio file not found", result.error)

    def test_unsupported_extension(self):
        """Test unsupported audio file format returns success=False."""
        unsupported_path = self.reports_dir / "field_reports.csv"  # CSV is not audio
        result = ASRProcessor.process_audio(unsupported_path)

        self.assertFalse(result.success)
        self.assertEqual(result.transcribed_text, "")
        self.assertIsNotNone(result.error)
        self.assertIn("Unsupported audio file format", result.error)

    def test_invalid_corrupt_audio(self):
        """Test corrupt file with .wav extension returns success=False without crashing."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"CORRUPT_WAV_HEADER_DATA_12345")
            tmp_path = Path(tmp.name)

        try:
            result = ASRProcessor.process_audio(tmp_path)
            self.assertFalse(result.success)
            self.assertEqual(result.transcribed_text, "")
            self.assertIsNotNone(result.error)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_structured_failure_handling(self):
        """Test empty/unreadable audio without mock parameter returns structured failure without hallucinating."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            with wave.open(tmp.name, "w") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(44100)
                f.writeframes(b"")  # 0 frames
            tmp_path = Path(tmp.name)

        try:
            result = ASRProcessor.process_audio(tmp_path)
            self.assertFalse(result.success)
            self.assertEqual(result.transcribed_text, "")
            self.assertIsNotNone(result.error)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_empty_transcription(self):
        """Test empty/None input text normalization produces empty string."""
        self.assertEqual(ASRProcessor.normalize_text(""), "")
        self.assertEqual(ASRProcessor.normalize_text(None), "")
        self.assertEqual(ASRProcessor.normalize_text("   \n\t  "), "")

    def test_deterministic_asr_result_structure(self):
        """Test repeated calls on identical audio yield identical ASRResult attributes."""
        res1 = ASRProcessor.process_audio(self.synthetic_wav_path, mock_transcription=self.sample_text)
        res2 = ASRProcessor.process_audio(self.synthetic_wav_path, mock_transcription=self.sample_text)

        self.assertEqual(res1.source_path, res2.source_path)
        self.assertEqual(res1.transcribed_text, res2.transcribed_text)
        self.assertEqual(res1.success, res2.success)
        self.assertEqual(res1.confidence, res2.confidence)
        self.assertEqual(res1.error, res2.error)

    def test_asr_integration_with_extractor(self):
        """Test passing ASRResult transcribed_text directly into ProgressEventExtractor."""
        asr_result = ASRProcessor.process_audio(self.synthetic_wav_path, mock_transcription=self.sample_text)
        self.assertTrue(asr_result.success)

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-ASR-TEST",
            raw_text=asr_result.transcribed_text,
        )

        self.assertEqual(event.report_id, "REP-ASR-TEST")
        self.assertIn("CIV-007", event.activity_description)
        self.assertEqual(event.status, "In Progress")
        self.assertEqual(event.progress_value, 50.0)

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
