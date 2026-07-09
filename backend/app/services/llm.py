import os

from app.config import settings
from app.services.snippets import clinical


def _load_system_prompt() -> str:
    system_prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "clinical_system.md"
    )
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def diagnose(
    age: int,
    gender: str,
    preconditions: str,
    findings: str,
) -> list[str]:
    """
    Generate differential diagnoses using the clinical snippet.

    Delegates to `snippets.clinical.generate_clinical_report` and returns
    a list of diagnosis strings for backward compatibility with routes.
    """
    system_prompt = _load_system_prompt()
    report = clinical.generate_clinical_report(
        age=age,
        gender=gender,
        preconditions=preconditions,
        findings=findings,
        backend=settings.llm_backend,
        base_url=getattr(settings, "ollama_base_url", "http://localhost:11434"),
        model="llama3:8b-instruct",
        api_key=getattr(settings, "openai_api_key", ""),
        system_prompt=system_prompt,
    )
    return report.diagnoses


def generate_full_report(
    age: int,
    gender: str,
    preconditions: str,
    findings: str,
) -> dict:
    """
    Generate a full structured clinical report.

    Returns a dictionary with diagnoses, disclaimer, confidence,
    contraindications, and markdown-formatted report.
    """
    system_prompt = _load_system_prompt()
    report = clinical.generate_clinical_report(
        age=age,
        gender=gender,
        preconditions=preconditions,
        findings=findings,
        backend=settings.llm_backend,
        base_url=getattr(settings, "ollama_base_url", "http://localhost:11434"),
        model="llama3:8b-instruct",
        api_key=getattr(settings, "openai_api_key", ""),
        system_prompt=system_prompt,
    )
    return {
        "diagnoses": report.diagnoses,
        "disclaimer": report.disclaimer,
        "confidence": report.confidence,
        "contraindications": report.contraindications,
        "report_markdown": report.to_markdown(),
    }
