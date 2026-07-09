from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field, ValidationError
from app.services.llm import diagnose

router = APIRouter()


class DiagnoseRequest(BaseModel):
    age: int = Field(ge=0, description="Patient age in years")
    gender: str = Field(pattern="^(male|female|other|unknown)$", description="Patient gender")
    preconditions: str = Field(default="", description="Known preconditions")
    findings: str = Field(min_length=1, description="Radiology findings text")


@router.post("/analyze-diagnose")
async def analyze_diagnose(request: DiagnoseRequest):
    try:
        results = diagnose(
            age=request.age,
            gender=request.gender,
            preconditions=request.preconditions,
            findings=request.findings,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {exc}") from exc

    disclaimer = (
        "Decision-support only — confirm with supervising physician."
    )
    return {"diagnoses": results, "disclaimer": disclaimer}
