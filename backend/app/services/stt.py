import os

from app.config import settings
from app.services.snippets import audio


def transcribe(audio_bytes: bytes, section_id: str, filename: str = "audio.webm") -> str:
    """
    Transcribe audio bytes using the audio snippet.

    Delegates to `snippets.audio.transcribe_audio` and returns plaintext.
    """
    result = audio.transcribe_audio(
        audio_bytes=audio_bytes,
        section_id=section_id,
        filename=filename,
        backend=settings.stt_backend,
        whisper_model=getattr(settings, "whisper_model", "base"),
        max_size_mb=settings.max_audio_size_mb,
    )
    return result.text
