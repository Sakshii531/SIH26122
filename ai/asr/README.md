# ASR (Automatic Speech Recognition) Module (`ai/asr/`)

The ASR module provides local audio file validation, speech-to-text transcription processing, and text whitespace normalization for voice-based field progress reports in the SIH26122 AI/ML pipeline.

---

## Key Features

1. **Local & Offline Execution**: Operates 100% locally without external cloud API key requirements.
2. **Supported Formats**: `.wav`, `.mp3`, `.m4a`, `.ogg`, `.flac`, `.wma`.
3. **Strict Non-Fallback Policy**:
   - `ASRProcessor.process_audio()` requires an active local/offline ASR engine (or explicit mock parameter passed by test fixtures).
   - Companion `.txt` transcript files (e.g. `synthetic_sample_report.txt`) are **test fixtures only** and are **never** silently read as runtime ASR fallbacks.
4. **Graceful Error Handling**: Validates audio file existence, format extension, and WAV wave header integrity without crashing. Returns structured `ASRResult` objects with `success=False` and clear error messages when ASR engine processing fails or audio contains no speech.
5. **Text Normalization**: Strips excessive whitespace, consecutive linebreaks, and padding to produce clean text for `ProgressEventExtractor`.
6. **No Hallucination**: Never invents or fabricates voice report text when ASR processing fails.

---

## Architecture & Integration Flow

```text
Voice Report Audio (.wav / .mp3) 
  --> ASRProcessor.process_audio() 
  --> ASRResult (transcribed_text, success, confidence, error)
  --> ProgressEventExtractor.extract_from_report(report_id, ASRResult.transcribed_text)
  --> ExtractedProgressEvent
```

---

## Usage Example

```python
from pathlib import Path
from ai.asr import ASRProcessor
from ai.extraction import ProgressEventExtractor

# Step 1: Process voice report audio file (passing explicit mock transcript for test environment)
audio_path = Path("ai/data/reports/synthetic_sample_report.wav")
asr_result = ASRProcessor.process_audio(audio_path, mock_transcription="CIV-007 Concrete curing 50% completed.")

if asr_result.success:
    # Step 2: Pass transcribed clean text to ProgressEventExtractor
    event = ProgressEventExtractor.extract_from_report(
        report_id="REP-ASR-001",
        raw_text=asr_result.transcribed_text,
    )
    print(f"Extracted activity: {event.activity_description}")
else:
    print(f"ASR failed: {asr_result.error}")
```

---

## Dependencies

- **`wave`**: Python standard library module for WAV audio format header and sample validation.
- **`SpeechRecognition`**: Optional Python wrapper for local offline ASR recognition engines (`speech_recognition`).
