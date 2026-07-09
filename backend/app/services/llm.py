import json
import os
from typing import List

import httpx
from app.config import settings

SYSTEM_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "prompts", "clinical_system.md"
)


def _load_system_prompt() -> str:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _mock_diagnose(age: int, gender: str, preconditions: str, findings: str) -> List[str]:
    return [
        "Community-acquired pneumonia (low-to-moderate confidence) — correlate with clinical symptoms and consider follow-up imaging if indicated.",
        "Atelectasis (moderate confidence) — often secondary to reduced ventilation; evaluate for underlying cause.",
        "Normal variant / no acute cardiopulmonary process (moderate confidence) — if patient is asymptomatic, routine follow-up may be sufficient.",
    ]


def _ollama_diagnose(age: int, gender: str, preconditions: str, findings: str) -> List[str]:
    system_prompt = _load_system_prompt()
    user_prompt = (
        f"Patient Age: {age}\n"
        f"Gender: {gender}\n"
        f"Preconditions: {preconditions or 'None reported'}\n"
        f"Findings: {findings}\n\n"
        "Provide a JSON array of potential differential diagnoses. Each item should be a concise string."
    )

    payload = {
        "model": "llama3:8b-instruct",
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2, "num_ctx": 4096},
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "[]")
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        if isinstance(parsed, dict) and "diagnoses" in parsed:
            return [str(item) for item in parsed["diagnoses"]]
        return [str(parsed)]


def _openai_diagnose(age: int, gender: str, preconditions: str, findings: str) -> List[str]:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package is required for LLM_BACKEND=openai")

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=settings.openai_api_key)
    system_prompt = _load_system_prompt()
    user_prompt = (
        f"Patient Age: {age}\n"
        f"Gender: {gender}\n"
        f"Preconditions: {preconditions or 'None reported'}\n"
        f"Findings: {findings}\n\n"
        "Respond with a JSON object containing a key 'diagnoses' whose value is an array of strings."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content
    parsed = json.loads(content)
    if isinstance(parsed, dict) and "diagnoses" in parsed:
        return [str(item) for item in parsed["diagnoses"]]
    return [str(parsed)]


def diagnose(age: int, gender: str, preconditions: str, findings: str) -> List[str]:
    if settings.llm_backend == "ollama":
        return _ollama_diagnose(age, gender, preconditions, findings)
    if settings.llm_backend == "openai":
        return _openai_diagnose(age, gender, preconditions, findings)
    return _mock_diagnose(age, gender, preconditions, findings)
