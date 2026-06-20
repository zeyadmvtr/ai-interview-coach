"""
Module 8: Voice Transcription.

Lazy-loaded singleton faster-whisper model. Loading the model is expensive
(seconds, plus VRAM/RAM), so we load it once on first use and reuse it for
every request rather than per-request.
"""
import os
import tempfile

from app.core.config import get_settings
from app.core.exceptions import TranscriptionError
from app.core.logging import get_logger

logger = get_logger(__name__)

_SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a"}

_model = None  # lazy singleton, populated by _get_model()


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel  # imported lazily: heavy import

        settings = get_settings()
        logger.info(
            "Loading faster-whisper model '%s' (device=%s, compute_type=%s)...",
            settings.whisper_model_size,
            settings.whisper_device,
            settings.whisper_compute_type,
        )
        _model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        logger.info("faster-whisper model loaded.")
    return _model


class WhisperService:
    """Transcribes interview answer audio to text using faster-whisper."""

    def transcribe_audio(self, file_bytes: bytes, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in _SUPPORTED_EXTENSIONS:
            raise TranscriptionError(
                f"Unsupported audio format '{ext}'. Supported formats: {sorted(_SUPPORTED_EXTENSIONS)}"
            )
        if not file_bytes:
            raise TranscriptionError("Uploaded audio file is empty.")

        model = _get_model()

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            segments, info = model.transcribe(tmp_path, beam_size=5, vad_filter=True)
            transcript = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:
            raise TranscriptionError(f"Transcription failed: {exc}") from exc
        finally:
            os.unlink(tmp_path)

        if not transcript:
            raise TranscriptionError(
                "No speech detected in audio. Please check the recording and try again."
            )

        logger.info(
            "Transcribed %d bytes of audio (%s) -> %d chars, detected_language=%s",
            len(file_bytes),
            ext,
            len(transcript),
            getattr(info, "language", "unknown"),
        )
        return transcript
