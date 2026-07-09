# MediScript

AI-powered radiology assistant — Proof-of-Concept.

## Quick Start

```bash
cd mediscript
docker compose up --build
```

Open http://localhost:8080 in your browser.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STT_BACKEND` | `mock` | Speech-to-text backend: `mock` or `whisper` |
| `LLM_BACKEND` | `mock` | LLM backend: `mock`, `ollama`, or `openai` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key (required if `LLM_BACKEND=openai`) |
| `MAX_AUDIO_SIZE_MB` | `10` | Maximum audio upload size in MB |
| `WHISPER_MODEL` | `Systran/faster-whisper-small` | HuggingFace model ID for faster-whisper |

## Backends

### Mock (default)
No external services required. Returns deterministic placeholder text for transcription and a fixed list of differential diagnoses.

### Whisper (STT)
Set `STT_BACKEND=whisper`. The backend uses `faster-whisper` locally on CPU. Default model is `Systran/faster-whisper-small` (~250 MB). Override with `WHISPER_MODEL` (e.g., `tiny` for ~75 MB).

### Ollama (LLM)
Set `LLM_BACKEND=ollama` and ensure Ollama is running with `llama3:8b-instruct` pulled:
```bash
ollama pull llama3:8b-instruct
```

### OpenAI (LLM)
Set `LLM_BACKEND=openai` and provide `OPENAI_API_KEY`. Uses `gpt-4o-mini` by default.

## API Reference

### POST /api/transcribe
Transcribes an audio file.

**Request:** `multipart/form-data`
- `audio`: audio file (webm, wav, mp3, etc.)
- `section_id`: string identifier for the section

**Response:**
```json
{ "text": "transcribed text here" }
```

### POST /api/analyze-diagnose
Generates differential diagnoses.

**Request:**
```json
{
  "age": 45,
  "gender": "male",
  "preconditions": "COPD",
  "findings": "No acute consolidation. Heart size normal."
}
```

**Response:**
```json
{
  "diagnoses": [
    "Community-acquired pneumonia (low-to-moderate confidence)...",
    "Atelectasis (moderate confidence)..."
  ],
  "disclaimer": "Decision-support only — confirm with supervising physician."
}
```

### GET /healthz
Health check endpoint. Returns backend configuration.

## Running Tests

```bash
# Backend unit tests (run from repo root)
cd backend
python -m pytest tests/ -v
```

## Architecture

See `docs/architecture.mmd` for the cloud deployment diagram.

## Guardrails

- This tool is **decision-support only** and is **not** a final diagnosis.
- Every diagnosis response includes a disclaimer to consult a supervising physician.
- The LLM is instructed to state uncertainty and list contraindications.
- No PHI is persisted in the PoC unless explicitly encrypted.
- Audio uploads are size-limited (default 10 MB).
