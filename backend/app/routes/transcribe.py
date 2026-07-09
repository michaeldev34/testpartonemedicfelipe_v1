from fastapi import APIRouter, File, Form, HTTPException

from app.services.snippets import audio as audio_snippet

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(
    audio: bytes = File(...),
    section_id: str = Form(...),
):
    if not audio:
        raise HTTPException(status_code=400, detail="Empty audio file.")

    try:
        result = audio_snippet.transcribe_audio(
            audio_bytes=audio,
            section_id=section_id,
            filename="upload.webm",
        )
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}") from exc

    return {
        "text": result.text,
        "section_id": result.section_id,
        "backend": result.backend,
    }
