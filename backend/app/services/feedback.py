"""
Генерация текстовых советов по улучшению резюме через Phi-3-mini.

Phi-3-mini здесь НЕ дообучается — она просто вызывается с промптом,
который собирает в себе текст резюме, вакансии и посчитанный score.

Пока FEEDBACK_MOCK=true в .env, реальная модель не грузится вообще —
это специально, чтобы можно было поднять и проверить весь backend
без тяжёлой LLM на борту. Отключаете мок, когда дойдёте до этого
шага роадмапа (этап 2/4).
"""

from functools import lru_cache

from app.core.config import get_settings

PROMPT_TEMPLATE = """Ты — ассистент по подбору персонала. Вот резюме кандидата и описание вакансии.
Оценка соответствия: {score}/100.

Резюме:
{resume}

Вакансия:
{job_description}

Дай 3-4 коротких, конкретных совета, как улучшить резюме под эту вакансию.
Отвечай списком, без вступления."""


def _mock_suggestions(score: int) -> list[str]:
    if score >= 75:
        return [
            "Резюме уже хорошо соответствует вакансии — проверьте, что ключевые навыки идут в начале.",
            "Добавьте конкретные метрики к последним проектам (цифры убеждают сильнее описаний).",
        ]
    return [
        "Добавьте в резюме ключевые слова и технологии из описания вакансии.",
        "Опишите опыт конкретными результатами, а не только списком обязанностей.",
        "Сократите разделы, не относящиеся напрямую к этой вакансии.",
    ]


@lru_cache
def _get_pipeline():
    # Импорт transformers и загрузка весов — только когда мок выключен,
    # чтобы не тянуть тяжёлые зависимости на каждый старт сервера.
    from transformers import pipeline

    settings = get_settings()
    return pipeline(
        "text-generation",
        model=settings.feedback_model_name,
        device_map="auto",
    )


def generate_suggestions(resume_text: str, job_description_text: str, score: int) -> list[str]:
    settings = get_settings()
    if settings.feedback_mock:
        return _mock_suggestions(score)

    prompt = PROMPT_TEMPLATE.format(
        score=score, resume=resume_text, job_description=job_description_text
    )
    generator = _get_pipeline()
    output = generator(prompt, max_new_tokens=220, do_sample=False)[0]["generated_text"]
    # Модель продолжает текст после промпта — забираем только продолжение
    completion = output[len(prompt):].strip()

    # Разбиваем на строки списка; простая эвристика, можно улучшить позже
    lines = [line.strip("-• ").strip() for line in completion.splitlines() if line.strip()]
    return lines[:4] if lines else [completion]
