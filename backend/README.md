# Backend (FastAPI)

## Запуск локально

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Сервер поднимется на `http://127.0.0.1:8000`. Документация API —
на `http://127.0.0.1:8000/docs` (генерируется FastAPI автоматически
из Pydantic-схем).

## Структура

```
app/
  main.py            # точка входа, CORS, подключение роутов
  api/routes.py       # эндпоинт POST /api/analyze
  core/config.py      # настройки из .env
  services/
    parsing.py         # извлечение текста из PDF/DOCX
    embeddings.py       # MiniLM: эмбеддинги + score
    feedback.py         # Phi-3-mini: советы (или мок, см. FEEDBACK_MOCK)
  models/schemas.py    # Pydantic-схемы запроса/ответа
```

## Пока нет дообученной модели

По умолчанию `app/services/embeddings.py` откатывается на базовую
`all-MiniLM-L6-v2`, если в `EMBEDDING_MODEL_PATH` ничего нет — это
позволяет поднять и проверить весь сервер до того, как обучение
в Colab (см. `../ml/README.md`) закончено.

По умолчанию также включён `FEEDBACK_MOCK=true` — Phi-3-mini не
грузится, чтобы не требовать лишней памяти на старте разработки.
Отключите флаг в `.env`, когда дойдёте до этого шага.
