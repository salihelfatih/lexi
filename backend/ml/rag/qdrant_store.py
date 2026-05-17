"""Qdrant-backed vector store adapter."""

from __future__ import annotations

from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from backend.ml.rag.vector_store import VectorStore


_DISTANCE_MAP = {
    "cosine": Distance.COSINE,
    "dot": Distance.DOT,
    "euclid": Distance.EUCLID,
    "manhattan": Distance.MANHATTAN,
}


class QdrantVectorStore(VectorStore):
    """Vector store implementation backed by Qdrant."""

    def __init__(
        self,
        *,
        url: str,
        collection_name: str,
        vector_size: int,
        api_key: str | None = None,
        distance: str = "cosine",
    ) -> None:
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance.lower()
        self.client = QdrantClient(url=url, api_key=api_key or None)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=_DISTANCE_MAP.get(self.distance, Distance.COSINE),
            ),
        )

    def upsert(self, items: list[dict]) -> None:
        points: list[PointStruct] = []
        for item in items:
            embedding = item.get("embedding")
            if embedding is None:
                raise ValueError("Each item must include an 'embedding' field")

            payload = dict(item.get("payload") or {})
            if "text" in item and "text" not in payload:
                payload["text"] = item["text"]
            if "chunk_id" in item and "chunk_id" not in payload:
                payload["chunk_id"] = item["chunk_id"]
            if "document_id" in item and "document_id" not in payload:
                payload["document_id"] = item["document_id"]

            point_id = item.get("id") or str(uuid4())
            points.append(PointStruct(id=point_id, vector=embedding, payload=payload))

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def query(self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None) -> list[dict]:
        query_filter = _build_filter(filters)
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        ).points

        return [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload or {},
            }
            for point in results
        ]


def _build_filter(filters: dict | None) -> Filter | None:
    if not filters:
        return None

    conditions = [
        FieldCondition(key=key, match=MatchValue(value=value))
        for key, value in filters.items()
    ]
    return Filter(must=conditions)
