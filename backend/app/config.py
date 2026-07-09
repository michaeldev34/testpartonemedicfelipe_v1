import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    stt_backend: str = os.getenv("STT_BACKEND", "mock")
    llm_backend: str = os.getenv("LLM_BACKEND", "mock")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    max_audio_size_mb: int = int(os.getenv("MAX_AUDIO_SIZE_MB", "10"))
    whisper_model: str = os.getenv("WHISPER_MODEL", "Systran/faster-whisper-small")

    class Config:
        env_file = ".env"


settings = Settings()
