# Multi-Modal AI Pipeline & Suggestion Engine (`ai/pipeline/`)

The Multi-Modal AI Pipeline orchestrates end-to-end field report processing across heterogeneous inputs (Text, Scanned OCR Images, Voice Audio ASR) to produce structured, explainable **AI Suggestions** (`AISuggestion`).

---

## Architectural Principles

1. **Multi-Modal Input Processing**:
   - **Text Input**: Passed directly to `ProgressEventExtractor` (`source_type="text"`).
   - **Image Input (`.png`, `.jpg`, etc.)**: Processed by local `OCRProcessor` before passing extracted text to `ProgressEventExtractor` (`source_type="image_ocr"`).
   - **Audio Input (`.wav`, `.mp3`, etc.)**: Processed by local `ASRProcessor` before passing transcribed text to `ProgressEventExtractor` (`source_type="audio_asr"`).
2. **Strict Non-Mutation Policy**:
   - The AI **NEVER** directly updates or applies changes to the project schedule database.
   - `human_validation_required` is **ALWAYS `True`** for every generated `AISuggestion`.
   - `AUTO_APPROVE` represents an AI recommendation label based on strong evidence; human confirmation remains mandatory.
3. **Decision Priority Precedence**:
   - **`CRITICAL_REVIEW` > `HUMAN_REVIEW` > `AUTO_APPROVE`**.
   - Flagged high-severity conflicts (defects/breakdowns, inverted dates, status regressions) or OCR/ASR input failures strictly force `CRITICAL_REVIEW`, overriding high match scores.
4. **Source Provenance Preservation**:
   - The `source_type` attribute (`text`, `image_ocr`, `audio_asr`) is explicitly tracked and preserved in every `AISuggestion`.

---

## End-to-End Workflow

```text
Multi-Modal Input (Text / Image Path / Audio Path)
  │
  ├──► OCRProcessor (if Image file) ──────┐
  ├──► ASRProcessor (if Audio file) ──────┼──► ProgressEventExtractor
  └──► Raw Text (if String / Dict) ───────┘           │
                                                      ▼
                                              ExtractedProgressEvent
                                                      │
                                                      ▼
                                              ActivityMatcher (L5/L6 Candidates)
                                                      │
                                                      ▼
                                              ConfidenceScorer (Multi-signal Reliability)
                                                      │
                                                      ▼
                                              ConflictDetector (Defects & Regressions)
                                                      │
                                                      ▼
                                              Decision Engine (Priority Rules)
                                                      │
                                                      ▼
                                              AISuggestion (human_validation_required=True)
```

---

## Usage Example

```python
from pathlib import Path
from ai.data.schedule_loader import ScheduleLoader
from ai.pipeline import ReportPipeline

# Load schedule dataset
dataset = ScheduleLoader.load_from_directory(Path("ai/data/schedule"))

# 1. Process Text Report Input
sugg_text = ReportPipeline.process_input(
    "CIV-007 Concrete curing and wet matting for Column C-101 foundation. Status: In Progress, progress: 50%.",
    schedule_target=dataset,
)
print(f"Action: {sugg_text.recommended_action}, Source: {sugg_text.source_type}")

# 2. Process Scanned OCR Image Input
sugg_image = ReportPipeline.process_input(
    Path("ai/data/reports/synthetic_sample_report.png"),
    schedule_target=dataset,
)
print(f"Action: {sugg_image.recommended_action}, Source: {sugg_image.source_type}")

# 3. Heterogeneous Batch Processing
inputs = [
    {"report_id": "REP-001", "raw_text": "CIV-007 Concrete curing 50% completed."},
    Path("ai/data/reports/synthetic_sample_report.png"),
    Path("ai/data/reports/synthetic_sample_report.wav"),
]
batch_suggestions = ReportPipeline.process_heterogeneous_batch(inputs, schedule_target=dataset)
```
