"""
ASR (Automatic Speech Recognition) Processor Module for SIH26122.

Provides local audio file validation, speech-to-text transcription processing, 
and text whitespace normalization for voice field reports.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional, Set, Union
import wave

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False


@dataclass
class ASRResult:
    """
    Structured result of ASR voice report transcription.
    """
    source_path: str
    transcribed_text: str
    success: bool
    confidence: Optional[float] = None
    error: Optional[str] = None


class ASRProcessor:
    """
    Local, offline ASR processor for audio voice field reports.
    Converts audio report inputs into clean text for ProgressEventExtractor.
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        ".wav",
        ".mp3",
        ".m4a",
        ".ogg",
        ".flac",
        ".wma",
    }

    @classmethod
    def process_audio(
        cls,
        audio_path: Union[str, Path],
        mock_transcription: Optional[str] = None,
    ) -> ASRResult:
        """
        Process an audio file and transcribe voice report text.
        
        Args:
            audio_path: Path to the target audio file.
            mock_transcription: Optional mock transcript string provided explicitly by test fixtures.
            
        Returns:
            ASRResult containing source_path, transcribed_text, success, confidence, and error.
        """
        path = Path(audio_path)
        path_str = str(path)

        # 1. File existence validation
        if not path.exists():
            return ASRResult(
                source_path=path_str,
                transcribed_text="",
                success=False,
                confidence=None,
                error=f"Audio file not found: '{path_str}'",
            )

        # 2. File extension validation
        ext = path.suffix.lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            return ASRResult(
                source_path=path_str,
                transcribed_text="",
                success=False,
                confidence=None,
                error=f"Unsupported audio file format: '{ext}'. Supported formats: {sorted(cls.SUPPORTED_EXTENSIONS)}",
            )

        # 3. Audio file integrity validation (.wav check)
        if ext == ".wav":
            try:
                with wave.open(path_str, "rb") as wav_file:
                    n_channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    framerate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()
                    if n_frames == 0 or n_channels == 0:
                        return ASRResult(
                            source_path=path_str,
                            transcribed_text="",
                            success=False,
                            confidence=None,
                            error="Empty audio file containing 0 samples.",
                        )
            except wave.Error as e:
                return ASRResult(
                    source_path=path_str,
                    transcribed_text="",
                    success=False,
                    confidence=None,
                    error=f"Invalid or corrupt audio file: {str(e)}",
                )
            except Exception as e:
                return ASRResult(
                    source_path=path_str,
                    transcribed_text="",
                    success=False,
                    confidence=None,
                    error=f"Failed to open audio file: {str(e)}",
                )

        # 4. Transcription Processing
        raw_text = ""
        confidence = None
        asr_error = None

        # Option A: Explicit mock_transcription passed directly by test fixture
        if mock_transcription is not None:
            raw_text = mock_transcription
            confidence = 0.95
        # Option B: Run actual configured local ASR engine
        elif SPEECH_RECOGNITION_AVAILABLE and ext == ".wav":
            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(path_str) as source:
                    audio_data = recognizer.record(source)
                    if hasattr(recognizer, "recognize_sphinx"):
                        raw_text = recognizer.recognize_sphinx(audio_data)
                        confidence = 0.85
                    else:
                        asr_error = "No local offline ASR recognition method available on Recognizer instance."
            except Exception as ex:
                asr_error = f"Local ASR engine error: {str(ex)}"
        else:
            if not SPEECH_RECOGNITION_AVAILABLE:
                asr_error = "SpeechRecognition library is not installed."
            else:
                asr_error = f"No local ASR decoder available for format '{ext}'."

        # 5. Output Normalization & Failure Handling
        normalized_text = cls.normalize_text(raw_text)

        if not normalized_text:
            err_msg = asr_error or "ASR engine produced empty transcript."
            return ASRResult(
                source_path=path_str,
                transcribed_text="",
                success=False,
                confidence=None,
                error=err_msg,
            )

        return ASRResult(
            source_path=path_str,
            transcribed_text=normalized_text,
            success=True,
            confidence=confidence,
            error=None,
        )

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """
        Normalize ASR transcribed text by compressing excessive whitespace.
        
        Args:
            text: Raw transcript string.
            
        Returns:
            Normalized, single-space separated text string.
        """
        if not text:
            return ""
        clean = " ".join(text.strip().split())
        return clean
