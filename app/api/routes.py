from fastapi import APIRouter

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.embeddings import compute_score
from app.services.feedback import generate_suggestions

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    score, label = compute_score(payload.resume_text, payload.job_description_text)
    suggestions = generate_suggestions(payload.resume_text, payload.job_description_text, score)
    return AnalyzeResponse(score=score, label=label, suggestions=suggestions)
