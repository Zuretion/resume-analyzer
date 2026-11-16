from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.embeddings import compute_score
from app.services.feedback import generate_suggestions
from app.services.parsing import extract_text

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    resume_text: Optional[str] = Form(None),
    job_description_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    job_description_file: Optional[UploadFile] = File(None)
) -> AnalyzeResponse:
    # 1. Извлекаем текст из файлов, если они есть
    resume_content = resume_text
    if resume_file:
        content = await resume_file.read()
        resume_content = extract_text(resume_file.filename, content)

    job_content = job_description_text
    if job_description_file:
        content = await job_description_file.read()
        job_content = extract_text(job_description_file.filename, content)

    if not resume_content or not job_content:
        return {"score": 0, "label": "No Fit", "suggestions": ["Please provide both resume and job description."]}

    # 2. Считаем score
    score, label = compute_score(resume_content, job_content)

    # 3. Генерируем советы
    suggestions = generate_suggestions(resume_content, job_content, score)

    return AnalyzeResponse(score=score, label=label, suggestions=suggestions)
