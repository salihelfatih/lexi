"""Document processing Celery tasks."""

from datetime import datetime
from uuid import UUID

from pytesseract.pytesseract import TesseractNotFoundError

from backend.celery_app import celery_app
from backend.database import SessionLocal
from backend.logging_config import get_logger
from backend.models import Document, DocumentType, JobStatus, JobStatusEnum

logger = get_logger(__name__)


def _processing_error_message(error: Exception) -> str:
    """Return a safe, actionable message for recoverable processing failures."""
    if isinstance(error, FileNotFoundError):
        return "Lexi could not access the uploaded file for processing. Please upload it again."

    if isinstance(error, TesseractNotFoundError):
        return "Lexi's OCR engine is not available. Please try a PDF or DOCX, or restart the backend with OCR support."

    return "An error occurred during processing. Please try again."


@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id_str: str):
    """
    Main document processing task.

    Orchestrates: extraction → classification → parsing → metadata → storage
    """
    document_id = UUID(document_id_str)
    db = SessionLocal()

    try:
        logger.info(f"Starting processing for document {document_id}")

        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        job_status = db.query(JobStatus).filter(JobStatus.document_id == document_id).first()

        # Step 1: Text Extraction
        job_status.status = JobStatusEnum.EXTRACTING_TEXT
        db.commit()

        from backend.core.processing.extraction import ExtractionService

        extraction_service = ExtractionService()
        extraction_result = extraction_service.extract_text(document_id, document.format)

        document.extracted_text = extraction_result.text
        document.extraction_confidence = extraction_result.confidence
        db.commit()

        logger.info(f"Text extracted for document {document_id}")

        # Step 2: Document Classification
        job_status.status = JobStatusEnum.CLASSIFYING
        db.commit()

        from backend.ml.models.classifier import ClassificationService

        classification_service = ClassificationService()
        classification_result = classification_service.classify(extraction_result.text)

        document.document_type = classification_result.document_type
        document.classification_confidence = classification_result.confidence
        db.commit()

        logger.info(f"Document classified as {classification_result.document_type}")

        is_supported_lease = (
            classification_result.document_type.value == DocumentType.ONTARIO_RESIDENTIAL_LEASE.value
        )

        # Step 3: Supported-document enrichment only.
        if is_supported_lease:
            # Best-effort indexing for retrieval; should not block core processing.
            try:
                from backend.services.rag_service import RagService

                rag_service = RagService()
                indexed_count = rag_service.index_document(
                    document_id=document_id,
                    text=extraction_result.text,
                )
                logger.info(f"Indexed {indexed_count} chunks for document {document_id}")
            except Exception as index_error:
                logger.warning(f"RAG indexing skipped for document {document_id}: {str(index_error)}")

            job_status.status = JobStatusEnum.EXTRACTING_CLAUSES
            db.commit()

            from backend.core.processing.clause_parsing import ClauseService

            clause_service = ClauseService()
            clause_service.extract_clauses(db, document_id, extraction_result.text)

            logger.info(f"Clauses extracted for document {document_id}")

            # Step 4: Metadata Extraction
            from backend.core.processing.metadata import MetadataService

            metadata_service = MetadataService()
            metadata_service.extract_metadata(db, document_id, extraction_result.text)

            logger.info(f"Metadata extracted for document {document_id}")

            # Step 5: Grounded Summary
            try:
                from backend.services.summary_service import SummaryService

                summary_service = SummaryService()
                summary_service.generate_summary(db, document_id)
                logger.info(f"Summary generated for document {document_id}")
            except Exception as summary_error:
                logger.warning(
                    f"Summary generation skipped for document {document_id}: {str(summary_error)}"
                )

            # Step 6: RiskSense first-pass signals
            try:
                from backend.services.risk_service import RiskService

                risk_service = RiskService()
                risk_service.generate_risks(db, document_id)
                logger.info(f"RiskSense generated for document {document_id}")
            except Exception as risk_error:
                logger.warning(
                    f"RiskSense generation skipped for document {document_id}: {str(risk_error)}"
                )
        else:
            logger.info(
                "Document %s is unsupported by Lexi; skipping clauses, summary, retrieval, and RiskSense.",
                document_id,
            )

        # Step 7: Storage (if persistent mode)
        if document.storage_mode.value == "persistent":
            from backend.core.storage.s3_storage import StorageService

            storage_service = StorageService()
            storage_service.store_document_persistent(db, document_id)

            logger.info(f"Document stored persistently: {document_id}")

        # Mark as complete
        job_status.status = JobStatusEnum.COMPLETE
        job_status.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Processing complete for document {document_id}")

    except Exception as e:
        logger.error(f"Processing failed for document {document_id}: {str(e)}")

        job_status = db.query(JobStatus).filter(JobStatus.document_id == document_id).first()
        if job_status:
            job_status.status = JobStatusEnum.FAILED
            job_status.error_message = _processing_error_message(e)
            job_status.completed_at = datetime.utcnow()
            db.commit()

        raise

    finally:
        db.close()
