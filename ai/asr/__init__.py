"""
ASR (Automatic Speech Recognition) Module for SIH26122.

Provides local audio file validation, speech-to-text transcription, 
and whitespace normalization for voice-based field reports.
"""

from ai.asr.asr_processor import ASRProcessor, ASRResult

__all__ = [
    "ASRResult",
    "ASRProcessor",
]
