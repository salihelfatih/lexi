"""Configuration management for Lexi."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = Field(default="postgresql://lexi:lexi@localhost:5432/lexi")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # S3 Storage
    s3_endpoint_url: str = Field(default="http://localhost:9000")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")
    s3_bucket_name: str = Field(default="lexi-documents")
    s3_region: str = Field(default="us-east-1")

    # Encryption
    master_encryption_key: str = Field(default="")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")

    # API
    api_v1_prefix: str = Field(default="/api/v1")
    cors_origins: List[str] = Field(default=["http://localhost:3000"])

    # Processing
    max_file_size_mb: int = Field(default=50)
    ephemeral_ttl_minutes: int = Field(default=5)
    text_extraction_timeout_seconds: int = Field(default=120)
    ocr_timeout_seconds: int = Field(default=300)
    classification_timeout_seconds: int = Field(default=30)
    clause_extraction_timeout_seconds: int = Field(default=60)
    upload_temp_dir: str = Field(default="")

    # ML Models
    hf_model_name: str = Field(default="distilbert-base-uncased")
    spacy_model_name: str = Field(default="en_core_web_sm")

    # RAG Vector Backend
    rag_vector_backend: str = Field(default="qdrant")
    rag_embedding_backend: str = Field(default="transformer")
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_api_key: str = Field(default="")
    qdrant_collection_name: str = Field(default="lexi_documents")
    qdrant_vector_size: int = Field(default=384)
    qdrant_distance: str = Field(default="cosine")

    # LLM summaries
    llm_provider: str = Field(default="fake")
    llm_model_name: str = Field(default="fake-grounded-summary-v1")
    llm_base_url: str = Field(default="")
    llm_request_timeout_seconds: int = Field(default=30)
    llm_summary_max_context_chars: int = Field(default=8000)
    llm_summary_min_extraction_confidence: float = Field(default=50.0)

    # Logging
    log_level: str = Field(default="INFO")

    # Authentication
    auth_provider: str = Field(default="custom")
    jwt_secret_key: str = Field(default="change-this-secret-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    supabase_url: str = Field(default="")
    supabase_publishable_key: str = Field(default="")
    supabase_jwks_url: str = Field(default="")
    supabase_jwt_audience: str = Field(default="authenticated")
    supabase_jwks_cache_seconds: int = Field(default=600)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
