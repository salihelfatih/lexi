"""Embedding utilities for RAG indexing and retrieval."""

from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache

import torch
from transformers import AutoModel, AutoTokenizer

from backend.config import get_settings


class DeterministicEmbedder:
    """Network-free bag-of-words embedder for tests and local product gates."""

    def __init__(self, target_size: int) -> None:
        self.model_name = "deterministic-hashed-bow"
        self.target_size = target_size

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate one stable vector per text."""
        return [self.embed_text(text) for text in texts]

    def embed_text(self, text: str) -> list[float]:
        """Generate a stable token-hash vector."""
        vector = [0.0] * self.target_size
        for token in re.findall(r"[a-z0-9$]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.target_size
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if not norm:
            return vector
        return [value / norm for value in vector]


class TransformerEmbedder:
    """Lightweight transformer embedder with mean pooling."""

    def __init__(self, model_name: str, target_size: int) -> None:
        self.model_name = model_name
        self.target_size = target_size
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate one embedding per input text."""
        if not texts:
            return []

        with torch.no_grad():
            encoded = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            outputs = self.model(**encoded)
            token_embeddings = outputs.last_hidden_state
            attention_mask = (
                encoded["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
            )
            summed = torch.sum(token_embeddings * attention_mask, dim=1)
            counts = torch.clamp(attention_mask.sum(dim=1), min=1e-9)
            pooled = summed / counts

        vectors = pooled.tolist()
        return [self._fit_dimension(vector) for vector in vectors]

    def embed_text(self, text: str) -> list[float]:
        """Generate a single embedding vector."""
        vectors = self.embed_texts([text])
        return vectors[0] if vectors else []

    def _fit_dimension(self, vector: list[float]) -> list[float]:
        """Resize vectors to configured store dimension for compatibility."""
        if len(vector) == self.target_size:
            return vector
        if len(vector) > self.target_size:
            return vector[: self.target_size]
        return vector + [0.0] * (self.target_size - len(vector))


@lru_cache(maxsize=1)
def get_embedder():
    """Get cached embedder instance."""
    settings = get_settings()
    if settings.rag_embedding_backend.lower() in {"deterministic", "fake", "test"}:
        return DeterministicEmbedder(target_size=settings.qdrant_vector_size)

    return TransformerEmbedder(
        model_name=settings.hf_model_name,
        target_size=settings.qdrant_vector_size,
    )
