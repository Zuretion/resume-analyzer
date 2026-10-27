"""
Матчинг резюме и вакансии через эмбеддинги (sentence-transformers).

На старте, пока дообученной модели ещё нет, используется базовая
all-MiniLM-L6-v2 — работает хуже, но позволяет проверить весь пайплайн
end-to-end. Как только в ml/model/ появятся веса дообученной модели
(этап 1 роадмапа), EMBEDDING_MODEL_PATH в .env указывает на неё, и
подмена происходит без изменений в этом файле.
"""

import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util

from app.core.config import get_settings

BASE_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def get_model() -> SentenceTransformer:
    settings = get_settings()
    model_path = settings.embedding_model_path
    # Если дообученной модели ещё нет на диске — откатываемся на базовую,
    # чтобы сервер не падал при первом запуске без обучения в Colab.
    if model_path and os.path.isdir(model_path) and os.listdir(model_path):
        return SentenceTransformer(model_path)
    return SentenceTransformer(BASE_MODEL_NAME)


def compute_score(resume_text: str, job_description_text: str) -> tuple[int, str]:
    model = get_model()
    embeddings = model.encode(
        [resume_text, job_description_text],
        convert_to_tensor=True,
        normalize_embeddings=True,
    )
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()  # диапазон [-1, 1]

    # Переводим косинусное сходство в 0-100. Для базовой (не дообученной)
    # модели реальные значения обычно лежат в узком диапазоне 0.2-0.8,
    # поэтому растягиваем его — после дообучения на размеченных данных
    # эту калибровку стоит пересчитать по валидационной выборке.
    score = round(max(0.0, min(1.0, (similarity - 0.2) / 0.6)) * 100)

    if score >= 75:
        label = "Good Fit"
    elif score >= 45:
        label = "Potential Fit"
    else:
        label = "No Fit"

    return score, label
