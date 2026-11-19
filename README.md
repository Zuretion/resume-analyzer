# Resume Analyzer

Оценивает соответствие резюме вакансии и даёт советы по улучшению.
Учебный проект: дообучение модели на Hugging Face + свой backend/frontend.

- `backend/` — FastAPI, эмбеддинги (MiniLM), фидбек (Phi-3-mini)
- `frontend/` — HTML/CSS(Tailwind)/JS
- `ml/` — скрипт для дообучения в Google Colab

Полный план — в роадмапе (ссылка в чате). Для быстрого старта см.
`backend/README.md` и `frontend/README.md` — оба сервиса запускаются
независимо и общаются через `http://127.0.0.1:8000/api/analyze`.

## Быстрый старт (без дообученной модели)

1. `cd backend && pip install -r requirements.txt && cp .env.example .env && uvicorn app.main:app --reload`
2. `cd frontend && python -m http.server 5500`
3. Откройте `http://127.0.0.1:5500` — форма работает уже на базовой
   (не дообученной) MiniLM-модели и моковом фидбеке.
