from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import transcribe, diagnose

app = FastAPI(
    title="MediScript API",
    description="AI-powered radiology assistant backend.",
    version="0.1.0",
)

# CORS for local development; in production remove or restrict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "stt_backend": settings.stt_backend,
        "llm_backend": settings.llm_backend,
    }


app.include_router(transcribe.router, prefix="/api")
app.include_router(diagnose.router, prefix="/api")
