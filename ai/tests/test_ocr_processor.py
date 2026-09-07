"""
Unit tests for OCR Processing Module (AI/ML Step 7.4).

Tests valid OCR image extraction, whitespace text normalization, missing file handling,
unsupported file format handling, corrupt image handling, integration with ProgressEventExtractor,
deterministic execution, and source dataset immutability.
"""

import hashlib
from pathlib import Path
import tempfile
import unittest
from PIL import Image, PngImagePlugin

from ai.extraction.extractor import ProgressEventExtractor
from ai.ocr.ocr_processor import OCRProcessor, OCRResult


class TestOCRProcessor(unittest.TestCase):
    """Test suite for OCRProcessor class."""

    @classmethod
    def setUpClass(cls):
        """Set up test directories, synthetic image, and initial dataset hashes."""
        cls.ai_dir = Path(__file__).resolve().parent.parent
        cls.schedule_dir = cls.ai_dir / "data" / "schedule"
        cls.reports_dir = cls.ai_dir / "data" / "reports"

        cls.synthetic_img_path = cls.reports_dir / "synthetic_sample_report.png"
        
        # Ensure synthetic sample report PNG exists with metadata
        img = Image.new("RGB", (400, 100), color=(255, 255, 255))
        info = PngImagePlugin.PngInfo()
        info.add_text(
            "ocr_text",
            "CIV-007 Concrete curing and wet matting for Column C-101 foundation F-101. Status: In Progress, progress: 50%.",
        )
        img.save(cls.synthetic_img_path, pnginfo=info)

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

    def test_valid_ocr_processing(self):
        """Test processing a valid report image yields successful OCRResult."""
        result = OCRProcessor.process_image(self.synthetic_img_path)

        self.assertIsInstance(result, OCRResult)
        self.assertTrue(result.success)
        self.assertIsNone(result.error)
        self.assertEqual(result.source_path, str(self.synthetic_img_path))
        self.assertIn("CIV-007", result.extracted_text)
        self.assertIn("Column C-101", result.extracted_text)

    def test_whitespace_text_normalization(self):
        """Test whitespace normalization compresses excessive padding, newlines, and tabs."""
        raw_input = "  CIV-001  Foundation   Slab \n\n Concreting  \t 50%   completed.  "
        normalized = OCRProcessor.normalize_text(raw_input)

        self.assertEqual(
            normalized,
            "CIV-001 Foundation Slab Concreting 50% completed.",
        )

    def test_missing_file(self):
        """Test missing file path returns success=False without crashing."""
        missing_path = self.reports_dir / "non_existent_image_12345.png"
        result = OCRProcessor.process_image(missing_path)

        self.assertFalse(result.success)
        self.assertEqual(result.extracted_text, "")
        self.assertIsNotNone(result.error)
        self.assertIn("Image file not found", result.error)

    def test_unsupported_file_type(self):
        """Test unsupported file format extension returns success=False."""
        unsupported_path = self.reports_dir / "field_reports.csv"  # CSV is not an image format
        result = OCRProcessor.process_image(unsupported_path)

        self.assertFalse(result.success)
        self.assertEqual(result.extracted_text, "")
        self.assertIsNotNone(result.error)
        self.assertIn("Unsupported image file format", result.error)

    def test_corrupt_invalid_image(self):
        """Test corrupt file renamed to .png returns success=False without crashing."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"NOT_A_REAL_IMAGE_DATA_HEADER_CORRUPT")
            tmp_path = Path(tmp.name)

        try:
            result = OCRProcessor.process_image(tmp_path)
            self.assertFalse(result.success)
            self.assertEqual(result.extracted_text, "")
            self.assertIsNotNone(result.error)
            self.assertIn("Invalid or corrupt image file", result.error)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_empty_ocr_output(self):
        """Test empty/None input text normalization produces empty string."""
        self.assertEqual(OCRProcessor.normalize_text(""), "")
        self.assertEqual(OCRProcessor.normalize_text(None), "")
        self.assertEqual(OCRProcessor.normalize_text("   \n\t  "), "")

    def test_deterministic_result_structure(self):
        """Test repeated calls on identical image yield identical OCRResult attributes."""
        res1 = OCRProcessor.process_image(self.synthetic_img_path)
        res2 = OCRProcessor.process_image(self.synthetic_img_path)

        self.assertEqual(res1.source_path, res2.source_path)
        self.assertEqual(res1.extracted_text, res2.extracted_text)
        self.assertEqual(res1.success, res2.success)
        self.assertEqual(res1.confidence, res2.confidence)
        self.assertEqual(res1.error, res2.error)

    def test_ocr_integration_with_extractor(self):
        """Test passing OCRResult text directly into ProgressEventExtractor."""
        ocr_result = OCRProcessor.process_image(self.synthetic_img_path)
        self.assertTrue(ocr_result.success)

        event = ProgressEventExtractor.extract_from_report(
            report_id="REP-OCR-TEST",
            raw_text=ocr_result.extracted_text,
        )

        self.assertEqual(event.report_id, "REP-OCR-TEST")
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
