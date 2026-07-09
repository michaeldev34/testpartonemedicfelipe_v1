"""
Snippet: Python to gather patient data

Reusable data structures and validation for patient demographics
and study context used across the MediScript pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PatientData:
    """Container for patient demographics and study context."""

    age: int
    gender: str
    preconditions: str = ""
    findings: str = ""

    def __post_init__(self) -> None:
        if self.age < 0:
            raise ValueError("Age must be a non-negative integer.")
        allowed_genders = {"male", "female", "other", "unknown"}
        if self.gender not in allowed_genders:
            raise ValueError(
                f"Gender must be one of: {', '.join(sorted(allowed_genders))}."
            )

    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "gender": self.gender,
            "preconditions": self.preconditions,
            "findings": self.findings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> PatientData:
        return cls(
            age=int(data.get("age", 0)),
            gender=str(data.get("gender", "unknown")),
            preconditions=str(data.get("preconditions", "")),
            findings=str(data.get("findings", "")),
        )


def validate_patient_payload(payload: dict) -> PatientData:
    """Validate an incoming patient payload and return a PatientData instance."""
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary.")
    return PatientData.from_dict(payload)
