"""Grounded document summary service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.logging_config import get_logger
from backend.ml.llm.providers import SummaryCompletion, get_llm_provider
from backend.models import Clause, Document, DocumentSummary, DocumentType

logger = get_logger(__name__)

LOW_CONFIDENCE_PROVIDER = "lexi"
LOW_CONFIDENCE_MODEL = "low-confidence-summary-fallback-v1"


class SummaryService:
    """Generate and persist grounded summary artifacts for processed documents."""

    def generate_summary(self, db: Session, document_id: UUID) -> DocumentSummary:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        if not document.extracted_text:
            raise ValueError(f"Document {document_id} has no extracted text")
        if document.document_type != DocumentType.ONTARIO_RESIDENTIAL_LEASE:
            raise ValueError(
                "This document type is unsupported by Lexi, so a legal-style summary was not generated."
            )

        context, grounded_in, source_count = self._build_grounded_context(db, document)
        settings = get_settings()
        context = context[: settings.llm_summary_max_context_chars]
        document_type = document.document_type.value if document.document_type else "unknown"

        if self._has_low_extraction_confidence(document, settings):
            grounded_in = "low_confidence_extracted_text"
            source_count = 1 if context else 0
            completion = self._low_confidence_completion(document_type)
        else:
            provider = get_llm_provider(settings)
            completion = provider.summarize(
                context=context,
                document_type=document_type,
            )

        summary = (
            db.query(DocumentSummary).filter(DocumentSummary.document_id == document_id).first()
        )
        if summary:
            summary.summary_text = completion.text
            summary.provider = completion.provider
            summary.model = completion.model
            summary.grounded_in = grounded_in
            summary.source_count = source_count
        else:
            summary = DocumentSummary(
                document_id=document_id,
                summary_text=completion.text,
                provider=completion.provider,
                model=completion.model,
                grounded_in=grounded_in,
                source_count=source_count,
            )
            db.add(summary)

        db.commit()
        db.refresh(summary)
        logger.info(f"Generated summary for document {document_id}")
        return summary

    def _has_low_extraction_confidence(self, document: Document, settings) -> bool:
        if document.extraction_confidence is None:
            return False
        return document.extraction_confidence < settings.llm_summary_min_extraction_confidence

    def _low_confidence_completion(self, document_type: str) -> SummaryCompletion:
        doc_label = document_type.replace("_", " ") if document_type else "processed document"
        return SummaryCompletion(
            text=(
                f"Lexi extracted this {doc_label} with low confidence, so this is a "
                "limited summary. Details that are unclear or missing in the extracted "
                "text are not summarized as facts."
            ),
            provider=LOW_CONFIDENCE_PROVIDER,
            model=LOW_CONFIDENCE_MODEL,
        )

    def _build_grounded_context(self, db: Session, document: Document) -> tuple[str, str, int]:
        clauses = (
            db.query(Clause)
            .filter(Clause.document_id == document.id)
            .order_by(Clause.order_index)
            .all()
        )
        if clauses:
            return "\n\n".join(clause.clause_text for clause in clauses), "clauses", len(clauses)

        return document.extracted_text or "", "extracted_text", 1
