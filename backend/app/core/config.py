from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    PROJECT_NAME: str = "DataInsight AI"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/datainsight"
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI-compatible API (DeepSeek: https://api.deepseek.com)
    LLM_API_BASE: str = "https://api.deepseek.com"
    # 任选其一设置环境变量即可：LLM_API_KEY / DEEPSEEK_API_KEY / OPENAI_API_KEY
    LLM_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"),
    )
    LLM_MODEL: str = "deepseek-v4-pro"

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 10
    MAX_DATASET_PARSE_ROWS: int = 200_000
    PREVIEW_MAX_ROWS: int = 50


settings = Settings()
