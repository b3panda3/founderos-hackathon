"""FounderOS Configuration — reads from environment variables.

AMD AI Developer Hackathon: FIREWORKS_BASE_URL and ALLOWED_MODELS are
injected by the hackathon platform and read at runtime to ensure
AMD compute usage is tracked.
"""

import os
import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # API Keys
    FIREWORKS_API_KEY: str = ""

    # API Base URL — overridden by hackathon platform injection
    # Falls back to standard Fireworks URL for local dev
    FIREWORKS_BASE_URL: str = "https://api.fireworks.ai/inference/v1"

    # ALLOWED_MODELS — injected by hackathon platform (comma-separated)
    # We read it at runtime and validate model selection against it
    ALLOWED_MODELS: str = ""

    # Dev mode (when True, returns mock responses — ZERO API cost)
    DEV_MODE: bool = True

    # Model IDs on Fireworks — ALL agents use Fireworks AI (AMD GPUs)
    MODEL_STRATEGIST: str = "accounts/fireworks/models/glm-5p2"
    MODEL_RESEARCHER: str = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    MODEL_WRITER: str = "accounts/fireworks/models/mistral-large"
    MODEL_ANALYST: str = "accounts/fireworks/models/qwen2p5-72b-instruct"
    MODEL_CODER: str = "accounts/fireworks/models/deepseek-v4-pro"
    MODEL_COACH: str = "accounts/fireworks/models/gemma-4-26b-a4b-it"  # Gemma 4 on Fireworks (Bonus Challenge)

    # Embedding model
    EMBEDDING_MODEL: str = "nomic-ai/nomic-embed-text-v1.5"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION: str = "founder_knowledge"

    # App settings
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    FRONTEND_DIR: str = "./frontend/out"  # Next.js static export

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # AMD GPU local inference (vLLM on the cloud instance)
    USE_LOCAL_GPU: bool = False
    LOCAL_VLLM_URL: str = "http://localhost:8080/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Log hackathon-injected env vars for transparency
if settings.ALLOWED_MODELS:
    logger.info(f"ALLOWED_MODELS injected: {settings.ALLOWED_MODELS[:100]}...")
if os.environ.get("FIREWORKS_BASE_URL") and os.environ.get("FIREWORKS_BASE_URL") != "https://api.fireworks.ai/inference/v1":
    logger.info(f"FIREWORKS_BASE_URL injected: {settings.FIREWORKS_BASE_URL}")