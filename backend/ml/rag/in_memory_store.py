"""Deterministic in-memory vector store for local gates and tests."""

from __future__ import annotations

import math
from threading import Lock

from backend.ml.rag.vector_store import VectorStore


class InMemoryVectorStore(VectorStore):
    """Small process-local vector store used when networked retrieval is not needed."""

    def __init__(self) -> None:
        self._items: dict[str, dict] = {}
        self._lock = Lock()

    def upsert(self, items: list[dict]) -> None:
        """Persist chunk embeddings and metadata in memory."""
        with self._lock:
            for item in items:
                self._items[str(item["id"])] = item

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[dict]:
        """Return top-k cosine-similar chunks, honoring exact-match filters."""
        if not query_embedding:
            return []

        filters = filters or {}
        with self._lock:
            candidates = list(self._items.values())

        scored = []
        for item in candidates:
            if any(str(item.get(key)) != str(value) for key, value in filters.items()):
                payload = item.get("payload") or {}
                if any(str(payload.get(key)) != str(value) for key, value in filters.items()):
                    continue

            score = _cosine_similarity(query_embedding, item.get("embedding") or [])
            if score <= 0:
                continue

            scored.append(
                {
                    "id": item.get("id"),
                    "score": score,
                    "payload": item.get("payload") or {},
                }
            )

        return sorted(scored, key=lambda match: match["score"], reverse=True)[:top_k]


_STORE = InMemoryVectorStore()


def get_in_memory_vector_store() -> InMemoryVectorStore:
    """Return the shared in-memory store for this Python process."""
    return _STORE


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0

    size = min(len(left), len(right))
    dot = sum(left[index] * right[index] for index in range(size))
    left_norm = math.sqrt(sum(value * value for value in left[:size]))
    right_norm = math.sqrt(sum(value * value for value in right[:size]))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)
