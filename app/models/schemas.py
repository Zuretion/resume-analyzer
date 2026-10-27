"""
Pydantic-схемы запроса и ответа для /api/analyze.

FastAPI сам валидирует вход по этим схемам и генерирует из них
документацию (доступна на /docs после запуска сервера).
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Текст резюме")
    job_description_text: str = Field(..., min_length=1, description="Текст вакансии")


class AnalyzeResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Оценка соответствия, 0-100")
    label: str = Field(..., description="Good Fit / Potential Fit / No Fit")
    suggestions: list[str] = Field(..., description="Конкретные советы по улучшению резюме")
