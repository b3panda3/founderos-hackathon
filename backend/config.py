"""FounderOS Configuration — reads from environment variables and .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEV_MODE: bool = True
    CORS_ORIGINS: list[str] = ["*"]
    FRONTEND_DIR: str = "frontend/out"

    # ── Fireworks AI (AMD GPUs) ─────────────────────────
    FIREWORKS_BASE_URL: str = "https://api.fireworks.ai/inference/v1"
    FIREWORKS_API_KEY: str = ""
    ALLOWED_MODELS: str = ""

    # ── Agent Model IDs (verified on Fireworks) ─────────
    MODEL_STRATEGIST: str = "accounts/fireworks/models/glm-5p2"
    MODEL_RESEARCHER: str = "accounts/fireworks/models/kimi-k2p6"
    MODEL_WRITER: str = "accounts/fireworks/models/gpt-oss-120b"
    MODEL_ANALYST: str = "accounts/fireworks/models/glm-5p1"
    MODEL_CODER: str = "accounts/fireworks/models/deepseek-v4-pro"
    MODEL_COACH: str = "accounts/fireworks/models/kimi-k2p6"

    # ── Local GPU (optional vLLM on AMD) ────────────────
    USE_LOCAL_GPU: bool = False
    LOCAL_VLLM_URL: str = "http://localhost:8080/v1"

    # ── Embeddings ──────────────────────────────────────
    EMBEDDING_MODEL: str = "nomic-ai/nomic-embed-text-v1.5"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()