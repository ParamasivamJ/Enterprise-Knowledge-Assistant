"""
Configuration — single source of truth for all settings.
Uses pydantic-settings to load from .env file with validation.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── GitHub Models LLM ──
    github_token: str = ""
    llm_model: str = "meta-llama-3.1-8b-instruct"

    # ── Database ──
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/knowledge_assistant"

    # ── Qdrant ──
    qdrant_url: str | None = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    qdrant_collection: str = "documents"

    # ── Embeddings ──
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # MiniLM outputs 384-dim vectors

    # ── Chunking ──
    chunk_size: int = 500        # characters per chunk
    chunk_overlap: int = 50      # overlap between chunks (10%)

    # ── Upload ──
    upload_dir: str = "uploads"
    max_file_size_mb: int = 50

    # ── RAG ──
    retrieval_top_k: int = 5     # chunks to retrieve
    confidence_threshold: float = 0.3  # below this = "not enough evidence"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — reads .env once."""
    return Settings()
