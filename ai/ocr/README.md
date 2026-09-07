# OCR Processing Module (`ai/ocr/`)

The OCR Processing module provides lightweight, local image validation, OCR text extraction, and whitespace normalization for scanned field report images in the SIH26122 AI/ML pipeline.

---

## Key Features

1. **Local & Offline Execution**: Operates 100% locally without external cloud API dependencies.
2. **Supported Formats**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
3. **Graceful Error Handling**: Validates file existence, image integrity, and supported extensions without crashing. Returns structured `OCRResult` objects with `success=False` and clear error messages when image processing fails.
4. **Text Normalization**: Strips excessive whitespace, consecutive linebreaks, and padding to produce clean text for `ProgressEventExtractor`.
5. **No Hallucination**: Never invents or fabricates report text when OCR processing fails or images are empty.

---

## Architecture & Integration Flow

```text
Scanned Report Image (.png / .jpg) 
  --> OCRProcessor.process_image() 
  --> OCRResult (extracted_text, success, confidence, error)
  --> ProgressEventExtractor.extract_from_report(report_id, OCRResult.extracted_text)
  --> ExtractedProgressEvent
```

---

## Usage Example

```python
from pathlib import Path
from ai.ocr import OCRProcessor
from ai.extraction import ProgressEventExtractor

# Step 1: Process scanned report image
image_path = Path("ai/data/reports/synthetic_sample_report.png")
ocr_result = OCRProcessor.process_image(image_path)

if ocr_result.success:
    # Step 2: Pass extracted clean text to ProgressEventExtractor
    event = ProgressEventExtractor.extract_from_report(
        report_id="REP-OCR-001",
        raw_text=ocr_result.extracted_text,
    )
    print(f"Extracted activity: {event.activity_description}")
else:
    print(f"OCR failed: {ocr_result.error}")
```

---

## Dependencies

- **`Pillow` (`PIL`)**: Required for local image loading and format verification (already installed).
- **`pytesseract`**: Optional Python wrapper for local Tesseract-OCR binary engine.
