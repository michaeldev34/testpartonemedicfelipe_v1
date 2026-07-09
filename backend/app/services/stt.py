import hashlib
import os
from typing import Optional

from app.config import settings

MAX_AUDIO_BYTES = settings.max_audio_size_mb * 1024 * 1024


def _mock_transcribe(audio_bytes: bytes, section_id: str) -> str:
    """Deterministic mock transcription based on audio content hash."""
    h = hashlib.sha256(audio_bytes).hexdigest()[:8]
    return f"[MOCK TRANSCRIPTION for {section_id}] Audio hash {h}. No acute consolidation. Heart size normal. No pleural effusion."


def _whisper_transcribe(audio_path: str) -> str:
    from faster_whisper import WhisperModel

    model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, beam_size=5)
    return " ".join(segment.text.strip() for segment in segments)


def transcribe(audio_bytes: bytes, section_id: str, filename: str = "audio.webm") -> str:
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise ValueError(
            f"Audio file too large. Max size is {settings.max_audio_size_mb} MB."
        )

    if settings.stt_backend == "whisper":
        tmp_path = f"/tmp/{filename}"
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)
        try:
            return _whisper_transcribe(tmp_path)
        finally:
            os.remove(tmp_path)
    else:
        return _mock_transcribe(audio_bytes, section_id)
