"""
Настройки приложения.

Используем pydantic-settings, чтобы все параметры читались из переменных
окружения (.env) и были видны в одном месте с подсказками типов —
вместо россыпи os.environ.get(...) по всему коду.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    embedding_model_path: str = "./ml/model"
    feedback_model_name: str = "microsoft/Phi-3-mini-4k-instruct"
    allowed_origins: str = "http://localhost:5500"
    feedback_mock: bool = True

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    # lru_cache гарантирует, что .env читается один раз, а не на каждый запрос
    return Settings()
