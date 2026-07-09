"""
Snippet: Python to think and output final clinical report

Reusable clinical reasoning engine for MediScript.
Wraps Ollama, OpenAI, or mock backend into a structured report.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ClinicalReport:
    """Structured clinical report output."""

    diagnoses: List[str] = field(default_factory=list)
    disclaimer: str = "Decision-support only — confirm with supervising physician."
    confidence: str = "moderate"
    contraindications: List[str] = field(default_factory=list)
    raw_response: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "diagnoses": self.diagnoses,
            "disclaimer": self.disclaimer,
            "confidence": self.confidence,
            "contraindications": self.contraindications,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Clinical Report",
            "",
            f"**Confidence:** {self.confidence}",
            "",
            "## Potential Differential Diagnoses",
            "",
        ]
        for i, d in enumerate(self.diagnoses, 1):
            lines.append(f"{i}. {d}")
        lines.append("")
        if self.contraindications:
            lines.extend([
                "## Contraindications / Red Flags",
                "",
            ])
            for c in self.contraindications:
                lines.append(f"- {c}")
            lines.append("")
        lines.extend([
            "---",
            f"*{self.disclaimer}*",
        ])
        return "\n".join(lines)


def _mock_generate_report(
    age: int,
    gender: str,
    preconditions: str,
    findings: str,
) -> ClinicalReport:
    """Deterministic mock clinical report."""
    return ClinicalReport(
        diagnoses=[
            "Community-acquired pneumonia (low-to-moderate confidence) — correlate with clinical symptoms and consider follow-up imaging if indicated.",
            "Atelectasis (moderate confidence) — often secondary to reduced ventilation; evaluate for underlying cause.",
            "Normal variant / no acute cardiopulmonary process (moderate confidence) — if patient is asymptomatic, routine follow-up may be sufficient.",
        ],
        confidence="moderate",
        contraindications=[
            "If patient is hemodynamically unstable, escalate care immediately.",
            "Correlate with lab results (CBC, CRP) before finalizing diagnosis.",
        ],
    )


def _ollama_generate_report(
    age: int,
    gender: str,
    preconditions: str,
    findings: str,
    base_url: str = "http://localhost:11434",
    model: str = "llama3:8b-instruct",
    system_prompt: str = "",
) -> ClinicalReport:
    import httpx

    user_prompt = (
        f"Patient Age: {age}\n"
        f"Gender: {gender}\n"
        f"Preconditions: {preconditions or 'None reported'}\n"
        f"Findings: {findings}\n\n"
        "Provide a JSON object with keys: diagnoses (array of strings), "
        "confidence (string), contraindications (array of strings)."
    )

    payload = {
        "model": model,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2, "num_ctx": 4096},
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(f"{base_url}/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "{}")
        parsed = json.loads(raw)

    diagnoses = [str(x) for x in parsed.get("diagnoses", [])]
    confidence = str(parsed.get("confidence", "moderate"))
    contraindications = [str(x) for x in parsed.get("contraindications", [])]

    return ClinicalReport(
        diagnoses=diagnoses,
        confidence=confidence,
        contraindications=contraindications,
        raw_response=raw,
    )


def _openai_generate_report(
    age: int,
    gender: str,
    preconditions: str,
    findings: str,
    api_key: str = "",
    model: str = "gpt-4o-mini",
    system_prompt: str = "",
) -> ClinicalReport:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is required for LLM_BACKEND=openai") from exc

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    user_prompt = (
        f"Patient Age: {age}\n"
        f"Gender: {gender}\n"
        f"Preconditions: {preconditions or 'None reported'}\n"
        f"Findings: {findings}\n\n"
        "Respond with a JSON object containing keys: diagnoses (array of strings), "
        "confidence (string), contraindications (array of strings)."
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content
    parsed = json.loads(content or "{}")

    diagnoses = [str(x) for x in parsed.get("diagnoses", [])]
    confidence = str(parsed.get("confidence", "moderate"))
    contraindications = [str(x) for x in parsed.get("contraindications", [])]

    return ClinicalReport(
        diagnoses=diagnoses,
        confidence=confidence,
        contraindications=contraindications,
        raw_response=content,
    )


def generate_clinical_report(
    age: int,
    gender: str,
    preconditions: str,
    findings: str,
    *,
    backend: str = "mock",
    base_url: str = "http://localhost:11434",
    model: str = "llama3:8b-instruct",
    api_key: str = "",
    system_prompt: str = "",
) -> ClinicalReport:
    """
    Generate a structured clinical report from patient data and findings.

    Args:
        age: Patient age in years.
        gender: Patient gender.
        preconditions: Known preconditions.
        findings: Radiology findings text.
        backend: 'mock', 'ollama', or 'openai'.
        base_url: Ollama base URL when backend='ollama'.
        model: Model name for the selected backend.
        api_key: OpenAI API key when backend='openai'.
        system_prompt: Clinical system prompt to inject.

    Returns:
        ClinicalReport with diagnoses, confidence, and contraindications.
    """
    if backend == "ollama":
        return _ollama_generate_report(
            age, gender, preconditions, findings,
            base_url=base_url, model=model, system_prompt=system_prompt,
        )
    if backend == "openai":
        return _openai_generate_report(
            age, gender, preconditions, findings,
            api_key=api_key, model=model, system_prompt=system_prompt,
        )
    return _mock_generate_report(age, gender, preconditions, findings)
