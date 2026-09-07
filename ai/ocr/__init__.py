"""
OCR Processing Module for SIH26122.

Provides local image validation, OCR text extraction, and whitespace normalization 
for scanned field reports prior to ProgressEventExtractor processing.
"""

from ai.ocr.ocr_processor import OCRProcessor, OCRResult

__all__ = [
    "OCRResult",
    "OCRProcessor",
]
