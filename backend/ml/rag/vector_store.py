"""Vector store abstraction and adapter factory for RAG retrieval."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.config import get_settings


class VectorStore(ABC):
    """Interface for embedding persistence and similarity search."""

    @abstractmethod
    def upsert(self, items: list[dict]) -> None:
        """Persist chunk embeddings and metadata."""

    @abstractmethod
    def query(
        self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None
    ) -> list[dict]:
        """Return top-k relevant chunks by similarity."""


def get_vector_store() -> VectorStore:
    """Build vector store adapter from runtime configuration."""
    settings = get_settings()

    backend = settings.rag_vector_backend.lower()
    if backend == "qdrant":
        from backend.ml.rag.qdrant_store import QdrantVectorStore

        return QdrantVectorStore(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            collection_name=settings.qdrant_collection_name,
            vector_size=settings.qdrant_vector_size,
            distance=settings.qdrant_distance,
        )

    if backend in {"in_memory", "memory", "test"}:
        from backend.ml.rag.in_memory_store import get_in_memory_vector_store

        return get_in_memory_vector_store()

    raise ValueError(f"Unsupported vector backend: {settings.rag_vector_backend}")
