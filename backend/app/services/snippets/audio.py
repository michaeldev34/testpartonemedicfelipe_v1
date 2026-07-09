"""
Snippet: Python to record and transcribe result

Reusable audio recording and transcription pipeline for MediScript.
Wraps faster-whisper or mock backend into a simple interface.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioTranscriptionResult:
    """Result of an audio transcription operation."""

    text: str
    section_id: str
    duration_ms: int = 0
    backend: str = "mock"


def _mock_transcribe(audio_bytes: bytes, section_id: str) -> str:
    """Deterministic mock transcription based on audio content hash."""
    h = hashlib.sha256(audio_bytes).hexdigest()[:8]
    return (
        f"[MOCK TRANSCRIPTION for {section_id}] Audio hash {h}. "
        "No acute consolidation. Heart size normal. No pleural effusion."
    )


def _whisper_transcribe(audio_path: str, model_name: str = "base") -> str:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, beam_size=5)
    return " ".join(segment.text.strip() for segment in segments)


def transcribe_audio(
    audio_bytes: bytes,
    section_id: str,
    *,
    filename: str = "audio.webm",
    backend: str = "mock",
    whisper_model: str = "base",
    max_size_mb: int = 25,
) -> AudioTranscriptionResult:
    """
    Transcribe audio bytes into plaintext.

    Args:
        audio_bytes: Raw audio file bytes.
        section_id: Logical section identifier (e.g., 'findings').
        filename: Original filename for temp storage when using whisper.
        backend: 'mock' or 'whisper'.
        whisper_model: faster-whisper model name when backend='whisper'.
        max_size_mb: Maximum allowed audio size in megabytes.

    Returns:
        AudioTranscriptionResult with transcribed text.
    """
    max_bytes = max_size_mb * 1024 * 1024
    if len(audio_bytes) > max_bytes:
        raise ValueError(
            f"Audio file too large. Max size is {max_size_mb} MB."
        )

    if backend == "whisper":
        tmp_path = f"/tmp/{filename}"
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)
        try:
            text = _whisper_transcribe(tmp_path, model_name=whisper_model)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        text = _mock_transcribe(audio_bytes, section_id)

    return AudioTranscriptionResult(
        text=text,
        section_id=section_id,
        backend=backend,
    )
