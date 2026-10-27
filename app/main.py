from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Resume Analyzer API")

# Без этого браузер будет блокировать запросы с другого origin (frontend
# на :5500 или на отдельном домене после деплоя) — см. этап 4 роадмапа.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Запуск для разработки: uvicorn app.main:app --reload
