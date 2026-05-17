"""RAG orchestration service for indexing and document-scoped Q&A."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from backend.models import Document, DocumentType
from backend.schemas import RagAnswerResponse, RagChunkMatch, RagCitation


class QuestionUnavailableError(ValueError):
    """Raised when a document exists but Q&A is not safe or ready."""


class RagService:
    """Orchestrates embedding, indexing, retrieval, and response shaping."""

    def __init__(self) -> None:
        self._embedder = None
        self._vector_store = None

    @property
    def embedder(self):
        """Load the transformer embedder only when RAG is actually used."""
        if self._embedder is None:
            from backend.ml.rag.embeddings import get_embedder

            self._embedder = get_embedder()
        return self._embedder

    @property
    def vector_store(self):
        """Connect to the vector store only when indexing or retrieval is requested."""
        if self._vector_store is None:
            from backend.ml.rag.vector_store import get_vector_store

            self._vector_store = get_vector_store()
        return self._vector_store

    def index_document(self, document_id: UUID, text: str) -> int:
        """Chunk and index a processed document into the vector store."""
        from backend.ml.rag.chunking import chunk_document

        chunks = chunk_document(text)
        if not chunks:
            return 0

        embeddings = self.embedder.embed_texts([chunk["text"] for chunk in chunks])
        items = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = str(chunk["chunk_id"])
            items.append(
                {
                    "id": f"{document_id}:{chunk_id}",
                    "embedding": embedding,
                    "document_id": str(document_id),
                    "chunk_id": chunk_id,
                    "text": chunk["text"],
                    "payload": {
                        "document_id": str(document_id),
                        "chunk_id": chunk_id,
                        "text": chunk["text"],
                    },
                }
            )

        self.vector_store.upsert(items)
        return len(items)

    def ask_document(
        self,
        db: Session,
        document_id: UUID,
        user_id: str,
        question: str,
        user_context: str | None = None,
        top_k: int = 5,
    ) -> RagAnswerResponse:
        """Retrieve relevant chunks and build a grounded answer payload."""
        from backend.ml.llm.qa import answer_document_question
        from backend.ml.rag.retrieval import retrieve_relevant_clauses

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
                Document.deleted_at.is_(None),
            )
            .first()
        )
        if not document:
            raise ValueError("Document not found or access denied")
        if not document.extracted_text or not document.document_type:
            raise QuestionUnavailableError("Document has not finished processing yet.")
        if document.document_type != DocumentType.ONTARIO_RESIDENTIAL_LEASE:
            raise QuestionUnavailableError(
                "Lexi could not identify this as a supported document type yet. "
                "This file is unsupported by Lexi right now, so document Q&A is unavailable."
            )

        query_embedding = self.embedder.embed_text(question)
        matches = retrieve_relevant_clauses(
            vector_store=self.vector_store,
            query_embedding=query_embedding,
            top_k=top_k,
            filters={"document_id": str(document_id)},
        )

        if not matches:
            # Lazy index as fallback to avoid hard failure if background indexing was missed.
            self.index_document(document_id=document_id, text=document.extracted_text)
            matches = retrieve_relevant_clauses(
                vector_store=self.vector_store,
                query_embedding=query_embedding,
                top_k=top_k,
                filters={"document_id": str(document_id)},
            )

        retrieved_chunks = []
        answer_chunks = []
        for match in matches:
            payload = match.get("payload") or {}
            text = str(payload.get("text", ""))
            score = float(match.get("score", 0.0))
            retrieved_chunks.append(
                RagChunkMatch(
                    chunk_id=str(payload.get("chunk_id", "")),
                    text=text,
                    score=score,
                )
            )
            answer_chunks.append(
                {
                    "chunk_id": str(payload.get("chunk_id", "")),
                    "text": text,
                    "score": score,
                }
            )

        context = "\n\n".join(chunk.text for chunk in retrieved_chunks if chunk.text)
        answer_payload = answer_document_question(
            question=question,
            context=context,
            chunks=answer_chunks,
            user_context=user_context,
        )

        return RagAnswerResponse(
            document_id=document_id,
            question=question,
            top_k=top_k,
            answer=str(answer_payload["answer"]),
            is_answered=bool(answer_payload["is_answered"]),
            citations=[RagCitation(**citation) for citation in answer_payload["citations"]],
            user_context_note=answer_payload.get("user_context_note"),
            retrieved_chunks=retrieved_chunks,
            context=context,
            answer_payload=answer_payload,
        )
