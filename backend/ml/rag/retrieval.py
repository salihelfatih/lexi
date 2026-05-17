"""Retrieval pipeline for document-scoped Q&A."""

from typing import Any

from backend.ml.rag.vector_store import VectorStore


def retrieve_relevant_clauses(
    vector_store: VectorStore,
    query_embedding: list[float],
    top_k: int = 5,
    filters: dict | None = None,
) -> list[dict[str, Any]]:
    """Retrieve relevant document chunks from vector store."""
    return vector_store.query(query_embedding=query_embedding, top_k=top_k, filters=filters)
